# Vision-Based Desktop Automation

> A Python-based desktop automation framework that leverages computer vision and GUI automation to locate arbitrary application icons and perform API-driven data entry without reliance on hardcoded screen coordinates.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Project Overview

This project demonstrates the application of computer vision, GUI automation, and robust error-handling to create an environment-agnostic desktop automation system. The framework dynamically locates target application icons on the desktop using multi-strategy visual detection with resolution-aware scaling, and subsequently performs automated data entry by fetching content from a live API and typing it into the target application.

The system is designed to be resilient across varying screen resolutions, Windows themes, and UI scaling configurations, eliminating the fragility typically associated with coordinate-based automation scripts.

### Video Demonstration

A comprehensive walkthrough of the system in operation is available below, demonstrating the end-to-end workflow from icon detection to automated data entry:

[![Project Demo](https://img.youtube.com/vi/bFWqlnhEnKA/0.jpg)](https://www.youtube.com/watch?v=bFWqlnhEnKA)

---

## Technical Architecture

| Component                | Technology                                                   | Purpose                                            |
| ------------------------ | ------------------------------------------------------------ | -------------------------------------------------- |
| Language                 | Python 3.10+                                                 | Core implementation                                |
| Package Management       | `uv`                                                       | Dependency resolution and environment management   |
| GUI Automation Framework | `botcity-framework-core`                                   | High-level desktop automation primitives           |
| Computer Vision          | OpenCV (Canny edge detection, multi-scale template matching) | Visual icon localization                           |
| GUI Interaction          | `pyautogui`                                                | Mouse control, keyboard input, screenshot capture  |
| Window Management        | `pygetwindow`                                              | Window detection, activation, and state monitoring |
| API Integration          | `requests`                                                 | Primary HTTP client for live data fetching         |
| Clipboard Operations     | `pyperclip`                                                | Fallback data extraction via clipboard             |
| Configuration            | Python module (`config.py`)                                | Centralized, environment-specific parameters       |
| Logging                  | `logging` with `RotatingFileHandler`                     | Structured execution logging to file and console   |

---

## System Capabilities

### Visual Grounding Engine

The system implements a multi-strategy, resolution-aware approach to icon localization:

- **Canny Edge Detection**: Robust against Windows theme variations, color scheme changes, and noisy wallpapers. Detects icon boundaries through gradient-based edge analysis and matches shapes rather than colors.
- **Multi-Scale Template Matching**: Correlates a provided template image against the desktop screenshot at dynamically computed scaling factors. Scales are adjusted based on the ratio between the current screen width and a baseline resolution (1920px), ensuring detection across display DPI variations, zoom levels, and aggressive scaling changes.
- **Dark/Light Mode Template Variants**: Automatically checks for theme-specific template variants (`Capture_dark.png`, `Capture_light.png`) alongside the primary template, improving detection accuracy across Windows personalization settings.
- **Dynamic Strategy Selection**: Runs both template matching and edge detection across all available template variants, then applies Non-Maximum Suppression (NMS) to select the highest-confidence detection.

### Resilient Fallback Mechanisms

If the visual grounding engine fails to locate the target icon, the system employs a two-tier fallback strategy:

1. **Windows Search Fallback**: Launches the application by name via the Windows Start Menu search.
2. **Microsoft Edge Fallback (API Layer)**: If the primary HTTP API request fails, the system automatically opens Microsoft Edge, navigates to the API endpoint, copies the response to the clipboard, and parses the JSON data.

### Automated Data Entry Pipeline

Upon successful application launch, the system:

1. Fetches structured data from a live external API (up to 10 posts per execution cycle, configurable via `MAX_POSTS`)
2. Types the retrieved content into the target application via simulated keyboard input with configurable typing intervals
3. Saves each entry as an individual text file (`post_{id}.txt`) in the designated output directory
4. Generates annotated screenshots documenting the detection process and application state for verification and debugging

### Operational Safeguards

- **Unexpected Popup Detection**: Monitors the active window title during execution. If an unexpected dialog or popup appears, the system attempts to dismiss it via `Escape` or `Alt+F4` before proceeding.
- **Retry Logic with Exponential Backoff**: Configurable retry attempts (`RETRY_ATTEMPTS`) with delay intervals (`RETRY_DELAY`) for icon-based application launches.
- **Window State Verification**: Uses `pygetwindow` to verify that the target application window has actually opened and is active before proceeding with data entry.

### Extensible Application Interface

The framework employs a modular `[app]_ops.py` pattern, allowing rapid adaptation to alternative target applications. The reference implementation (`writing_data/notepad_ops.py`) serves as a template for implementing application-specific operations.

---

## Prerequisites

- Operating System: Windows 10 or later
- Package Manager: [uv](https://github.com/astral-sh/uv)
- Runtime: Python >= 3.10

---

## Installation and Execution

### Dependency Installation

```bash
uv sync
```

### Template Configuration

Place a template image of the target application icon at:

```
grounding/input_templates/Capture.PNG
```

Optional: Add theme-specific variants for improved detection accuracy:

```
grounding/input_templates/Capture_dark.png
grounding/input_templates/Capture_light.png
```

If no template is provided, the system will default to the Windows Search fallback mechanism.

### Execution

```bash
uv run main.py
```

---

## Configuration Reference

All operational parameters are centralized in `config.py`:

| Parameter              | Type            | Description                                                                    | Default                                     |
| ---------------------- | --------------- | ------------------------------------------------------------------------------ | ------------------------------------------- |
| `ICON_NAME`          | `str`         | Display name of the target application for Windows Search fallback             | `"Notepad"`                               |
| `ICON_PATH`          | `str`         | File path to the primary template image for visual detection                   | `"grounding\input_templates\Capture.PNG"` |
| `TEMPLATE_SCALES`    | `List[float]` | Baseline scaling factors for multi-scale template matching                     | `[0.5, 0.75, 1.0, 1.25, 1.5]`             |
| `TEMPLATE_THRESHOLD` | `float`       | Minimum confidence threshold for template matching acceptance                  | `0.4`                                     |
| `MODE`               | `str`         | Execution mode:`"GUI"` (visual automation) or `"PYTHON"` (direct file I/O) | `"GUI"`                                   |
| `POSTS_API`          | `str`         | URL of the external API for data fetching                                      | `"https://dummyjson.com/posts"`           |
| `MAX_POSTS`          | `int`         | Maximum number of posts to fetch and process per execution                     | `10`                                      |
| `RETRY_ATTEMPTS`     | `int`         | Number of retry attempts for icon-based application launch                     | `3`                                       |
| `RETRY_DELAY`        | `int`         | Delay in seconds between retry attempts                                        | `1`                                       |
| `BASE_DIR`           | `Path`        | Base directory for all project outputs                                         | `~/Desktop/project`                       |
| `ANNOTATED_DIR`      | `str`         | Directory for annotated debug screenshots                                      | `grounding\output_annotated_screenshots`  |
| `POSTS_DIR`          | `Path`        | Directory for saved post files                                                 | `BASE_DIR / "writing_data\posts"`         |
| `LOG_DIR`            | `str`         | Directory for execution log files                                              | `"logs"`                                  |

---

## Project Structure

```
project/
├── config.py                          # Centralized configuration parameters
├── main.py                            # Application entry point and orchestration logic
├── pyproject.toml                     # Project metadata, dependencies, and tool configuration
├── README.md                          # Project documentation
├── fetching_data/
│   └── posts.py                       # API data fetching with Edge fallback
├── grounding/
│   ├── input_templates/               # Template images for visual icon detection
│   │   ├── Capture.PNG                # Primary template (required)
│   │   ├── Capture_dark.png           # Dark mode variant (optional)
│   │   └── Capture_light.png          # Light mode variant (optional)
│   └── output_annotated_screenshots/  # Annotated debug screenshots with counter suffixes
├── utils/
│   ├── logger.py                      # Structured logging with rotating file handlers
│   └── window_manager.py              # Popup detection and dismissal logic
└── writing_data/
    └── notepad_ops.py                 # Reference implementation of application-specific operations
```

---

## Output Artifacts

The system generates the following outputs upon execution:

- **Data Files**: Individual text files (`post_{id}.txt`, or `post_{id}_{counter}.txt` if duplicates exist) saved to the configured `POSTS_DIR` directory (default: `~/Desktop/project/writing_data/posts/`)
- **Annotated Screenshots**: Debug images saved to `grounding/output_annotated_screenshots/` with sequentially numbered suffixes (e.g., `annotated_screenshot.png`, `annotated_screenshot_1.png`), documenting the detection process and application state
- **Execution Logs**: Structured log files (`desktop_automation.log`) with rotation (max 5MB per file, 3 backup copies) saved to the configured `LOG_DIR`

---

## Design Principles

1. **Environment Agnosticism**: The resolution-aware scaling algorithm and multi-strategy detection approach ensure reliable operation across different hardware configurations, display resolutions, and Windows personalization settings without manual recalibration.
2. **Operational Resilience**: The tiered fallback architecture (visual detection → Windows Search → Edge API fallback) ensures that the automation pipeline completes successfully even when individual components encounter failures.
3. **Modular Extensibility**: The `[app]_ops.py` abstraction layer decouples the core automation engine from application-specific logic, enabling rapid adaptation to new target applications with minimal code modification.
4. **Observability**: Annotated screenshot generation and structured logging provide a transparent audit trail of the automation process, facilitating debugging, result verification, and post-hoc analysis.
5. **Defensive Execution**: Popup detection, retry logic, and window state verification prevent the automation from entering undefined states due to unexpected UI interactions.

---

## License

This project is distributed under the MIT License.
