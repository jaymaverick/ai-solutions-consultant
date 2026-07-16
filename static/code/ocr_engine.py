import cv2
import easyocr
from pydantic import BaseModel, Field
from typing import List, Dict, Tuple

# ==========================================
# 1. DATA SCHEMAS (Ensuring Rigid Contracts)
# ==========================================

class UIElement(BaseModel):
    """Represents a single extracted text element with its spatial truth."""
    id: int = Field(..., description="Unique integer ID assigned for LLM referencing")
    text: str = Field(..., description="The raw string extracted by EasyOCR")
    center_x: int = Field(..., description="Absolute center pixel X coordinate")
    center_y: int = Field(..., description="Absolute center pixel Y coordinate")

class OCRExtractionPayload(BaseModel):
    """The complete payload package containing coordinate maps and LLM inputs."""
    coordinate_map: Dict[int, Tuple[int, int]] = Field(..., description="Internal lookup: {id: (X, Y)}")
    flattened_text_list: List[str] = Field(..., description="The clean string list sent to Ministral")


# ==========================================
# 2. CORE OCR PROCESSING ENGINE
# ==========================================

class LocalOCREngine:
    def __init__(self, languages: List[str] = ['en']):
        """
        Initializes EasyOCR. 
        Loads models into memory once; do not re-instantiate in the execution loop.
        """
        print("[OCR ENGINE] Initializing EasyOCR models...")
        self.reader = easyocr.Reader(languages, gpu=True) # Automatically falls back to CPU if CUDA is unavailable
        print("[OCR ENGINE] EasyOCR Ready.")

    def process_frame(self, frame_source) -> OCRExtractionPayload:
        if isinstance(frame_source, str):
            image = cv2.imread(frame_source)
            if image is None:
                raise FileNotFoundError(f"Could not find mock screenshot: {frame_source}")
        else:
            image = frame_source

        raw_results = self.reader.readtext(image, detail=1)
        
        coordinate_map: Dict[int, Tuple[int, int]] = {}
        flattened_text_list: List[str] = []
        
        for idx, (bbox, text, confidence) in enumerate(raw_results):
            clean_text = text.strip()
            if not clean_text:
                continue
                
            top_left = bbox[0]
            bottom_right = bbox[2]
            
            center_x = int((top_left[0] + bottom_right[0]) / 2)
            center_y = int((top_left[1] + bottom_right[1]) / 2)
            
            coordinate_map[idx] = (center_x, center_y)
            
            # --- GEOMETRIC CONTEXT INJECTION ---
            # Your fourth row sits near the top of the window canvas. 
            # In a standard 1080p environment, rows 1-4 usually occupy the top 0px to 180px space.
            # Let's flag any element in this vertical slice to guide Ministral instantly.
            if center_y < 180:
                zone_prefix = "[LOCATION: APPLICATION HEADER REGION]"
            else:
                zone_prefix = "[LOCATION: MAIN DATA GRID]"
            # -----------------------------------
            
            flattened_text_list.append(f"[ID: {idx}] {zone_prefix} {clean_text}")
            
        return OCRExtractionPayload(
            coordinate_map=coordinate_map,
            flattened_text_list=flattened_text_list
        )

# ==========================================
# 3. LOCAL SANDBOX TEST PIPELINE
# ==========================================
if __name__ == "__main__":
    # Quick verification script using a mock file
    # Replace 'mock_parts_page.png' with an actual screenshot of your parts app
    engine = LocalOCREngine()
    
    try:
        # Simulate processing a static screenshot
        payload = engine.process_frame("mock_parts_page.png")
        
        print("\n--- DATA SHIPPED TO MINISTRAL LLM ---")
        for line in payload.flattened_text_list[:10]: # Print first 10 items for verification
            print(line)
            
        print("\n--- INTERNAL PYTHON COORDINATE MAP (JETKVM TARGETS) ---")
        for item_id, coords in list(payload.coordinate_map.items())[:5]:
            print(f"ID {item_id} -> Coordinates: X={coords[0]}, Y={coords[1]}")
            
    except FileNotFoundError as e:
        print(f"\n[Sandbox Info] Engine works! To run fully, drop a screenshot named 'mock_parts_page.png' into this directory: {e}")
