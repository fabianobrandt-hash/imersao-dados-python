import streamlit as st
import pandas as pd
import plotly as go

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Salários na área de Dados",
    page_icon=":bar_chart:",
    layout="wide"
)

# Carregamento dos dados (URL corrigida)
url = "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
df = pd.read_csv(url)

# Barra lateral - Filtros
st.sidebar.header("Filtros")

anos_disponiveis = sorted(df['ano'].unique())
ano_selecionados = st.sidebar.multiselect("Ano:", anos_disponiveis, default=anos_disponiveis)

senioridade_disponiveis = sorted(df['senioridade'].unique())
senioridade_selecionada = st.sidebar.multiselect("Senioridade:", senioridade_disponiveis, default=senioridade_disponiveis)

contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de contrato:", contratos_disponiveis, default=contratos_disponiveis)

tamanho_empresa_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanho_empresa_selecionados = st.sidebar.multiselect("Tamanho da empresa:", tamanho_empresa_disponiveis, default=tamanho_empresa_disponiveis)

# Filtragem do DataFrame
df_filtrado = df[
    (df['ano'].isin(ano_selecionados)) &
    (df['senioridade'].isin(senioridade_selecionada)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanho_empresa_selecionados))
]

# Título
st.title("Dashboard de Salários na área de Dados")
st.markdown("Análise de salários na área de Dados com base em dados reais coletados de profissionais da área.")

# KPIs
st.subheader("Métricas Gerais (Salário Anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0] if not df_filtrado['cargo'].mode().empty else "N/A"
else:
    salario_medio = 0
    salario_maximo = 0
    total_registros = 0
    cargo_mais_frequente = "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Médio", f"${salario_medio:,.0f}")
col2.metric("Salário Máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de Registros", f"{total_registros:,}")
col4.metric("Cargo Mais Frequente", cargo_mais_frequente)

st.markdown("---")

# Gráficos com tema escuro
st.subheader("Gráficos de Análise")
col_graf1, col_graf2 = st.columns(2)

# Gráfico 1: Top 10 cargos
with col_graf1:
    if not df_filtrado.empty:
        top_cargos = (
            df_filtrado.groupby('cargo')['usd'].mean()
            .nlargest(10)
            .sort_values(ascending=True)
            .reset_index()
        )
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=top_cargos['cargo'],
            x=top_cargos['usd'],
            orientation='h',
            marker_color='#00B8D9',  # Azul claro para destaque
            text=top_cargos['usd'],
            texttemplate='%{text:.0f}',
            textposition='auto',
            hovertemplate="Cargo: %{y}<br>Salário Médio: $%{x:,.0f}<extra></extra>"
        ))
        fig.update_layout(
            title="Top 10 Cargos com Maior Salário Médio Anual (USD)",
            xaxis=dict(title="Salário Médio (USD)", color="#B0B0B0", showgrid=True, gridcolor='gray'),
            yaxis=dict(title=None, color="#B0B0B0"),
            title_font_size=16,
            title_y=0.9,
            margin=dict(l=50, r=50, t=80, b=50),
            paper_bgcolor="#111111",  # Fundo do gráfico
            plot_bgcolor="#1E1E1E",   # Fundo da área de plotagem
            font=dict(color="#FFFFFF"),  # Texto branco
            hovermode="y unified"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de cargos.")

# Gráfico 2: Histograma
with col_graf2:
    if not df_filtrado.empty:
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=df_filtrado['usd'],
            nbinsx=30,
            marker_color="#00C853",
            name="Salários",
            hovertemplate="Salário: $%{x:,.0f}<br>Contagem: %{y}<extra></extra>"
        ))
        fig.update_layout(
            title="Distribuição dos Salários Anuais (USD)",
            xaxis=dict(title="Salário Anual (USD)", color="#B0B0B0", gridcolor='gray'),
            yaxis=dict(title="Número de Registros", color="#B0B0B0"),
            title_y=0.9,
            showlegend=False,
            margin=dict(l=50, r=50, t=80, b=50),
            paper_bgcolor="#111111",
            plot_bgcolor="#1E1E1E",
            font=dict(color="#FFFFFF")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de distribuição.")

# Linha 2 de gráficos
col_graf3, col_graf4 = st.columns(2)

# Gráfico 3: Pizza - Remoto
with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'Quantidade']
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=remoto_contagem['tipo_trabalho'],
            values=remoto_contagem['Quantidade'],
            hole=0.4,
            textinfo='percent+label',
            textposition='inside',
            marker=dict(colors=['#00B8D9', '#FF4081']),
            hovertemplate="%{label}: %{value} profissionais<extra></extra>"
        ))
        fig.update_layout(
            title="Proporção de Trabalho Remoto vs Presencial",
            title_x=0.5,
            legend_title_text="Tipo de Trabalho",
            margin=dict(t=80, b=20),
            paper_bgcolor="#111111",
            font=dict(color="#FFFFFF")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de tipos de trabalho.")

# Gráfico 4: Mapa coroplético
with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        if not df_ds.empty:
            media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
            fig = go.Figure(
                go.Choropleth(
                    locations=media_ds_pais['residencia_iso3'],
                    z=media_ds_pais['usd'],
                    colorscale='Earth',  # Tema terroso, funciona bem no escuro
                    autocolorscale=False,
                    reversescale=False,
                    marker_line_color='darkgray',
                    marker_line_width=0.5,
                    colorbar=dict(
                        title="Salário Médio (USD)",
                        tickfont_color="#B0B0B0",
                        titlefont_color="#FFFFFF"
                    ),
                    hovertemplate="País: %{location}<br>Salário Médio: $%{z:,.0f}<extra></extra>"
                )
            )
            fig.update_layout(
                title="Salário Médio Anual de Data Scientists por País (USD)",
                title_x=0.5,
                geo=dict(
                    showframe=False,
                    showcoastlines=True,
                    coastlinecolor='gray',
                    projection_type='natural earth',
                    bgcolor='rgba(0,0,0,0)'
                ),
                margin=dict(t=80, l=20, r=20, b=20),
                paper_bgcolor="#111111",
                font=dict(color="#FFFFFF")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nenhum registro de 'Data Scientist' encontrado.")
    else:
        st.warning("Nenhum dado disponível para exibir o mapa de salários.")

# Tabela
st.subheader("Tabela de Dados Filtrados")
if not df_filtrado.empty:
    st.dataframe(df_filtrado, use_container_width=True)
else:
    st.write("Nenhum dado corresponde aos filtros selecionados.")

