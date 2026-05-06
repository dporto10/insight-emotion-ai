from pathlib import Path

file_path = Path("app/ui/dashboard.py")
text = file_path.read_text(encoding="utf-8-sig")
file_path.write_text(text, encoding="utf-8")

print("BOM removido de app/ui/dashboard.py com sucesso.")
