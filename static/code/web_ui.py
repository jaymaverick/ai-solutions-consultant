import time
import requests
import base64
import re
from PIL import Image
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
from playwright.sync_api import sync_playwright
from ocr_engine import LocalOCREngine
from scroll_manager import ScrollStateManager

app = FastAPI(title="JetKVM Automation Dashboard")

# =====================================================================
# CORE CONFIGURATION CONFIG FRAMEWORK
# =====================================================================
DEBUGGING_URL = "http://127.0.0.1:9222"
FASTAPI_ROUTER_URL = "http://127.0.0.1:5000/v1/navigate"
ROW_Y_TOLERANCE = 12  

# Helper functions identical to your production harness setup
def query_router(query: str, text_list: list, mode: str):
    payload = {"user_query": query, "flattened_text_list": text_list, "mode": mode}
    try:
        response = requests.post(FASTAPI_ROUTER_URL, json=payload, timeout=15)
        return response.json()
    except Exception as e:
        print(f"❌ Router Connection Failure: {e}")
        return {"id_choice": -1, "reasoning": "Connection Error Fallback"}

def get_menu_column_bounds(image_path, target_y=130):
    try:
        img = Image.open(image_path).convert('RGB')
        width, _ = img.size
        segments = []
        in_segment = False
        start_x = None
        
        for x in range(width):
            r, g, b = img.getpixel((x, target_y))
            is_white = (r > 230 and g > 230 and b > 230)
            if is_white and not in_segment:
                in_segment = True
                start_x = x
            elif not is_white and in_segment:
                in_segment = False
                segments.append((start_x, x - 1))
        if in_segment:
            segments.append((start_x, width - 1))
            
        valid_segments = [s for s in segments if (s[1] - s[0]) >= 35]
        if valid_segments:
            return valid_segments[0][0], valid_segments[0][1]
    except Exception as e:
        print(f"⚠️ Image analysis failed: {e}")
    return None, None

# =====================================================================
# FRONTEND INTERFACE GENERATION (TAILWIND CSS)
# =====================================================================
@app.get("/", response_class=HTMLResponse)
def render_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JetKVM Catalog Navigator</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-gray-100 font-sans min-h-screen flex items-center justify-center p-6">
        <div class="max-w-xl w-full bg-gray-800 border border-gray-700 rounded-xl shadow-2xl p-8">
            <div class="flex items-center space-x-3 mb-6">
                <span class="text-3xl">🤖</span>
                <h1 class="text-2xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                    Mercedes EPC JetKVM Interface
                </h1>
            </div>
            
            <form action="/run" method="POST" class="space-y-5">
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-1">Vehicle Identification Number (VIN)</label>
                    <input type="text" name="vin" required value="WDB2112201B168546" 
                           class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 focus:outline-none focus:border-blue-500 text-white tracking-widest font-mono uppercase">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-1">Target Part Name</label>
                    <input type="text" name="part_name" required value="front spring"
                           class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 focus:outline-none focus:border-blue-500 text-white">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-1">General Location Area</label>
                    <input type="text" name="part_location" required value="front suspension" 
                           class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 focus:outline-none focus:border-blue-500 text-white">
                </div>
                
                <button type="submit" 
                        class="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold rounded-lg py-3 transition shadow-lg">
                    Execute Part Search
                </button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# =====================================================================
# PIPELINE AUTOMATION ROUTE HANDLER
# =====================================================================
@app.post("/run", response_class=HTMLResponse)
def execute_automation_pipeline(
    vin: str = Form(...), 
    part_name: str = Form(...), 
    part_location: str = Form(...)
):
    # Dynamically structure contexts based on input values
    USER_CONTEXT_QUERY = f"{part_name.strip()}, part of the {part_location.strip()}"
    TARGET_PART_QUERY = part_name.strip().upper()
    CLEAN_VIN = vin.strip().upper()

    print("\n" + "="*50)
    print(f"🚀 INCOMING DISPATCH COMMAND RECEIVED")
    print(f"❖ Target VIN: {CLEAN_VIN}")
    print(f"❖ Context Target: {USER_CONTEXT_QUERY}")
    print("="*50)

    ocr_engine = LocalOCREngine()
    scroll_tracker = ScrollStateManager()
    scraped_inventory = {}  
    mb_part_pattern = re.compile(r'\bA\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}\b|\bA\d{10}\b', re.IGNORECASE)
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(DEBUGGING_URL)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Harness could not find active port 9222 stream session: {e}")
            
        default_context = browser.contexts[0]
        page = default_context.pages[0]
        
        # Enforce strict layout aspect tracking alignment
        page.evaluate("""() => {
            const video = document.querySelector('video');
            if (!video) return;
            video.style.width = video.videoWidth + 'px';
            video.style.height = video.videoHeight + 'px';
            video.style.maxWidth = 'none';
            video.style.minWidth = 'none';
            video.scrollIntoView({block: "start", inline: "start"});
        }""")
        time.sleep(0.5)

        # Retrieve absolute location offsets of stream layout matrix
        video_offsets = page.evaluate("""() => {
            const video = document.querySelector('video');
            const rect = video.getBoundingClientRect();
            return { left: rect.left, top: rect.top };
        }""")

        # -----------------------------------------------------------------
        # 🔑 VIN INJECTION SUB-ROUTINE
        # -----------------------------------------------------------------
        vin_target_x = video_offsets["left"] + 290
        vin_target_y = video_offsets["top"] + 70
        
        print(f"[VIN System] Directing pointer focus to text field input box at calculated coordinate position: X={vin_target_x}, Y={vin_target_y}")
        page.mouse.click(vin_target_x, vin_target_y)
        time.sleep(0.2)
        
        # Clear existing text values defensively if fields cache data rows
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.1)
        
        print(f"[VIN System] Dispatching typing sequence string values: '{CLEAN_VIN}'")
        page.keyboard.type(CLEAN_VIN)
        time.sleep(0.2)
        page.keyboard.press("Enter")
        
        print("[VIN System] Payload committed. Pausing 4 seconds for catalog database search retrieval index adjustments...")
        time.sleep(4.0)

        # -----------------------------------------------------------------
        # 🌿 PHASE 1: DETERMINISTIC GEOMETRIC MENU DRILL-DOWN
        # -----------------------------------------------------------------
        print("\n==================================================")
        print("🌿 ENTERING STAGE 5 & 6: SPATIAL MENU DRILL-DOWN")
        print("==================================================")
        
        drilldown_loop = 1
        while True:
            print(f"\n[Drill-down Loop #{drilldown_loop}] Processing interface snapshot frames...")
            
            base64_image = page.evaluate("""() => {
                const video = document.querySelector('video');
                if (!video || !video.videoWidth) return null;
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                return canvas.toDataURL('image/png').split(',')[1];
            }""")
            
            if not base64_image:
                time.sleep(1)
                continue
                
            SNAPSHOT_FILE = "menu_drilldown_view.png"
            with open(SNAPSHOT_FILE, "wb") as fh:
                fh.write(base64.b64decode(base64_image))
                
            x_start, x_end = get_menu_column_bounds(SNAPSHOT_FILE, target_y=130)
            
            if x_start is None or x_end is None:
                print("🏁 DRILL-DOWN SUCCESSFUL: Dropdown closed on row 130. Transitioning downstream.")
                break
                
            print(f"👁️ Isolated Menu Column Channel Bounds: X = [{x_start} -> {x_end}]")
            payload = ocr_engine.process_frame(SNAPSHOT_FILE)
            
            filtered_text_list = []
            filtered_id_map = {}
            
            for original_id, text_line in enumerate(payload.flattened_text_list):
                if original_id in payload.coordinate_map:
                    raw_x, raw_y = payload.coordinate_map[original_id]
                    if x_start <= raw_x <= x_end and raw_y > 130:
                        new_id = len(filtered_text_list)
                        filtered_text_list.append(text_line)
                        filtered_id_map[new_id] = original_id
            
            if not filtered_text_list:
                print("⚠️ Column isolated bounds have no text arrays available.")
                break
                
            print(f"📊 Filtered Options List: {filtered_text_list}")
            result = query_router(USER_CONTEXT_QUERY, filtered_text_list, mode="MENU_DRILLDOWN")
            chosen_sub_id = result.get("id_choice", -1)
            reasoning = result.get("reasoning")
            
            print(f"✔️ AI Choice: \"{reasoning}\"")
            
            if chosen_sub_id != -1 and chosen_sub_id < len(filtered_text_list):
                true_payload_id = filtered_id_map[chosen_sub_id]
                raw_x, raw_y = payload.coordinate_map[true_payload_id]
                
                click_x = video_offsets["left"] + raw_x
                click_y = video_offsets["top"] + raw_y
                
                print(f"👉 Hardware Action: Clicking target match context row selection at X={click_x}, Y={click_y}")
                page.mouse.click(click_x, click_y)
                time.sleep(2.0)
                drilldown_loop += 1
            else:
                print("⚠️ End cascade pointer tracker alignment sequence limit reached.")
                break

        # -----------------------------------------------------------------
        # ⚖️ PHASE 2: STAGE 7 HORIZONTAL ROW-ALIGNED CORE SCRAPER
        # -----------------------------------------------------------------
        print("\n==================================================")
        print("⚖️ ENTERING STAGE 7: HORIZONTAL ROW-ALIGNED SCRAPER")
        print("==================================================")
        scroll_tracker.reset_history()
        scrape_loop = 1
        
        while True:
            print(f"\n--- SCRAPE LOOP CYCLE #{scrape_loop} ---")
            
            base64_image = page.evaluate("""() => {
                const video = document.querySelector('video');
                if (!video || !video.videoWidth) return null;
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                return canvas.toDataURL('image/png').split(',')[1];
            }""")
            
            if not base64_image:
                time.sleep(1)
                continue
                
            SNAPSHOT_FILE = "live_production_view.png"
            with open(SNAPSHOT_FILE, "wb") as fh:
                fh.write(base64.b64decode(base64_image))
                
            payload = ocr_engine.process_frame(SNAPSHOT_FILE)
            
            detected_part_numbers = []
            for element_id, text_line in enumerate(payload.flattened_text_list):
                match = mb_part_pattern.search(text_line)
                if match:
                    clean_pn = match.group(0).upper().replace(" ", "")
                    _, raw_y = payload.coordinate_map[element_id]
                    detected_part_numbers.append((clean_pn, raw_y))
            
            if detected_part_numbers:
                for part_number, pn_y in detected_part_numbers:
                    for element_id, text_line in enumerate(payload.flattened_text_list):
                        if TARGET_PART_QUERY.upper() in text_line.upper():
                            _, text_y = payload.coordinate_map[element_id]
                            if abs(text_y - pn_y) <= ROW_Y_TOLERANCE:
                                if part_number not in scraped_inventory:
                                    scraped_inventory[part_number] = text_line
                                    print(f"   🎯 MATCH VALIDATED: [PN: {part_number}] belongs directly to -> '{text_line}'")
            
            if scroll_tracker.update_and_check_if_stuck(payload.flattened_text_list):
                print("\n🏁 SCROLL COMPLETED: Hit absolute bottom boundary layer.")
                break
                
            target_scroll_x = video_offsets["left"] + 550
            target_scroll_y = video_offsets["top"] + 200
            page.mouse.move(target_scroll_x, target_scroll_y)
            time.sleep(0.05)
            page.mouse.wheel(0, 150)
            time.sleep(1.2)
            scrape_loop += 1

    # -----------------------------------------------------------------
    # RESULT REPORT RENDER GENERATION
    # -----------------------------------------------------------------
    results_html = f"""
    <div style="font-family: monospace; background: #111827; color: #10B981; padding: 20px; border-radius: 8px; margin-top: 20px;">
        <h3>📊 PIPELINE SCRAPE RESULTS REPORT</h3>
        <p>Target Part Query Filter Match: <b>{TARGET_PART_QUERY}</b></p>
        <p>Total Distinct Inventory Records Compiled: {len(scraped_inventory)}</p>
        <hr style="border-color: #374151; margin: 15px 0;" />
    """
    if scraped_inventory:
        for item_pn, item_name in scraped_inventory.items():
            results_html += f"<p>❖ <b>{item_pn:<15}</b> | {item_name}</p>"
    else:
        results_html += "<p style='color: #EF4444;'>No parts matching your search criteria were uncovered on the records view layout layers.</p>"
        
    results_html += "<br><a href='/' style='color: #3B82F6; text-decoration: underline;'>← Run Another Search</a></div>"
    return HTMLResponse(content=results_html)

if __name__ == "__main__":
    # Start the local UI instance engine dashboard on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
