import os

PROMPT_DIR = os.path.join(os.path.dirname(__file__), "prompts")


def load_prompts():
    files = sorted(
        [f for f in os.listdir(PROMPT_DIR) if f.endswith(".md")]
    )

    prompts = []
    for filename in files:
        path = os.path.join(PROMPT_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            prompts.append(f.read())

    return prompts
