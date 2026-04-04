import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ═══════════════════════════════════════════
# CONFIG DA PÁGINA
# ═══════════════════════════════════════════
st.set_page_config(
    page_title="AgroAnalítica IFRO",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════
# CSS CUSTOMIZADO
# ═══════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background-color: #0a0f0a;
}
[data-testid="stSidebar"] {
    background-color: #0f1a0f;
    border-right: 1px solid #1e3a1e;
}
h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
    color: #4ade80 !important;
}
.kpi-box {
    background: #0f1a0f;
    border: 1px solid #1e3a1e;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 8px;
}
.kpi-label {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #5a7a5a;
    margin-bottom: 6px;
}
.kpi-value {
    font-family: 'Space Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    color: #4ade80;
    line-height: 1;
}
.kpi-unit {
    font-size: 13px;
    color: #5a7a5a;
}
.kpi-sub {
    font-size: 11px;
    color: #5a7a5a;
    margin-top: 4px;
}
.score-bar-container {
    display: flex; align-items: center; gap: 10px; margin: 4px 0;
}
.score-bar-label {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: #94b894;
    width: 30px;
}
.score-bar-outer {
    flex: 1;
    height: 8px;
    background: #152115;
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid #1e3a1e;
}
.score-bar-pct {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    width: 36px;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# PLOTLY DARK TEMPLATE
# ═══════════════════════════════════════════
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#0a0f0a",
    plot_bgcolor="#0a0f0a",
    font=dict(family="Space Mono, monospace", color="#5a7a5a", size=11),
    xaxis=dict(gridcolor="#1e3a1e", linecolor="#1e3a1e"),
    yaxis=dict(gridcolor="#1e3a1e", linecolor="#1e3a1e"),
    margin=dict(l=50, r=20, t=40, b=40),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="right", x=1,
        font=dict(size=11)
    ),
    hoverlabel=dict(
        bgcolor="#0f1a0f",
        bordercolor="#2a5a2a",
        font=dict(family="Space Mono", size=11, color="#94b894")
    )
)

# ═══════════════════════════════════════════
# CARREGAR E PROCESSAR DADOS
# ═══════════════════════════════════════════
@st.cache_data
def carregar_dados():
    df = pd.read_csv(
        "Dados2024atéhoje.csv",
        skiprows=[1], quotechar='"', sep=',', encoding='utf-8'
    )
    df.columns = [c.strip() for c in df.columns]

    def purificar(valor):
        if pd.isna(valor) or str(valor).strip() == "":
            return 0.0
        limpo = str(valor).replace('"', '').replace(',', '.').strip()
        try:
            return float(limpo)
        except:
            return 0.0

    cols_num = ['Precipitação', 'Temp. Média', 'Temp. Máx.', 'Temp. Mín.',
                'Pressão Barométrica', 'Umidade Rel.', 'Evapotranspiração',
                'Rad. Solar', 'UV', 'Vel. Méd. Vento', 'Vel. Máx. Vento']

    for col in cols_num:
        if col in df.columns:
            df[col] = df[col].apply(purificar)

    df['Data'] = pd.to_datetime(df['Data'], format='%m/%d/%Y', errors='coerce')
    df = df.dropna(subset=['Data']).sort_values('Data').reset_index(drop=True)

    # Variáveis agronômicas
    df['GDD'] = ((df['Temp. Máx.'] + df['Temp. Mín.']) / 2 - 10).clip(lower=0)
    df['GDD_acum'] = df['GDD'].cumsum()
    df['Energia_MJ'] = df['Rad. Solar'] * 0.0864
    df['Rad_45d'] = df['Energia_MJ'].rolling(45).sum()
    df['Chuva_30d'] = df['Precipitação'].rolling(30).sum()
    df['GDD_30d'] = df['GDD'].rolling(30).sum()
    df['Mes'] = df['Data'].dt.month
    df['AnoMes'] = df['Data'].dt.to_period('M').astype(str)

    return df

df = carregar_dados()

# ═══════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🌱 AgroAnalítica IFRO")
    st.caption("Estação — Colorado do Oeste · RO")
    st.divider()

    painel = st.radio(
        "Navegar para",
        ["📊 Visão Geral", "🌡️ Temperatura & GDD",
         "☀️ Radiação Solar", "💧 Balanço Hídrico",
         "🌾 Janela de Plantio", "📋 Dados Brutos"],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption(f"📅 {df['Data'].min().strftime('%d/%m/%Y')} → {df['Data'].max().strftime('%d/%m/%Y')}")
    st.caption(f"📁 {len(df)} dias registrados")

# ═══════════════════════════════════════════
# HELPER: KPI
# ═══════════════════════════════════════════
def kpi(label, value, unit, sub="", color="#4ade80"):
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="color:{color}">
            {value}<span class="kpi-unit"> {unit}</span>
        </div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

def filtrar_periodo(dias):
    if dias == 0:
        return df
    return df.tail(dias)

# ═══════════════════════════════════════════
# DADOS MENSAIS
# ═══════════════════════════════════════════
mensal_precip = df.groupby('AnoMes')['Precipitação'].sum().reset_index()
mensal_et     = df.groupby('AnoMes')['Evapotranspiração'].sum().reset_index()
mensal_gdd    = df.groupby('AnoMes')['GDD'].sum().reset_index()
gdd_por_mes   = df.groupby('Mes')['GDD'].mean()
precip_por_mes = df.groupby('Mes')['Precipitação'].mean()
rad_por_mes   = df.groupby('Mes')['Energia_MJ'].mean() * 30

MESES = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

# ═══════════════════════════════════════════
# CULTIVARES
# ═══════════════════════════════════════════
CULTIVARES = {
    "🌿 Soja (Ciclo Médio 120d)": {
        "ciclo": 120,
        "fases": [
            {"nome": "Germinação/Emergência",  "dias": 7,  "gdd": 70,  "chuva": 30,  "rad": 50},
            {"nome": "Crescimento Vegetativo", "dias": 35, "gdd": 420, "chuva": 150, "rad": 280},
            {"nome": "Florescimento",          "dias": 20, "gdd": 240, "chuva": 80,  "rad": 180},
            {"nome": "Enchimento de Grãos",    "dias": 40, "gdd": 440, "chuva": 120, "rad": 350},
            {"nome": "Maturação",              "dias": 18, "gdd": 180, "chuva": 40,  "rad": 140},
        ]
    },
    "🌽 Milho (Ciclo Normal 130d)": {
        "ciclo": 130,
        "fases": [
            {"nome": "Germinação",             "dias": 7,  "gdd": 75,  "chuva": 25,  "rad": 50},
            {"nome": "Crescimento Vegetativo", "dias": 45, "gdd": 560, "chuva": 200, "rad": 360},
            {"nome": "Espigamento/Floração",   "dias": 20, "gdd": 260, "chuva": 100, "rad": 200},
            {"nome": "Enchimento de Grãos",    "dias": 40, "gdd": 440, "chuva": 120, "rad": 320},
            {"nome": "Maturação Fisiológica",  "dias": 18, "gdd": 180, "chuva": 30,  "rad": 130},
        ]
    },
    "🫘 Feijão Carioca (90d)": {
        "ciclo": 90,
        "fases": [
            {"nome": "Germinação",             "dias": 5,  "gdd": 50,  "chuva": 20,  "rad": 40},
            {"nome": "Crescimento Vegetativo", "dias": 25, "gdd": 280, "chuva": 100, "rad": 200},
            {"nome": "Floração/Vagem",         "dias": 30, "gdd": 330, "chuva": 120, "rad": 250},
            {"nome": "Maturação",              "dias": 30, "gdd": 300, "chuva": 40,  "rad": 220},
        ]
    },
    "☕ Café Arábica (365d)": {
        "ciclo": 365,
        "fases": [
            {"nome": "Dormência/Repouso",      "dias": 60,  "gdd": 600,  "chuva": 30,  "rad": 450},
            {"nome": "Floração",               "dias": 30,  "gdd": 360,  "chuva": 40,  "rad": 270},
            {"nome": "Chumbinho/Expansão",     "dias": 90,  "gdd": 990,  "chuva": 300, "rad": 720},
            {"nome": "Granação",               "dias": 120, "gdd": 1200, "chuva": 250, "rad": 960},
            {"nome": "Maturação/Colheita",     "dias": 65,  "gdd": 585,  "chuva": 60,  "rad": 500},
        ]
    },
    "🥔 Mandioca (12 meses)": {
        "ciclo": 365,
        "fases": [
            {"nome": "Brotação/Enraizamento",  "dias": 30,  "gdd": 300,  "chuva": 80,  "rad": 240},
            {"nome": "Crescimento Vegetativo", "dias": 120, "gdd": 1200, "chuva": 600, "rad": 960},
            {"nome": "Tuberização",            "dias": 120, "gdd": 1200, "chuva": 300, "rad": 960},
            {"nome": "Maturação/Colheita",     "dias": 95,  "gdd": 855,  "chuva": 100, "rad": 700},
        ]
    },
}

def calcular_janelas(cult):
    scores = []
    gdd_ideal   = sum(f["gdd"]   for f in cult["fases"])
    chuva_ideal = sum(f["chuva"] for f in cult["fases"])
    rad_ideal   = sum(f["rad"]   for f in cult["fases"])

    for inicio in range(12):
        dias_rest = cult["ciclo"]
        gdd_a = chuva_a = rad_a = 0
        m = inicio
        while dias_rest > 0:
            d = min(dias_rest, 30)
            idx = (m % 12) + 1
            gdd_a   += gdd_por_mes.get(idx, 0)   * d
            chuva_a += precip_por_mes.get(idx, 0) * d
            rad_a   += (rad_por_mes.get(idx, 0) / 30) * d
            dias_rest -= d
            m += 1
        s = (min(1, gdd_a/gdd_ideal) + min(1, chuva_a/chuva_ideal) + min(1, rad_a/rad_ideal)) / 3
        scores.append({
            "mes_idx": inicio, "mes": MESES[inicio], "score": s,
            "gdd_acum": gdd_a, "chuva_acum": chuva_a, "rad_acum": rad_a,
            "gdd_ideal": gdd_ideal, "chuva_ideal": chuva_ideal, "rad_ideal": rad_ideal
        })
    return sorted(scores, key=lambda x: x["score"], reverse=True)

# ═══════════════════════════════════════════════════════════════
# PAINEL 1: VISÃO GERAL
# ═══════════════════════════════════════════════════════════════
if painel == "📊 Visão Geral":
    st.title("📊 Visão Geral")
    st.caption("Série histórica completa da Estação IFRO — Colorado do Oeste · RO")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: kpi("GDD Acumulado", f"{df['GDD_acum'].iloc[-1]:,.0f}", "°C·dia", "desde fev/2024")
    with c2: kpi("Precipitação Total", f"{df['Precipitação'].sum():,.0f}", "mm", "acumulado", "#60a5fa")
    with c3: kpi("Radiação Média", f"{df['Rad. Solar'].mean():.1f}", "W/m²", "média diária", "#fbbf24")
    with c4: kpi("Temp. Média", f"{df['Temp. Média'].mean():.1f}", "°C", "do período", "#f87171")
    with c5: kpi("ET Total", f"{df['Evapotranspiração'].sum():,.0f}", "mm", "acumulada", "#22c55e")
    with c6: kpi("Dias Registrados", f"{len(df)}", "dias", "série histórica", "#94b894")

    # Temperatura histórica
    fig = go.Figure()
    step = max(1, len(df)//200)
    dfs = df.iloc[::step]
    fig.add_trace(go.Scatter(x=dfs['Data'], y=dfs['Temp. Máx.'], name="Tmax",
        line=dict(color="#f87171", width=1), opacity=0.7))
    fig.add_trace(go.Scatter(x=dfs['Data'], y=dfs['Temp. Média'], name="Tméd",
        line=dict(color="#4ade80", width=2)))
    fig.add_trace(go.Scatter(x=dfs['Data'], y=dfs['Temp. Mín.'], name="Tmin",
        line=dict(color="#60a5fa", width=1), opacity=0.7))
    fig.update_layout(**PLOTLY_LAYOUT, title="Temperatura Diária — Série Histórica",
                      yaxis_title="°C", height=250)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=dfs['Data'], y=dfs['GDD_acum'], name="GDD Acumulado",
            line=dict(color="#4ade80", width=2), fill='tozeroy',
            fillcolor='rgba(74,222,128,0.08)'))
        fig2.update_layout(**PLOTLY_LAYOUT, title="GDD Acumulado",
                           yaxis_title="°C·dia", height=220, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=mensal_precip['AnoMes'], y=mensal_precip['Precipitação'],
            name="Precip.", marker_color='rgba(96,165,250,0.7)'))
        fig3.update_layout(**PLOTLY_LAYOUT, title="Precipitação Mensal",
                           yaxis_title="mm", height=220, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# PAINEL 2: TEMPERATURA & GDD
# ═══════════════════════════════════════════════════════════════
elif painel == "🌡️ Temperatura & GDD":
    st.title("🌡️ Temperatura & GDD")

    periodo = st.select_slider(
        "Período de análise",
        options=[30, 60, 90, 180, 365, 0],
        value=180,
        format_func=lambda x: "Tudo" if x == 0 else f"{x} dias"
    )
    d = filtrar_periodo(periodo)

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Tmax Absoluta",  f"{d['Temp. Máx.'].max():.1f}", "°C", "", "#f87171")
    with c2: kpi("Tmin Absoluta",  f"{d['Temp. Mín.'].min():.1f}", "°C", "", "#60a5fa")
    with c3: kpi("GDD (30d móvel)",f"{d['GDD_30d'].iloc[-1]:.0f}", "°C·d", "últimos 30 dias")
    with c4: kpi("Amplitude Média",f"{(d['Temp. Máx.']-d['Temp. Mín.']).mean():.1f}", "°C", "Tmax - Tmin")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d['Data'], y=d['Temp. Máx.'], name="Tmax",
        line=dict(color="#f87171", width=1.5)))
    fig.add_trace(go.Scatter(x=d['Data'], y=d['Temp. Média'], name="Tméd",
        line=dict(color="#4ade80", width=2)))
    fig.add_trace(go.Scatter(x=d['Data'], y=d['Temp. Mín.'], name="Tmin",
        line=dict(color="#60a5fa", width=1.5),
        fill='tonexty', fillcolor='rgba(96,165,250,0.06)'))
    fig.update_layout(**PLOTLY_LAYOUT, title="Temperatura Diária com Amplitude",
                      yaxis_title="°C", height=280)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=d['Data'], y=d['GDD'], name="GDD",
            marker_color='rgba(74,222,128,0.6)'))
        fig2.update_layout(**PLOTLY_LAYOUT, title="GDD Diário (Tbase=10°C)",
                           yaxis_title="°C·dia", height=220, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=d['Data'], y=d['GDD_30d'], name="GDD 30d",
            line=dict(color="#fbbf24", width=2), fill='tozeroy',
            fillcolor='rgba(251,191,36,0.1)'))
        fig3.update_layout(**PLOTLY_LAYOUT, title="GDD Janela Móvel 30 dias",
                           yaxis_title="°C·dia", height=220, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# PAINEL 3: RADIAÇÃO SOLAR
# ═══════════════════════════════════════════════════════════════
elif painel == "☀️ Radiação Solar":
    st.title("☀️ Radiação Solar")

    periodo = st.select_slider(
        "Período",
        options=[30, 60, 90, 180, 365, 0],
        value=180,
        format_func=lambda x: "Tudo" if x == 0 else f"{x} dias"
    )
    d = filtrar_periodo(periodo)
    last45 = d[d['Rad_45d'] > 0]['Rad_45d'].iloc[-1] if len(d[d['Rad_45d'] > 0]) > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Rad. Máx.",   f"{d['Rad. Solar'].max():.0f}", "W/m²", "", "#fbbf24")
    with c2: kpi("Acúmulo 45d", f"{last45:.0f}", "MJ/m²", "janela móvel", "#f97316")
    with c3: kpi("ET Total",    f"{d['Evapotranspiração'].sum():.0f}", "mm", "no período", "#22c55e")
    with c4: kpi("Rad. Média",  f"{d['Rad. Solar'].mean():.1f}", "W/m²", "média diária", "#fbbf24")

    # Gráfico duplo eixo: barra + linha
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=d['Data'], y=d['Rad. Solar'], name="Rad. Diária (W/m²)",
        marker_color='rgba(251,191,36,0.5)'), secondary_y=False)
    fig.add_trace(go.Scatter(x=d['Data'], y=d['Rad_45d'], name="Acúmulo 45d (MJ/m²)",
        line=dict(color="#f97316", width=2.5)), secondary_y=True)
    fig.update_layout(**PLOTLY_LAYOUT, title="Radiação Diária + Acúmulo 45 dias", height=300)
    fig.update_yaxes(title_text="W/m²", secondary_y=False,
                     gridcolor="#1e3a1e", color="#5a7a5a")
    fig.update_yaxes(title_text="MJ/m²", secondary_y=True,
                     gridcolor=None, color="#f97316")
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=d['Data'], y=d['Evapotranspiração'], name="ET",
            line=dict(color="#22c55e", width=1.5), fill='tozeroy',
            fillcolor='rgba(34,197,94,0.1)'))
        fig2.update_layout(**PLOTLY_LAYOUT, title="Evapotranspiração Diária",
                           yaxis_title="mm/dia", height=220, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        # Scatter mensal Rad x ET
        scatter_df = d.copy()
        scatter_df['AnoMes'] = scatter_df['Data'].dt.to_period('M').astype(str)
        sc = scatter_df.groupby('AnoMes').agg(
            Rad=('Rad. Solar','mean'), ET=('Evapotranspiração','mean')).reset_index()
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=sc['Rad'], y=sc['ET'], mode='markers',
            marker=dict(color='rgba(251,191,36,0.7)', size=9),
            text=sc['AnoMes'], name="Mês"))
        fig3.update_layout(**PLOTLY_LAYOUT, title="Radiação × ET (médias mensais)",
                           xaxis_title="Rad. média (W/m²)",
                           yaxis_title="ET média (mm)", height=220, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# PAINEL 4: BALANÇO HÍDRICO
# ═══════════════════════════════════════════════════════════════
elif painel == "💧 Balanço Hídrico":
    st.title("💧 Balanço Hídrico")

    precip_total = df['Precipitação'].sum()
    et_total     = df['Evapotranspiração'].sum()
    balanco      = precip_total - et_total
    chuva30      = df[df['Chuva_30d'] > 0]['Chuva_30d'].iloc[-1]

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Precip. Total", f"{precip_total:,.0f}", "mm", "", "#60a5fa")
    with c2: kpi("ET Total",      f"{et_total:,.0f}",     "mm", "", "#22c55e")
    with c3: kpi("Balanço (P-ET)",f"{balanco:,.0f}",      "mm", "", "#fbbf24" if balanco > 0 else "#f87171")
    with c4: kpi("Chuva 30d",     f"{chuva30:.0f}",       "mm", "últimos 30d", "#94b894")

    # Barras mensais P vs ET
    fig = go.Figure()
    fig.add_trace(go.Bar(x=mensal_precip['AnoMes'], y=mensal_precip['Precipitação'],
        name="Precipitação", marker_color='rgba(96,165,250,0.7)'))
    fig.add_trace(go.Bar(x=mensal_et['AnoMes'], y=mensal_et['Evapotranspiração'],
        name="ET", marker_color='rgba(34,197,94,0.6)'))
    fig.update_layout(**PLOTLY_LAYOUT, title="Precipitação × ET por Mês",
                      yaxis_title="mm", height=260, barmode='group')
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df['Data'], y=df['Chuva_30d'],
            line=dict(color="#60a5fa", width=2), fill='tozeroy',
            fillcolor='rgba(96,165,250,0.1)', name="Chuva 30d"))
        fig2.update_layout(**PLOTLY_LAYOUT, title="Chuva Acumulada Janela 30 dias",
                           yaxis_title="mm", height=220, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=df['Data'], y=df['Umidade Rel.'],
            line=dict(color="#a78bfa", width=1.5), fill='tozeroy',
            fillcolor='rgba(167,139,250,0.08)', name="Umidade"))
        fig3.update_layout(**PLOTLY_LAYOUT, title="Umidade Relativa do Ar",
                           yaxis=dict(range=[0,100], title="% UR", gridcolor="#1e3a1e"),
                           height=220, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# PAINEL 5: JANELA DE PLANTIO
# ═══════════════════════════════════════════════════════════════
elif painel == "🌾 Janela de Plantio":
    st.title("🌾 Janela de Plantio")
    st.caption("Cálculo baseado nos dados históricos reais da estação — Colorado do Oeste · RO")

    cultura_sel = st.selectbox("Selecione a cultura", list(CULTIVARES.keys()))
    cult = CULTIVARES[cultura_sel]
    scores = calcular_janelas(cult)
    melhor  = scores[0]
    segundo = scores[1]
    pior    = scores[-1]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### ✅ Melhor Janela")
        kpi("Mês de Plantio", melhor["mes"], "", f"Score: {melhor['score']*100:.0f}%")
        st.caption(f"GDD: {melhor['gdd_acum']:.0f} / {melhor['gdd_ideal']} °C·d")
        st.caption(f"Chuva: {melhor['chuva_acum']:.0f} / {melhor['chuva_ideal']} mm")
        st.caption(f"Rad: {melhor['rad_acum']:.0f} / {melhor['rad_ideal']} MJ/m²")
    with c2:
        st.markdown("### 🟡 2ª Opção")
        kpi("Mês de Plantio", segundo["mes"], "", f"Score: {segundo['score']*100:.0f}%", "#fbbf24")
    with c3:
        st.markdown("### ❌ Evitar")
        kpi("Mês de Plantio", pior["mes"], "", f"Score: {pior['score']*100:.0f}%", "#f87171")

    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Score por Mês de Plantio**")
        # Radar / bar de scores por mês
        scores_ord = sorted(scores, key=lambda x: x["mes_idx"])
        fig = go.Figure()
        cores = ["#4ade80" if s["score"] > 0.75 else "#fbbf24" if s["score"] > 0.55 else "#f87171"
                 for s in scores_ord]
        fig.add_trace(go.Bar(
            x=[s["mes"] for s in scores_ord],
            y=[round(s["score"]*100, 1) for s in scores_ord],
            marker_color=cores,
            text=[f"{s['score']*100:.0f}%" for s in scores_ord],
            textposition='outside'
        ))
        fig.update_layout(**PLOTLY_LAYOUT, yaxis=dict(range=[0, 110], title="%"),
                          height=280, showlegend=False,
                          title="Score de Adequação Climática por Mês (%)")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("**Fases Fenológicas e Exigências**")
        fase_df = pd.DataFrame(cult["fases"])
        fase_df.columns = ["Fase", "Dias", "GDD (°C·d)", "Chuva (mm)", "Rad. (MJ/m²)"]
        st.dataframe(fase_df, use_container_width=True, hide_index=True)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        fig2 = go.Figure()
        gdd_vals = [gdd_por_mes.get(i+1, 0) for i in range(12)]
        fig2.add_trace(go.Bar(x=MESES, y=gdd_vals,
            marker_color=["rgba(74,222,128,0.8)" if v > 15 else "rgba(74,222,128,0.35)"
                          for v in gdd_vals]))
        fig2.update_layout(**PLOTLY_LAYOUT, title="GDD Médio Diário por Mês",
                           yaxis_title="°C·dia/dia", height=230, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=MESES,
            y=[precip_por_mes.get(i+1, 0) for i in range(12)],
            marker_color='rgba(96,165,250,0.65)'))
        fig3.update_layout(**PLOTLY_LAYOUT, title="Precipitação Média Diária por Mês",
                           yaxis_title="mm/dia", height=230, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# PAINEL 6: DADOS BRUTOS
# ═══════════════════════════════════════════════════════════════
elif painel == "📋 Dados Brutos":
    st.title("📋 Dados Brutos")

    dias_tabela = st.select_slider(
        "Exibir últimos",
        options=[30, 60, 90, 180, 365, 0],
        value=30,
        format_func=lambda x: "Todos" if x == 0 else f"{x} dias"
    )
    d = filtrar_periodo(dias_tabela)

    cols_show = ['Data', 'Temp. Média', 'Temp. Máx.', 'Temp. Mín.',
                 'Precipitação', 'Rad. Solar', 'Evapotranspiração',
                 'Umidade Rel.', 'GDD', 'GDD_acum']
    show_df = d[cols_show].sort_values('Data', ascending=False).copy()
    show_df['Data'] = show_df['Data'].dt.strftime('%d/%m/%Y')
    show_df = show_df.rename(columns={
        'Temp. Média':'Tméd (°C)', 'Temp. Máx.':'Tmax (°C)', 'Temp. Mín.':'Tmin (°C)',
        'Precipitação':'Precip (mm)', 'Rad. Solar':'Rad (W/m²)',
        'Evapotranspiração':'ET (mm)', 'Umidade Rel.':'UR (%)',
        'GDD':'GDD diário', 'GDD_acum':'GDD Acum.'
    })

    st.dataframe(
        show_df.style.format(precision=2),
        use_container_width=True,
        height=500
    )

    csv = d.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Baixar período selecionado (.csv)",
        data=csv,
        file_name=f"IFRO_{d['Data'].min().strftime('%Y%m%d')}_{d['Data'].max().strftime('%Y%m%d')}.csv",
        mime='text/csv'
    )
