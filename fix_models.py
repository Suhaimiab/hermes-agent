"""Fix deprecated :free models in ~/.hermes/config.yaml"""
import re
from pathlib import Path

config_path = Path.home() / ".hermes" / "config.yaml"
text = config_path.read_text()

# Remove :free suffix from all model references
fixed = re.sub(r"(model:\s*.+):free", r"\1", text)

if fixed != text:
    config_path.write_text(fixed)
    print("Fixed config.yaml — removed :free from all models:")
    for line in text.splitlines():
        if ":free" in line:
            print(f"  - {line.strip()}")
else:
    print("No :free models found in config.yaml")
