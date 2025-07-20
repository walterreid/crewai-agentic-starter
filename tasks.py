# Task scaffolding for crew agents 

from crewai import Task
import json
import os

def safe_get(d, key, default="UNKNOWN"):
    return d[key] if key in d else default

def health_check_brand_json(path="input/brand.json"):
    if not os.path.exists(path):
        print(f"[HEALTH CHECK] ERROR: {path} does not exist.")
        return False
    try:
        with open(path) as f:
            data = json.load(f)
        # Check for at least one required key
        if "name" not in data:
            print(f"[HEALTH CHECK] WARNING: 'name' key missing in {path}.")
        return True
    except Exception as e:
        print(f"[HEALTH CHECK] ERROR: Could not parse {path}: {e}")
        return False

health_check_brand_json()

def get_tasks(agent_lookup, test_mode=False, brand_slug='unknown_brand'):
    # Load the brand data robustly
    try:
        with open("input/brand.json") as f:
            brand_data = json.load(f)
    except Exception as e:
        print(f"[TASKS] ERROR: Could not load input/brand.json: {e}")
        brand_data = {}
    brand_summary = (
        f"Brand Name: {safe_get(brand_data, 'name')}\n"
        f"Launch Year: {safe_get(brand_data, 'launch_year')}\n"
        f"Origin: {safe_get(brand_data, 'origin')}\n"
        f"Key Traits: {', '.join(brand_data.get('key_traits', []))}\n"
        f"Slogans: {', '.join(brand_data.get('slogans', []))}\n"
        f"Notes: {safe_get(brand_data, 'notes')}\n"
        f"URLs: {', '.join(brand_data.get('urls', []))}\n"
    )

    mood_board_path = f"output/{brand_slug}/mood_board/"
    test_output_path = f"output/{brand_slug}/brand_analyst_test_output.txt"
    creative_synthesizer_test_output_path = f"output/{brand_slug}/creative_synthesizer_test_output.txt"
    vignette_designer_test_output_path = f"output/{brand_slug}/vignette_designer_test_output.txt"
    visual_stylist_test_output_path = f"output/{brand_slug}/visual_stylist_test_output.txt"
    prompt_architect_test_output_path = f"output/{brand_slug}/prompt_architect_test_output.txt"
    ad_prompts_path = f"output/{brand_slug}/ad_prompts.json"

    delegate_tool_note = (
        "When using the Delegate work to coworker tool, always provide the 'task' and 'context' as plain strings, not as objects or dictionaries.\n"
        "Example: {\"coworker\": \"Vignette Designer\", \"task\": \"Create 3 visual themes...\", \"context\": \"The brand is Pizza Post...\"}"
    )

    return [
        Task(
            description=(
                f"Analyze the following brand and perform web search to extract tone, style, and key brand traits.\n"
                f"BRAND DATA:\n{brand_summary}\n"
                f"Additionally, search for and download 5-10 relevant images that represent the brand's visual style, "
                f"including: logo variations, product photos, lifestyle imagery, color palette examples, and brand aesthetic references. "
                f"IMPORTANT: Only download direct image URLs (ending in .jpg, .png, etc.). "
                f"Do NOT use social media URLs (Instagram, Facebook, etc.) as they will not work. "
                f"Save these images to '{mood_board_path}' for use in video production. "
                f"Focus on images that capture the brand's essence, tone, and visual identity.\n"
                f"When using the WebSearchTool, always pass a plain string as the search query, such as the brand name or a relevant search phrase. Do not pass a dictionary or any other structure. For example: 'Dr. Carly Tocco, Psychologist, PhD' or 'Grow a Garden Roblox game screenshots'.\n"
                f"Use this as your primary brand reference. If any brand data is missing or unclear, note it in your analysis and proceed with best effort.\n"
                f"When using the Delegate work to coworker tool, always provide the 'task' and 'context' as plain strings, not as objects or dictionaries.\n"
                f"Example: {{\"coworker\": \"Vignette Designer\", \"task\": \"Create 3 visual themes...\", \"context\": \"The brand is Pizza Post...\"}}"
                + (
                    f"\nTEST MODE: In addition to your normal output, use the FileWriterTool to write a summary of your findings (including tone, style, key traits, and a list of downloaded images) to '{test_output_path}'. Also, if you write a file named 'themes_for_{brand_slug}.txt', always specify the directory as 'output/{brand_slug}' so it is saved in the correct brand output folder."
                    if test_mode else ""
                )
            ),
            expected_output="A brand summary with tone, positioning, style cues, and a collection of relevant images for mood board creation.",
            agent=agent_lookup["Brand Analyst"]
        ),
        Task(
            description=(
                "Take the brand analysis and propose 3 core visual/experiential themes. If any upstream data is missing, proceed with best effort and note any assumptions. "
                "When using the Delegate work to coworker tool, always provide the 'task' and 'context' as plain strings, not as objects or dictionaries."
                + (
                    f"\nTEST MODE: In addition to your normal output, use the FileWriterTool to write a summary of your findings (including the 3 themes and any assumptions) to '{creative_synthesizer_test_output_path}'."
                    if test_mode else ""
                )
            ),
            expected_output="3 concise themes with emotional framing.",
            agent=agent_lookup["Creative Synthesizer"]
        ),
        Task(
            description=(
                "Create 6–8 second vignette ideas based on the visual themes. If any required information is missing, use your best judgment and document any assumptions. "
                "When using the Delegate work to coworker tool, always provide the 'task' and 'context' as plain strings, not as objects or dictionaries."
                + (
                    f"\nTEST MODE: In addition to your normal output, use the FileWriterTool to write a summary of your findings (including the vignette concepts and any assumptions) to '{vignette_designer_test_output_path}'."
                    if test_mode else ""
                )
            ),
            expected_output="Short vignette concepts suitable for video generation.",
            agent=agent_lookup["Vignette Designer"]
        ),
        Task(
            description=(
                "Suggest color palettes, visual tone, and style references for each vignette based on the brand analysis and themes. If any information is missing, proceed with best effort and document any assumptions. When using the Delegate work to coworker tool, always provide the 'task' and 'context' as plain strings, not as objects or dictionaries."
                + (
                    f"\nTEST MODE: In addition to your normal output, use the FileWriterTool to write a summary of your findings (including color palettes, visual tone, style references, and any assumptions) to '{visual_stylist_test_output_path}'."
                    if test_mode else ""
                )
            ),
            expected_output="A short guide to visual tone for use in cinematic vignette creation.",
            agent=agent_lookup["Visual Stylist"]
        ),
        Task(
            description=(
                "You are the Prompt Architect. For each vignette you receive, create 3-4 formatted JSON prompt "
                "suitable for video generation like Veo3. You may select the model based on the "
                "vignette's style, realism needs, or cinematic ambition — or inherit it from upstream input.\n\n"
                "IMPORTANT:You must use both the final visual summary and the mood board. If there is a conflict, "
                "prioritize the final visual summary, as it is the authoritative source for the game's tone, style, and features.\n\n"
                "For each vignette, return a single structured JSON block with the following fields:\n"
                "- model: 'google_veo_v3'\n"
                "- scene: contains title, duration, fps, style, character, environment, and a short script (see structure below)\n"
                "- reasoning (optional): a short note explaining why you chose the model, structure, or cinematic framing\n\n"
                "Output format per vignette:\n"
                "{\n"
                "  \"model\": \"sora\",\n"
                "  \"reasoning\": \"Sora selected for fast-paced surreal motion and mobile-friendly ratio.\",\n"
                "  \"scene\": {\n"
                "    \"title\": \"...\",\n"
                "    \"duration_seconds\": 8,\n"
                "    \"fps\": 30,\n"
                "    \"aspect_ratio\": \"9:16\",\n"
                "    \"style\": { \"render\": \"...\", \"lighting\": \"...\", \"camera_equipment\": \"...\" },\n"
                "    \"character\": { \"name\": \"...\", \"appearance\": \"...\", \"emotional_journey\": \"...\" },\n"
                "    \"environment\": { \"location\": \"...\", \"props\": [\"...\"], \"atmospherics\": \"...\" },\n"
                "    \"script\": [\n"
                "      { \"type\": \"stage_direction\", \"character\": \"...\", \"movement\": \"...\" },\n"
                "      { \"type\": \"dialogue\", \"character\": \"...\", \"line\": \"...\" }\n"
                "    ]\n"
                "  }\n"
                "}\n\n"
                f"IMPORTANT: Use the FileWriterTool to save your final JSON output to '{ad_prompts_path}'. "
                "Do not just return the JSON in your response - actually write it to the file using the tool.\n"
                "You may include reasoning per vignette inline as a 'reasoning' field or as _comment blocks. "
                "If any required information is missing, proceed with best effort and document any assumptions. "
                "When using the Delegate work to coworker tool, always provide the 'task' and 'context' as plain strings, not as objects or dictionaries."
                + (
                    f"\nTEST MODE: In addition to your normal output, use the FileWriterTool to write a summary of your findings (including the JSON prompt(s) and any assumptions) to '{prompt_architect_test_output_path}'."
                    if test_mode else ""
                )
            ),
            expected_output=f"A JSON file saved to {ad_prompts_path} containing structured video prompts for each vignette.",
            agent=agent_lookup["Prompt Architect"]
        )
    ]
