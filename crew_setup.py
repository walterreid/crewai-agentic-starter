from crewai import Agent, Task, Crew
from crewai_tools import FileWriterTool
from dotenv import load_dotenv
from tools.logger import CrewLogger

from tools.logger import TeeLogger
from datetime import datetime
import os
import sys
import re
import json

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    text = re.sub(r'_+', '_', text)
    return text.strip('_')

# Load brand name for output folder
try:
    with open('input/brand.json') as f:
        brand_data = json.load(f)
        brand_name = brand_data.get('name', 'unknown_brand')
except Exception:
    brand_name = 'unknown_brand'
brand_slug = slugify(brand_name)
output_dir = os.path.join('output', brand_slug)
os.makedirs(output_dir, exist_ok=True)

# Update log path and logger to use brand folder
log_path = os.path.join(output_dir, 'crew_log.txt')
sys.stdout = TeeLogger(log_path)

# Clear the log at the start of each run
with open(log_path, 'w') as f:
    f.write(f"🕓 Run started: {datetime.now()}\n{'='*60}\n")

load_dotenv()

logger = CrewLogger()
# 🔧 Tool Setup
write_tool = FileWriterTool()


def load_roles(json_path):
    with open(json_path) as f:
        roles = json.load(f)
    agents = []
    for role in roles:
        tools = []
        if "WebSearchTool" in role.get("tools", []):
            from crewai_tools import SerperDevTool
            tools.append(SerperDevTool())
        if "FileWriterTool" in role.get("tools", []):
            from crewai_tools import FileWriterTool
            tools.append(FileWriterTool())
        if "MoodBoardImageTool" in role.get("tools", []):
            from tools.image_downloader import MoodBoardImageTool
            tools.append(MoodBoardImageTool())
        agents.append(Agent(
            role=role["role"],
            goal=role["goal"],
            backstory=role["backstory"],
            tools=tools,
            verbose=role.get("verbose", True),
            allow_delegation=role.get("allow_delegation", False)
        ))
    return agents

agents = load_roles('roles.json')
agent_lookup = {agent.role: agent for agent in agents}

from tasks import get_tasks
# To enable agent test mode, set test_mode=True below
TEST_MODE = True  # Set to True to enable agent test output files
tasks = get_tasks(agent_lookup, test_mode=TEST_MODE, brand_slug=brand_slug)

MAX_ITERATIONS = 50  # Set a reasonable upper bound for agent actions/steps

def safe_kickoff(crew):
    try:
        result = crew.kickoff()
        with open(os.path.join(output_dir, "crew_status.txt"), "w") as f:
            f.write(f"SUCCESS\n{str(result)}\n")
        print("\n✅ Workflow completed successfully.")
        return result
    except Exception as e:
        logger.log(f"❌ Error during crew execution: {e}")
        # Notify all agents (if context is supported)
        for agent in crew.agents:
            if hasattr(agent, 'context'):
                agent.context += "\n[ALERT] A previous step failed. Please proceed accordingly."
        with open(os.path.join(output_dir, "crew_status.txt"), "w") as f:
            f.write(f"FAILURE\n{e}\n")
        print(f"\n❌ Workflow failed: {e}")
        return f"Workflow terminated due to error. See logs for details."

# 🚀 Launch!
crew = Crew(agents=agents, tasks=tasks, verbose=True)
result = safe_kickoff(crew)
print(f"\n🧾 Final Output:\n{result}")

# Optional: reset stdout if needed
# sys.stdout = sys.__stdout__
logger.log("\n🧾 Final Output:\n" + str(result))
print("\n🧾 Final Output:\n")
print(result)

