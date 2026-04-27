from pathlib import Path
import ctypes
import cv2
import numpy as np

from botcity.core import DesktopBot

from config import (
    ANNOTATED_DIR,
    DEFAULT_ANNOTATED_SCREENSHOT_NAME,
    ICON_PATH,
    ICON_NAME,
    TEMPLATE_SCALES,
    TEMPLATE_THRESHOLD,
)
from utils.logger import get_logger

log = get_logger(__name__)

# ----------------------------------------------------------------------
# Resolution helpers
# ----------------------------------------------------------------------
def _get_screen_size() -> tuple[int, int]:
    """Get primary monitor size without extra dependencies."""
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def get_resolution_aware_scales(template_path: str | Path, base_screen_w: int = 1920) -> list[float]:
    """
    If you captured the template on a 1920-wide screen but now run on 4K/1366x768,
    shift the scale pyramid so the 'middle' of the pyramid matches the new resolution.
    """
    screen_w, _ = _get_screen_size()
    base_scale = screen_w / base_screen_w

    # Widen the pyramid a bit more than before to handle aggressive DPI changes
    relative_scales = [0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0]
    return [round(base_scale * s, 3) for s in relative_scales]

# ----------------------------------------------------------------------
# Detection primitives
# ----------------------------------------------------------------------
def _match_template(
    screenshot_gray: np.ndarray,
    template_path: Path,
    scales: list[float],
    threshold: float,
    method_name: str,
) -> list[dict]:
    """Standard grayscale normalized cross-correlation."""
    template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
    if template is None:
        return []

    th, tw = template.shape[:2]
    matches = []

    for scale in scales:
        rw, rh = int(tw * scale), int(th * scale)
        if rw > screenshot_gray.shape[1] or rh > screenshot_gray.shape[0]:
            continue

        resized = cv2.resize(template, (rw, rh), interpolation=cv2.INTER_AREA)
        res = cv2.matchTemplate(screenshot_gray, resized, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):
            matches.append({
                "x": int(pt[0] + rw / 2),
                "y": int(pt[1] + rh / 2),
                "confidence": float(res[pt[1], pt[0]]),
                "scale": scale,
                "method": method_name,
            })
    return matches


def _match_edges(
    screenshot_gray: np.ndarray,
    template_path: Path,
    scales: list[float],
    threshold: float,
) -> list[dict]:
    """
    Edge-based matching.  Robust across dark/light mode and noisy wallpapers
    because we match shapes, not colors.
    """
    template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
    if template is None:
        return []

    edges_t = cv2.Canny(template, 50, 150)
    th, tw = edges_t.shape[:2]

    # One Canny call for the whole screenshot is enough
    edges_s = cv2.Canny(screenshot_gray, 50, 150)
    matches = []

    for scale in scales:
        rw, rh = int(tw * scale), int(th * scale)
        if rw > edges_s.shape[1] or rh > edges_s.shape[0]:
            continue

        resized = cv2.resize(edges_t, (rw, rh), interpolation=cv2.INTER_AREA)
        res = cv2.matchTemplate(edges_s, resized, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):
            matches.append({
                "x": int(pt[0] + rw / 2),
                "y": int(pt[1] + rh / 2),
                "confidence": float(res[pt[1], pt[0]]),
                "scale": scale,
                "method": "edge",
            })
    return matches


def _nms(detections: list[dict], min_dist: int = 40) -> list[dict]:
    """
    Simple distance-based Non-Maximum Suppression.
    If two matches are within `min_dist` pixels, keep only the higher-confidence one.
    """
    if not detections:
        return []

    detections = sorted(detections, key=lambda d: d["confidence"], reverse=True)
    kept = []

    while detections:
        best = detections.pop(0)
        kept.append(best)
        detections = [
            d for d in detections
            if abs(d["x"] - best["x"]) > min_dist or abs(d["y"] - best["y"]) > min_dist
        ]
    return kept


# ----------------------------------------------------------------------
# Main entrypoint
# ----------------------------------------------------------------------
def detect_icon(bot: DesktopBot, icon_name: str = ICON_NAME):
    bot.type_keys(["win", "d"])
    bot.wait(1200)

    # --- screenshot ----------------------------------------------------
    out_dir = Path(ANNOTATED_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    screenshot_path = out_dir / f"{DEFAULT_ANNOTATED_SCREENSHOT_NAME}.png"
    counter = 1
    while screenshot_path.exists():
        screenshot_path = out_dir / f"{DEFAULT_ANNOTATED_SCREENSHOT_NAME}_{counter}.png"
        counter += 1

    bot.screenshot(screenshot_path)

    image_color = cv2.imread(str(screenshot_path))
    image_gray = cv2.cvtColor(image_color, cv2.COLOR_BGR2GRAY)

    # --- template candidates -------------------------------------------
    # You can drop in extra templates for dark/light mode:
    #   Capture.PNG
    #   Capture_dark.png
    #   Capture_light.png
    stem = Path(ICON_PATH).stem
    suffix = Path(ICON_PATH).suffix
    parent = Path(ICON_PATH).parent

    template_candidates = [
        Path(ICON_PATH),
        parent / f"{stem}_dark{suffix}",
        parent / f"{stem}_light{suffix}",
    ]

    # --- run detectors -------------------------------------------------
    scales = get_resolution_aware_scales(ICON_PATH)

    all_detections: list[dict] = []

    for tpl in template_candidates:
        if not tpl.exists():
            continue

        # 1) Classic template match
        all_detections.extend(
            _match_template(image_gray, tpl, scales, TEMPLATE_THRESHOLD, "template")
        )

        # 2) Edge match (slightly lower threshold because edge images are sparser)
        all_detections.extend(
            _match_edges(image_gray, tpl, scales, max(0.25, TEMPLATE_THRESHOLD * 0.75))
        )

    # --- arbitrate: NMS + best confidence ------------------------------
    detections = _nms(all_detections, min_dist=50)

    if detections:
        best = max(detections, key=lambda d: d["confidence"])

        # Annotate result
        cv2.circle(image_color, (best["x"], best["y"]), 22, (0, 255, 0), 3)
        cv2.putText(
            image_color,
            f"{best['method']}:{best['confidence']:.2f}",
            (best["x"] + 25, best["y"]),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )
        cv2.imwrite(str(screenshot_path), image_color)

        log.info(
            "Detected via '%s' at (%d, %d) conf=%.3f (scale=%.2f)",
            best["method"], best["x"], best["y"], best["confidence"], best["scale"],
        )
        return best["x"], best["y"]

    # --- fallback ------------------------------------------------------
    log.warning("All detection methods failed. Will use Windows Search fallback.")
    return None