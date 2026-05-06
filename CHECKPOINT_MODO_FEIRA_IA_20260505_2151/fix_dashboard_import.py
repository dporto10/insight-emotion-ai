from pathlib import Path

file_path = Path("app/ui/dashboard.py")
content = file_path.read_text(encoding="utf-8")

prefix = '''import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

'''

if "ROOT_DIR = Path(__file__).resolve().parents[2]" not in content:
    content = prefix + content

file_path.write_text(content, encoding="utf-8")
print("dashboard.py ajustado com sys.path.")
