# Vision-Based Desktop Automation

Automatically locates any desktop icon (using the best option in these: edge detection, template matching) and performs data entry from an API.
I've used notepad here as an example .. but you can use you're own by changing the configurations mentioned below and having an [app]_ops.py like the one named [notepad_ops.py]

## prerequisits
1. windows 10
2. uv
3. python >= 3.10

## Setup

```bash
uv sync
```

Add template `grounding/input_templates/icon_image.png` (optional). If missing, falls back to Windows Search.

## Run

```bash
uv run main.py
```

## How it works

1. **Grounding using the best option every execution** (Canny edge‑based, template matching) → finds the icon regardless of its position, the theme, the scale of windows...
2. **Fallback** – launches Notepad via Windows Search if template fails.
3. Types 10 fetched posts and saves them as `post_{id}.txt`.

## Config (`config.py`)

- `ICON_NAME` – e.g., `"Notepad"`
- `ICON_PATH` – template image path (optional)
- `TEMPLATE_SCALES` – `[0.5, 0.75, 1.0, 1.25, 1.5]`
- `MODE` – `"GUI"` or `"PYTHON"`

## Output

Annotated screenshots saved in `grounding/output_annotated_screenshots/`.