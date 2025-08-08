import streamlit as st
import pandas as pd
import plotly.express as px


# Configuração da página
st.set_page_config(
    page_title="Dashboard de Salários na área de Dados",
    page_icon=":bar_chart:",
    layout="wide"
)

# Carregamento dos dados (URL corrigida - sem espaço no final)
url = "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
df = pd.read_csv(url)

# Barra lateral - Filtros
st.sidebar.header("Filtros")

# Filtro de ano
anos_disponiveis = sorted(df['ano'].unique())
ano_selecionados = st.sidebar.multiselect("Ano:", anos_disponiveis, default=anos_disponiveis)

# Filtro de senioridade (corrigido o nome da variável)
senioridade_disponiveis = sorted(df['senioridade'].unique())
senioridade_selecionada = st.sidebar.multiselect("Senioridade:", senioridade_disponiveis, default=senioridade_disponiveis)

# Filtro por tipo de contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de contrato:", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por tamanho da empresa
tamanho_empresa_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanho_empresa_selecionados = st.sidebar.multiselect("Tamanho da empresa:", tamanho_empresa_disponiveis, default=tamanho_empresa_disponiveis)

# Filtragem do DataFrame
df_filtrado = df[
    (df['ano'].isin(ano_selecionados)) &
    (df['senioridade'].isin(senioridade_selecionada)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanho_empresa_selecionados))
]

# Conteúdo principal
st.title("Dashboard de Salários na área de Dados")
st.markdown("Análise de salários na área de Dados com base em dados reais coletados de profissionais da área.")

# Métricas principais (KPIs)
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

# Exibir KPIs (sempre visíveis)
col1, col2, col3, col4 = st.columns(4)

col1.metric("Salário Médio", f"${salario_medio:,.0f}")
col2.metric("Salário Máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de Registros", f"{total_registros:,}")
col4.metric("Cargo Mais Frequente", cargo_mais_frequente)

st.markdown("---")

# Análises visuais com Plotly
st.subheader("Gráficos de Análise")
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = (
            df_filtrado.groupby('cargo')['usd'].mean()
            .nlargest(10)
            .sort_values(ascending=True)
            .reset_index()
        )
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title='Top 10 Cargos com Maior Salário Médio Anual (USD)',
            labels={'usd': 'Salário Médio Anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(
            title_y=0.9,
            xaxis_title="Salário Médio Anual (USD)",
            yaxis_title=None
        )
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title='Distribuição dos Salários Anuais (USD)',
            labels={'usd': 'Salário Anual (USD)', 'count': 'Número de Registros'}
        )
        grafico_hist.update_layout(
            title_y=0.9,
            xaxis_title="Salário Anual (USD)",
            yaxis_title="Número de Registros"
        )
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de distribuição de salários.")

col_graf3, col_graf4 = st.columns(2)

# Gráfico 3: Proporção de trabalho remoto
with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'Quantidade']  # Corrigido: 'Quatidade' → 'Quantidade'

        grafico_remoto = px.pie(
            remoto_contagem,
            values='Quantidade',
            names='tipo_trabalho',
            title='Proporção dos Tipos de Trabalho (Remoto/Presencial)',
            hole=0.4
        )
        grafico_remoto.update_traces(textposition='inside', textinfo='percent+label')
        grafico_remoto.update_layout(
            title_x=0.5,
            legend_title_text='Tipo de Trabalho'
        )
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de tipos de trabalho.")

# Gráfico 4: Salário médio de Data Scientists por país (mapa coroplético)
with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        if not df_ds.empty:
            media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
            grafico_paises = px.choropleth(
                media_ds_pais,
                locations='residencia_iso3',
                color='usd',
                title='Salário Médio Anual de Data Scientists por País (USD)',
                color_continuous_scale='RdYlGn',  # Corrigido: string do colormap
                labels={'usd': 'Salário Médio Anual (USD)', 'residencia_iso3': 'País'}
            )
            grafico_paises.update_layout(title_x=0.5)
            st.plotly_chart(grafico_paises, use_container_width=True)
        else:
            st.warning("Nenhum registro de 'Data Scientist' encontrado.")
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de distribuição por país.")

#Tabela de dados filtrados
st.subheader("Tabela de Dados Filtrados")       
st.dataframe(df_filtrado, use_container_width=True)
