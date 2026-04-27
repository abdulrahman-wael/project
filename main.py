from botcity.core import DesktopBot

from grounding.icon_detector import detect_icon
from fetching_data.posts import fetch_posts
from writing_data.notepad_ops import open_notepad, wait_for_notepad, type_and_save_post, save_file

from config import LOG_DIR, MODE, RETRY_ATTEMPTS, RETRY_DELAY, ICON_NAME
from utils.logger import get_logger, setup_logging
from utils.window_manager import close_unexpected_popups

def main() -> None:
    
    setup_logging(LOG_DIR)
    log = get_logger(__name__)
    log.info(f"Desktop automation starting (MODE={MODE}).")
    
    bot = DesktopBot()
    
    posts = fetch_posts(bot)
    if not posts:
        log.error("No posts available.")
        exit(1)

    log.info("Detecting icon...")
    icon_position = detect_icon(bot, ICON_NAME)
    
    
    for post in posts:
        
        log.info("Processing post %d...", post["id"])
        success = False
        
        if MODE == "GUI":
            for attempt in range(RETRY_ATTEMPTS):
                close_unexpected_popups(bot, [ICON_NAME, "Desktop", "Save As"])

                log.info("Opening Notepad (Attempt %d/%d)...", attempt + 1, RETRY_ATTEMPTS)
                open_notepad(bot, icon_position, force_search=False)
                window = wait_for_notepad()
                if window:
                    success = True
                    break
                log.warning("Attempt %d failed. Retrying in %.1f sec", attempt + 1, RETRY_DELAY)
                bot.wait(RETRY_DELAY*1000)
                
            if not success:
                log.info("All icon attempts failed — trying Windows Search fallback.")
                open_notepad(bot, icon_position, force_search=True)
                window = wait_for_notepad()
                if window:
                    success = True

            if not success:
                log.warning(f"Failed to open Notepad for post {post['id']}. Skipping...")
                continue
            
            type_and_save_post(bot, post)

        else:
            content = f"Title: {post['title']}\n\n{post['body']}\n"
            save_file(post, content)

        log.info(f"Post {post['id']} saved.")
        bot.wait(500)

    log.info("All posts processed successfully.")
    

if __name__ == "__main__":
    main()
    