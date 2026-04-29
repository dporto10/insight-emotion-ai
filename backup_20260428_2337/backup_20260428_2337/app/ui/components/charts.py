import plotly.graph_objects as go

def criar_grafico_emocional(df_plot, metrics, formatar_tempo):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_plot["tempo_segundos"],
            y=df_plot["y"],
            mode="lines",
            line=dict(width=3, color="#64a8ff"),
            text=df_plot["emocao_negocio"],
            hovertemplate="Tempo: %{x}s<br>Emoção: %{text}<extra></extra>"
        )
    )

    pico = metrics.get("pico_emocional_segundos")
    queda = metrics.get("queda_interesse_segundos")

    if pico:
        fig.add_vline(
            x=pico,
            line_dash="dash",
            line_color="#9b7bff",
            annotation_text=f"Pico {formatar_tempo(pico)}"
        )

    if queda:
        fig.add_vline(
            x=queda,
            line_dash="dash",
            line_color="#ff5f62",
            annotation_text=f"Queda {formatar_tempo(queda)}"
        )

    fig.update_layout(
        height=410,
        paper_bgcolor="#0b1730",
        plot_bgcolor="#0b1730",
        font=dict(color="#d9e5ff"),
        margin=dict(l=10,r=10,t=20,b=10)
    )

    return fig
