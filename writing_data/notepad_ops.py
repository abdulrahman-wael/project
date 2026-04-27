from pathlib import Path
import time

import pyautogui

import pygetwindow as gw

from config import ICON_NAME, BASE_DIR, MODE, POSTS_DIR
from utils.logger import get_logger

log = get_logger(__name__)


# Opening

def open_notepad(bot, icon_position, force_search = False):
    
    if not force_search and icon_position:
        x, y = icon_position
        log.debug("Double-clicking Notepad icon at (%d, %d).", x, y)
        bot.mouse_move(x, y)
        pyautogui.doubleClick()   # bypasses BotCity's element-wrapper
        return True

    # fallback search
    log.info("Using Windows Search to open The app.")
    bot.type_windows()
    bot.wait(300)
    bot.kb_type(ICON_NAME)
    bot.enter()
    bot.wait(300)
    return True

def wait_for_notepad(timeout = 10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        wins = gw.getWindowsWithTitle(ICON_NAME)
        if wins:
            try:
                wins[0].activate()
            except Exception:
                raise
            log.debug("Notepad window found.")
            return wins[0]
        time.sleep(0.5)
    log.warning("Notepad window not found within %.1f s.", timeout)
    return None


# Typying / Saving 

def type_and_save_post(bot, post):
    content = f"Title: {post['title']}\n\n{post['body']}\n"

    for line in content.splitlines():
        bot.kb_type(line, interval=0.02)
        bot.enter()
    
    save_file(bot, post, content)

def save_file(bot, post, content):
    base_name = f"post_{post['id']}"
    full_path = Path(POSTS_DIR)
    full_path.mkdir(parents=True, exist_ok=True)
    
    full_path = full_path / f"{base_name}.txt"
    counter = 1

    while Path.exists(full_path):
        full_path = Path(POSTS_DIR) / f"{base_name}_{counter}.txt"
        counter += 1
    
    if MODE == "GUI":
        bot.control_s()
        bot.wait(500)
        bot.kb_type(str(full_path))
        bot.enter()
        bot.wait(500)
        bot.type_keys(["ctrl", "w"])
    else:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        log.debug("Written directly to %s.", full_path)
  

        