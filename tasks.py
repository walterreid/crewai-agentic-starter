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

def scale_to_emotional_scope(scale):
    if scale in ["solo", "small"]:
        return "intimacy, daily routine, personalization, local context, grounded visuals"
    elif scale == "midsize":
        return "professionalism, community trust, mild polish, neighborhood or regional context"
    elif scale == "large":
        return "cinematic impact, bold visuals, national reach, stylized treatments"
    else:
        return "grounded, human-scale, relatable"

def get_tasks(agent_lookup, test_mode=False, brand_slug='unknown_brand'):
    # Load the brand data robustly
    try:
        with open("input/brand.json") as f:
            brand_data = json.load(f)
    except Exception as e:
        print(f"[TASKS] ERROR: Could not load input/brand.json: {e}")
        brand_data = {}

    # Determine business scale (default to small if not specified)
    brand_scale = brand_data.get("scale", "small")

    brand_summary = (
        f"Brand Name: {safe_get(brand_data, 'name')}\n"
        f"Launch Year: {safe_get(brand_data, 'launch_year')}\n"
        f"Origin: {safe_get(brand_data, 'origin')}\n"
        f"Key Traits: {', '.join(brand_data.get('key_traits', []))}\n"
        f"Slogans: {', '.join(brand_data.get('slogans', []))}\n"
        f"Notes: {safe_get(brand_data, 'notes')}\n"
        f"URLs: {', '.join(brand_data.get('urls', []))}\n"
        f"Scale: {brand_scale}\n"
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

    tasks = [
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
                f"When using the WebSearchTool (SerperDevTool), ALWAYS pass a plain string as the search_query argument. NEVER pass a dictionary, list, or any other structure. For example, use 'Dr. Carly Tocco, Psychologist, PhD' or 'therapy office calming decor' as your search_query.\n"
                f"Before submitting a search, analyze the brand data and refine your search terms for maximum relevance. Use the brand name, key traits, or specific visual queries that will yield the best results.\n"
                f"If your first search fails, retry with just the brand name as a plain string.\n"
                f"Be discerning: prioritize quality and relevance of search terms over quantity.\n"
                f"Use this as your primary brand reference. If any brand data is missing or unclear, note it in your analysis and proceed with best effort.\n"
                f"When using the Delegate work to coworker tool, always provide the 'task' and 'context' as plain strings, not as objects or dictionaries.\n"
                f"Example: {{\"coworker\": \"Vignette Designer\", \"task\": \"Create 3 visual themes...\", \"context\": \"The brand is Pizza Post...\"}}"
                + (
                    f"\nTEST MODE: In addition to your normal output, use the FileWriterTool to write a summary of your findings (including tone, style, key traits, and a list of downloaded images) to '{test_output_path}'. Also, if you write a file named 'themes_for_{brand_slug}.txt', always specify the directory as 'output/{brand_slug}' so it is saved in the correct brand output folder. If the FileWriterTool fails to write a file, log an error and continue."
                    if test_mode else ""
                )
            ),
            expected_output="A brand summary with tone, positioning, style cues, and a collection of relevant images for mood board creation.",
            agent=agent_lookup["Brand Analyst"]
        ),
        Task(
            description=(
                "Take the brand analysis and propose 3 core visual/experiential themes. If any upstream data is missing, proceed with best effort and note any assumptions. "
                "When using the Delegate work to coworker tool, always provide the 'task' and 'context' as plain strings, not as objects or dictionaries.\n"
                f"Business scale: {brand_scale}. For this scale, prioritize outcomes that feel: {scale_to_emotional_scope(brand_scale)}.\n"
                "If the business is solo or small, prioritize outcomes that feel local, grounded, and emotionally specific.\n"
                "If the business is mid or large, explore more stylized or cinematic framings that reflect scale.\n"
                + (
                    f"\nTEST MODE: In addition to your normal output, use the FileWriterTool to write a summary of your findings (including the 3 themes and any assumptions) to '{creative_synthesizer_test_output_path}'."
                    if test_mode else ""
                )
            ),
            expected_output="3 concise themes with emotional framing.",
            agent=agent_lookup["Business Creative Synthesizer"]
        )
    ]

    # Route to SmallBusiness Localizer if small business
    if brand_scale == "small":
        tasks.append(
            Task(
                description=(
                    "You are the SmallBusiness Localizer. Translate small business details into grounded creative and visual context using business type, scale, location, and identity markers. Use business-type templates, regional inference, and available images to create environment and character constraints. Redirect abstract or cinematic assumptions into local, human-scale storytelling.\n"
                    f"Business scale: {brand_scale}. For this scale, prioritize outcomes that feel: {scale_to_emotional_scope(brand_scale)}.\n"
                    "If the business is solo or small, avoid owner depictions unless contextually relevant, and focus on indirect cues of scale and trust.\n"
                    "Relevant to all small businesses: Do NOT use the owner or brand name as a character unless contextually required. Use generic terms like 'therapist,' 'staff,' or 'client.'\n"
                    + (
                        f"\nTEST MODE: In addition to your normal output, use the FileWriterTool to write a summary of your findings to 'output/{{brand_slug}}/smallbusiness_localizer_test_output.txt'. Your output MUST include the relevant 'scene_constraints' (both 'avoid' and 'include') from small_business_localizer.json for this business type, and a note that these constraints should be passed to downstream agents to guide their creative decisions. If the FileWriterTool fails to write a file, log an error and continue."
                        if test_mode else ""
                    )
                ),
                expected_output="A grounded, local, and business-specific creative context for the brand, including explicit scene constraints for downstream agents.",
                agent=agent_lookup["SmallBusiness Localizer"]
            )
        )

    tasks.extend([
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
                "You are the Prompt Architect. For each vignette you receive, create 3-4 formatted JSON prompts suitable for video generation like Veo3. You may select the model based on the vignette's style, realism needs, or cinematic ambition — or inherit it from upstream input.\n"
                "IMPORTANT: You must use both the final visual summary and the mood board. If there is a conflict, prioritize the final visual summary, as it is the authoritative source for the game's tone, style, and features.\n"
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
                "IMPORTANT: Use the FileWriterTool to save your final JSON output to 'output/{brand_slug}/ad_prompts.json'. Do not just return the JSON in your response - actually write it to the file using the tool.\n"
                "After writing, confirm that the file exists in the correct directory. If the file is not found, log an error and output the JSON to the log for debugging.\n"
                "You may include reasoning per vignette inline as a 'reasoning' field or as _comment blocks. If any required information is missing, proceed with best effort and document any assumptions. When using the Delegate work to coworker tool, always provide the 'task' and 'context' as plain strings, not as objects or dictionaries.\n"
                "TEST MODE: In addition to your normal output, use the FileWriterTool to write a summary of your findings (including the JSON prompt(s) and any assumptions) to 'output/{brand_slug}/prompt_architect_test_output.txt'. If the FileWriterTool fails to write a file, log an error and continue."
            ),
            expected_output=f"A JSON file saved to output/{brand_slug}/ad_prompts.json containing structured video prompts for each vignette.",
            agent=agent_lookup["Prompt Architect"],
            test_mode=test_mode,
            brand_slug=brand_slug
        )
    ])

    return tasks
