import json

import pyperclip
import requests


from config import MAX_POSTS, POSTS_API
from utils.logger import get_logger

log = get_logger(__name__)

def fetch_posts(bot) -> list[dict]:
    try:
        log.info("Fetching posts from %s", POSTS_API)
        response = requests.get(POSTS_API)
        response.raise_for_status()
        posts = response.json()['posts'][:MAX_POSTS]
        log.info("Fetched %d posts from API.", len(posts))
        return posts
    except Exception as exc:
        log.warning("API call failed (%s). Falling back to Edge.", exc)
        return _fetch_posts_from_edge(bot)


# TODO needs work (exception handling)
def _fetch_posts_from_edge(bot) -> list[dict]:
    log.info("Opening Edge to fetch posts...")
    bot.type_windows()
    bot.wait(500)
    bot.kb_type("edge")
    bot.enter()
    bot.wait(2000)

    bot.type_keys(["ctrl", "l"])
    bot.kb_type(POSTS_API)
    bot.enter()
    bot.wait(5000)

    bot.control_a()
    bot.control_c()
    bot.wait(200)
    
    raw = pyperclip.paste()
    posts = json.loads(raw)[:MAX_POSTS]
    log.info("Fetched %d posts via Edge fallback.", len(posts))
    return posts
