import os
from datetime import datetime

def save_markdown(content: str, prefix: str = "final_proposal") -> str:
    folder = "proposals"
    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.md"
    filepath = os.path.join(folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath
