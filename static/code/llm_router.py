from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import json
import re

app = FastAPI(title="JetKVM Local LLM Routing Engine")

class NavigationPayload(BaseModel):
    user_query: str
    flattened_text_list: list
    mode: str

def get_system_prompt(mode: str, query: str) -> str:
    base = "You are a precise routing engine. Return ONLY a valid minified JSON object matching the requested output structure. Do not append regular conversation text.\n\n"
    
    if mode == "MENU_DRILLDOWN":
        return base + f"""Your task is to act as an expert automotive parts advisor navigating a Mercedes Electronic Parts Catalog.
The user is looking for a specific component, described as: "{query}"

Analyze the text elements from the current screen inside the open dropdown menu column.

CRITICAL MECHANICAL DIFFERENTIATION RULES:
1. CHASSIS VS ENGINE SUSPENSION: The user is looking for suspension ride components (springs, dust caps, struts). Do NOT select categories containing "ENGINE SUSPENSION" or "MOTOR MOUNT". Those are structural engine supports. 
2. Look specifically for options that represent wheels, axles, or ride suspension assemblies (e.g., "SPRINGS, SUSPENSION AND HYDRAULIC SYSTEM" or "FRONT AXLE").
3. Return the integer 'id_choice' of the category that physically contains the user's part.

EXPECTED OUTPUT FORMAT:
{{
  "id_choice": 2,
  "reasoning": "Selected the ride suspension system group, avoiding engine structural mounts."
}}
"""
    return base

def mock_ministral_call(system_prompt: str, user_content: str) -> str:
    """Mock classification logic tuned to mirror precise automotive system rules."""
    lines = json.loads(user_content)
    
    # Advanced menu filtering loop: Scan items for clean ride-suspension indicators
    for idx, text in enumerate(lines):
        t_up = text.upper()
        
        # Explicitly skip engine mount rows
        if "ENGINE" in t_up and "SUSPENSION" in t_up:
            continue
            
        # Target the exact ride mechanics groups
        if "SPRING" in t_up or "FRONT AXLE" in t_up or "HYDRAULIC SYSTEM" in t_up:
            return json.dumps({
                "id_choice": idx, 
                "reasoning": f"Target ride suspension structure matched on line entry: '{text}'"
            })
            
    # Secondary loose fallback for structural suspension categories
    for idx, text in enumerate(lines):
        t_up = text.upper()
        if "SUSPENSION" in t_up and "ENGINE" not in t_up:
            return json.dumps({
                "id_choice": idx, 
                "reasoning": f"Chassis suspension fallback matched on line entry: '{text}'"
            })
            
    return json.dumps({"id_choice": -1, "reasoning": "No valid structural category found inside open column bounds."})

@app.post("/v1/navigate")
def route_interface_action(payload: NavigationPayload):
    try:
        system_prompt = get_system_prompt(payload.mode, payload.user_query)
        user_content = json.dumps(payload.flattened_text_list)
        
        raw_response = mock_ministral_call(system_prompt, user_content)
        
        clean_json_str = re.sub(r"```json\s*|```", "", raw_response).strip()
        parsed_response = json.loads(clean_json_str)
        return parsed_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Router Processing Failure: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
