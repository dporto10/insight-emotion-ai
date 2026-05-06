from pathlib import Path
import re

file_path = Path("app/ui/dashboard.py")
content = file_path.read_text(encoding="utf-8-sig")

new_css_block = '''st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1rem;
    max-width: 1500px;
}

html, body, [class*="css"], .stApp, .stMarkdown, .stText, p, div, span, label, input, textarea, button {
    font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif !important;
}

.main-title {
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1.15;
    color: #1f2a44;
    margin-bottom: 0.35rem;
    letter-spacing: -0.02em;
}

.sub-title {
    font-size: 1.02rem;
    font-weight: 400;
    line-height: 1.6;
    color: #6c7893;
    margin-bottom: 1.4rem;
}

.section-title {
    font-size: 1.28rem;
    font-weight: 700;
    line-height: 1.3;
    color: #24324d;
    margin-top: 0.8rem;
    margin-bottom: 0.9rem;
    letter-spacing: -0.01em;
}

.card {
    background: white;
    border: 1px solid #e6ebf4;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 8px 24px rgba(31,42,68,0.06);
}

.kpi-card {
    background: white;
    border: 1px solid #e6ebf4;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 8px 24px rgba(31,42,68,0.06);
    min-height: 120px;
}

.kpi-title {
    font-size: 0.95rem;
    font-weight: 600;
    line-height: 1.35;
    color: #6b7895;
    margin-bottom: 10px;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.02em;
    color: #21304d;
}

.kpi-sub {
    font-size: 0.92rem;
    font-weight: 400;
    line-height: 1.5;
    color: #7b879f;
    margin-top: 12px;
}

.kpi-red .kpi-value { color: #d84f5f; }
.kpi-green .kpi-value { color: #198b63; }
.kpi-purple .kpi-value { color: #7a57d1; }
.kpi-blue .kpi-value { color: #2f6ee5; }

.insight-box {
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    border: 1px solid #e5ebf5;
    border-radius: 18px;
    padding: 18px;
    color: #2a3650;
    font-size: 0.98rem;
    font-weight: 400;
    line-height: 1.7;
}

.list-box {
    background: white;
    border: 1px solid #e6ebf4;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 8px 24px rgba(31,42,68,0.06);
    font-size: 0.96rem;
    line-height: 1.65;
    color: #2a3650;
}

.small-label {
    color: #74819c;
    font-size: 0.9rem;
    font-weight: 500;
    line-height: 1.4;
}

.big-text {
    color: #1f2a44;
    font-size: 1.08rem;
    font-weight: 700;
    line-height: 1.35;
}

.stButton button {
    font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif !important;
    font-size: 0.96rem;
    font-weight: 700;
}

[data-testid="stMetricLabel"] {
    font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif !important;
    font-size: 1.9rem !important;
    font-weight: 800 !important;
}

[data-testid="stDataFrame"] * {
    font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif !important;
    font-size: 0.92rem !important;
}

textarea {
    font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
}

ul, ol, li {
    font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif !important;
    font-size: 0.96rem;
    line-height: 1.65;
    color: #2a3650;
}
</style>
""", unsafe_allow_html=True)'''

pattern = r'st\.markdown\("""\s*<style>.*?</style>\s*""",\s*unsafe_allow_html=True\)'
new_content, count = re.subn(pattern, new_css_block, content, count=1, flags=re.S)

if count == 0:
    raise SystemExit("Bloco CSS não encontrado no dashboard.py. Nada foi alterado.")

file_path.write_text(new_content, encoding="utf-8")
print("Tipografia atualizada sem sobrescrever o restante do dashboard.")
