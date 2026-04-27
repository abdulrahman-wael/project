import pygetwindow as gw

from utils.logger import get_logger

log = get_logger(__name__)

def close_unexpected_popups(bot, expected_titles):
    active = gw.getActiveWindow()
    if not active:
        return

    title = active.title.strip()
    if title == "":
        log.debug("Active window has empty title (likely Desktop). Skipping popup check.")
        return
    
    if any(exp.lower() in title.lower() for exp in expected_titles):
        return  # expected window — nothing to do

    log.warning("Unexpected window detected: '%s'. Attempting to close...", title)

    try:
        bot.type_keys(["esc"])
        bot.wait(500)

        active = gw.getActiveWindow()
        if active and active.title.strip() == title:
            bot.type_keys(["alt", "f4"])
            bot.wait(500)

        log.info("Closed unexpected window: '%s'.", title)
    except Exception as exc:
        log.error("Could not close window '%s': %s", title, exc)