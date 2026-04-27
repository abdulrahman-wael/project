from pathlib import Path

# Paths
BASE_DIR = Path.home() / "Desktop" / "project"
ANNOTATED_DIR = "grounding\output_annotated_screenshots"
LOG_DIR       = "logs"
POSTS_DIR = BASE_DIR / "writing_data\posts"
ICON_PATH     = "grounding\input_templates\Capture.PNG"
DEFAULT_ANNOTATED_SCREENSHOT_NAME = "annotated_screenshot"

# Icon
ICON_NAME = "Notepad"

# API 
POSTS_API = "https://dummyjson.com/posts"
MAX_POSTS = 10

# Retry / timing 
RETRY_ATTEMPTS = 3
RETRY_DELAY    = 1

# Mode 
MODE = "GUI".upper() # "GUI"  or "PYTHON"

# Image-matching
TEMPLATE_SCALES    = [0.5, 0.75, 1.0, 1.25, 1.5]
TEMPLATE_THRESHOLD = 0.4