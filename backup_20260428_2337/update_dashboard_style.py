import re

file_path = "app/ui/dashboard.py"

new_css = """
st.markdown(\"\"\"
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1rem;
    max-width: 1500px;
}

html, body, [class*="css"], .stApp, .stMarkdown, .stText, p, div, span {
    font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif !important;
}

.main-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #1f2a44;
}

.sub-title {
    font-size: 1.02rem;
    color: #6c7893;
}

.section-title {
    font-size: 1.28rem;
    font-weight: 700;
    color: #24324d;
}

.card {
    background: white;
    border: 1px solid #e6ebf4;
    border-radius: 18px;
    padding: 18px;
}

.kpi-card {
    background: white;
    border: 1px solid #e6ebf4;
    border-radius: 18px;
    padding: 18px;
}

.kpi-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #6b7895;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: #21304d;
}

.kpi-sub {
    font-size: 0.92rem;
    color: #7b879f;
}

.kpi-red .kpi-value { color: #d84f5f; }
.kpi-green .kpi-value { color: #198b63; }
.kpi-purple .kpi-value { color: #7a57d1; }
.kpi-blue .kpi-value { color: #2f6ee5; }

.insight-box {
    background: #ffffff;
    border: 1px solid #e5ebf5;
    border-radius: 18px;
    padding: 18px;
    color: #2a3650;
}

.list-box {
    background: white;
    border: 1px solid #e6ebf4;
    border-radius: 18px;
    padding: 18px;
}

.stButton button {
    background: linear-gradient(90deg,#5a7cff,#6f61ff);
    color: white;
    border-radius: 12px;
    font-weight: 700;
}
</style>
\"\"\", unsafe_allow_html=True)
"""

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(
    r"st\.markdown\(\"\"\"<style>.*?</style>\"\"\", unsafe_allow_html=True\)",
    new_css,
    content,
    flags=re.S
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("CSS do dashboard atualizado com sucesso.")
