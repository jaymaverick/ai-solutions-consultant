import hashlib
from typing import List

class ScrollStateManager:
    def __init__(self, history_limit: int = 3):
        """
        Manages the history of screen states to detect if scrolling is changing the UI layout
        or if the application has hit a dead-end (the bottom of the parts catalog view).
        """
        # Keeps track of the last N hashes to prevent rubber-banding or oscillating scroll containers
        self.state_history: List[str] = []
        self.history_limit = history_limit

    def _generate_text_hash(self, flattened_text_list: List[str]) -> str:
        """
        Strips out volatile coordinate indices and generates a clean structural fingerprint 
        of the current text viewport.
        """
        # Strip out the "[ID: X]" prefixes because IDs might dynamically shift 
        # based on minor OCR box detection changes, but the core content strings remain identical.
        normalized_strings = []
        for line in flattened_text_list:
            if "] " in line:
                # Extract everything after the '[ID: XX] '
                normalized_strings.append(line.split("] ", 1)[1])
            else:
                normalized_strings.append(line)
        
        # Combine all strings into a single dense block of bytes
        combined_text = "".join(normalized_strings).encode('utf-8')
        
        # Return a deterministic SHA-256 string fingerprint
        return hashlib.sha256(combined_text).hexdigest()

    def update_and_check_if_stuck(self, flattened_text_list: List[str]) -> bool:
        """
        Appends the current screen text signature to history.
        Returns True if the page is STUCK (no new content changed after a scroll action).
        Returns False if the page is FRESH (the content shifted successfully).
        """
        if not flattened_text_list:
            # If the screen is completely blank, treat it as stuck/error to prevent infinite loops
            return True

        current_hash = self._generate_text_hash(flattened_text_list)
        
        # Check if this exact layout fingerprint has been seen recently
        if current_hash in self.state_history:
            print("[SCROLL MANAGER] ⚠️ Scroll Blockage Detected: Viewport signature matches historical state.")
            return True
            
        # Append to our tracking queue
        self.state_history.append(current_hash)
        
        # Prune older history states to keep evaluation lightweight
        if len(self.state_history) > self.history_limit:
            self.state_history.pop(0)
            
        print(f"[SCROLL MANAGER] ✅ Viewport Shifting Confirmed. New Signature Registered: {current_hash[:8]}...")
        return False

    def reset_history(self):
        """Clears memory buffers when jumping to entirely new layout screens (Stage 2.5)."""
        self.state_history.clear()
        print("[SCROLL MANAGER] History state buffer purged.")
