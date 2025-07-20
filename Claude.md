# Project Structure Documentation

This document describes the structure and purpose of each file and folder in the project.

```
my-crew-workspace/
├── crew_setup.py
├── roles.json
├── tasks.py
├── tools/
│   ├── logger.py
│   └── image_downloader.py
├── input/
│   └── brand.json
├── output/
│   ├── crew_log.txt
│   ├── crew_status.txt
│   ├── ad_prompts.json
│   └── mood_board/
```

## File/Folder Descriptions

- **crew_setup.py**  
  Main entry point for running the CrewAI workflow. Defines agents, tasks, tools, and launches the process. Includes robust error handling with `safe_kickoff` to ensure graceful workflow completion and agent notification if a step fails. Uses `TeeLogger` to capture all agent conversations to `output/crew_log.txt`.

- **roles.json**  
  JSON file defining agent roles, goals, backstories, tool access, and delegation permissions for the workflow. Currently supports 5 agents: Brand Analyst, Creative Synthesizer, Vignette Designer, Visual Stylist, and Prompt Architect.

- **tasks.py**  
  Defines all agent tasks with robust error handling and brand data injection. Includes health checks for `input/brand.json` and safe defaults for missing data. Each task includes explicit instructions for tool usage and delegation.

- **tools/logger.py**  
  Custom logging utilities including `TeeLogger` (captures stdout to both console and file) and `CrewLogger` (structured logging). Used to record all agent conversations and workflow events.

- **tools/image_downloader.py**  
  Custom tool for downloading brand-relevant images for mood boards. `MoodBoardImageTool` downloads images from URLs and saves them to `output/mood_board/` for use in video production. **UPDATED**: Now includes URL validation to reject social media URLs and ensure only direct image URLs are downloaded.

- **input/brand.json**  
  JSON file containing structured brand data (name, launch_year, origin, key_traits, slogans, URLs, notes) for use in brand analysis tasks. Automatically injected into agent prompts.

- **output/crew_log.txt**  
  **PRIMARY LOG FILE** - Records all agent conversations, tool usage, thoughts, and workflow execution. Contains the complete interaction history between agents.

- **output/crew_status.txt**  
  Final workflow results summary. Contains the structured output from the Prompt Architect agent in JSON format.

- **output/ad_prompts.json**  
  JSON file containing structured video prompts for AI video generation models (Sora, Runway, Google Veo). Each prompt includes scene details, character descriptions, and script elements.

- **output/mood_board/**  
  Directory containing downloaded brand-relevant images for visual reference and mood board creation. Images are automatically downloaded by the Brand Analyst agent.

## Error Handling & Workflow Robustness

- **safe_kickoff()** wrapper catches errors and ensures graceful workflow completion
- **Health checks** for `input/brand.json` with safe defaults for missing data
- **Max iterations safeguard** (50) prevents runaway loops
- **Agent notification** when steps fail, allowing graceful degradation
- **Robust delegation** with explicit string formatting instructions

## Agent Workflow

1. **Brand Analyst** - Analyzes brand data from `input/brand.json`, performs web search, downloads relevant images to `output/mood_board/`
2. **Creative Synthesizer** - Creates 3 core visual/experiential themes based on brand analysis
3. **Vignette Designer** - Designs 6-8 second cinematic vignettes for each theme
4. **Visual Stylist** - Suggests color palettes, visual tone, and style references
5. **Prompt Architect** - Formats vignettes into structured JSON prompts and saves to `output/ad_prompts.json`

## Tools Used

- **SerperDevTool** - Web search utility (requires serper.dev API key)
- **FileWriterTool** - Writes structured outputs to JSON files
- **MoodBoardImageTool** - Downloads brand-relevant images for mood boards
- **TeeLogger** - Captures all stdout to both console and `output/crew_log.txt`

## File Status

| File | Status | Purpose |
|------|--------|---------|
| `output/crew_log.txt` | ✅ **ACTIVE** | Complete agent conversation log |
| `output/crew_status.txt` | ✅ **ACTIVE** | Final workflow results |
| `output/ad_prompts.json` | ✅ **ACTIVE** | Video prompts (updated to use FileWriterTool) |
| `output/mood_board/` | ✅ **ACTIVE** | Downloaded brand images |

## How to Run

1. Ensure your virtual environment is activated:
   ```bash
   source .venv/bin/activate
   ```

2. Update `input/brand.json` with your brand data

3. Run the workflow:
   ```bash
   python crew_setup.py
   ```

4. Monitor progress:
   ```bash
   tail -f output/crew_log.txt
   ```

5. Check results:
   - `output/ad_prompts.json` - Structured video prompts
   - `output/mood_board/` - Brand images
   - `output/crew_log.txt` - Complete conversation log

## Recent Updates

- ✅ **Image Download Functionality** - Brand Analyst now downloads brand-relevant images
- ✅ **URL Validation** - Image downloader now rejects social media URLs and validates image content
- ✅ **Robust Error Handling** - Safe defaults and health checks for missing data
- ✅ **Fixed File Writing** - Prompt Architect now properly uses FileWriterTool
- ✅ **Complete Logging** - All agent conversations recorded in `output/crew_log.txt`
- ✅ **Mood Board Creation** - Images saved to `output/mood_board/` for visual reference

---

## 🗂️ Output Organization by Brand

- For each run, outputs are stored in a subfolder of `output/` named after the brand (e.g., `output/grow_a_garden/`).
- The brand folder name is generated by slugifying the brand name from `input/brand.json` (e.g., `Dr. Carly Tocco, Psychologist, PhD` → `dr_carly_tocco_psychologist_phd`).
- All logs, JSON files, mood board images, and test outputs for that brand are stored in this folder.
- If the brand name is missing, outputs are stored in `output/unknown_brand/`.
- This structure supports multiple brands and keeps results organized and easy to review.

### Example Structure

```
output/
  grow_a_garden/
    crew_log.txt
    crew_status.txt
    ad_prompts.json
    brand_analyst_test_output.txt
    creative_synthesizer_test_output.txt
    vignette_designer_test_output.txt
    visual_stylist_test_output.txt
    prompt_architect_test_output.txt
    mood_board/
      image1.jpg
      image2.jpg
  dr_carly_tocco_psychologist_phd/
    crew_log.txt
    crew_status.txt
    ad_prompts.json
    brand_analyst_test_output.txt
    creative_synthesizer_test_output.txt
    vignette_designer_test_output.txt
    visual_stylist_test_output.txt
    prompt_architect_test_output.txt
    mood_board/
      image1.jpg
      image2.jpg
```

---

## 🧪 Agent Test Output Pattern

All agents now support a robust test mode for output validation:

- **Test Mode:**  
  Each agent can be run in “test mode,” where it must output a summary of its findings/results to a dedicated file in the brand’s output folder using `FileWriterTool`.
- **File Naming:**  
  Use the pattern `output/{brand_slug}/{agent_role}_test_output.txt` (e.g., `output/grow_a_garden/creative_synthesizer_test_output.txt`).
- **Content:**  
  The file should include:
  - Agent role and task description
  - Key findings or outputs (e.g., for Creative Synthesizer: 3 themes and assumptions)
  - Any assumptions or missing data
- **How to Enable:**  
  Set `TEST_MODE = True` in `crew_setup.py` to pass `test_mode=True` to `get_tasks()` in `tasks.py`.
- **Purpose:**  
  This enables automated and manual validation of agent outputs, and can be extended to all agents for comprehensive testing.

### Example: Agent Test Output Files

When test mode is enabled, each agent will write a summary of its findings to a dedicated file in the brand’s output folder:

- `output/{brand_slug}/brand_analyst_test_output.txt`
- `output/{brand_slug}/creative_synthesizer_test_output.txt`
- `output/{brand_slug}/vignette_designer_test_output.txt`
- `output/{brand_slug}/visual_stylist_test_output.txt`
- `output/{brand_slug}/prompt_architect_test_output.txt`

Each file will contain the agent’s role, task, key outputs, and any assumptions or missing data.

---

## Setup

Before running the workflow, install all required dependencies:

```bash
pip install -r requirements.txt
```

This will install:
- crewai
- crewai_tools (for agent tools and file writing)
- requests (for image downloading)
- python-dotenv (for environment variable loading)

## Python Version and Virtual Environment Setup

This project requires **Python 3.12** or higher for full compatibility with CrewAI and its dependencies.

To set up your environment:

1. **Ensure Python 3.12 is installed:**
   ```bash
   python3.12 --version
   # Should print Python 3.12.x
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the workflow:**
   ```bash
   python3.12 crew_setup.py
   ```

If you have multiple brands, ensure your `input/brand.json` is set for the brand you want to process before running the workflow.
