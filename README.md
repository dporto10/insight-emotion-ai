# Insight Emotion AI

Protótipo de análise emocional e comercial para vídeos de vendas e pitch.

## Funcionalidades

- Upload de vídeo de venda
- Extração e transcrição de áudio
- Análise emocional facial
- Análise vocal
- Diagnóstico comercial
- Resumo executivo por IA
- Plano estratégico de melhoria
- Evidências da conversa analisadas por IA

## Como rodar

1. Criar ambiente virtual:

python -m venv .venv310

2. Ativar ambiente:

.venv310\Scripts\activate

3. Instalar dependências:

pip install -r requirements.txt

4. Criar arquivo .env com base no .env.example:

OPENAI_API_KEY=sua_chave_aqui
INSIGHT_LLM_MODEL=gpt-4.1-mini
WHISPER_MODEL=small

5. Rodar dashboard:

python -m streamlit run app\ui\dashboard.py

## Observações

- O arquivo .env não deve ser enviado ao GitHub.
- A pasta .venv310 não deve ser enviada ao GitHub.
- Para melhor funcionamento, o computador precisa ter FFmpeg instalado.
