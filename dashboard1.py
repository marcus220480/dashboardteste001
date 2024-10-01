import streamlit as st
import pandas as pd
import plotly.express as px

# Configurar o layout da página como wide (mais amplo)
st.set_page_config(page_title="Dashboard de Produtos e Vendas", layout="wide")

# Links das planilhas no Google Sheets
sheet_url_produtos = "https://docs.google.com/spreadsheets/d/11kY8TYVY1qY0wQP4smjoSfYXDN3s6S0y8h2PyxAyPCk/pub?output=csv"
sheet_url_vendas = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTkWFrz89PS9bCsPIN5uXk17FoJCixJUfMlQ-GUwlJKsFRZQ7sSsxhClXP1nYMZbTx6SxG-7CQWGbqB/pub?output=csv"

# Carregar os dados do Google Sheets usando pandas
df_produtos = pd.read_csv(sheet_url_produtos)
df_vendas = pd.read_csv(sheet_url_vendas)

# Limpando espaços em branco nos nomes das colunas (se necessário)
df_produtos.columns = df_produtos.columns.str.strip()
df_vendas.columns = df_vendas.columns.str.strip()

# Converter as colunas 'vendas' e 'lucro' para tipo float (números), se necessário
df_vendas['vendas'] = pd.to_numeric(df_vendas['vendas'], errors='coerce')
df_vendas['lucro'] = pd.to_numeric(df_vendas['lucro'], errors='coerce')

# --- Filtros ---
# Filtro de período (trimestre, semestre, anual)
periodo_selecionado = st.selectbox("Selecione o período", ["Trimestre", "Semestre", "Anual"])

# Filtro de data (dia, mês, ano)
data_inicio = st.date_input("Selecione a data de início")
data_fim = st.date_input("Selecione a data de fim")

# Filtro por estado
estados_selecionados = st.multiselect("Selecione o(s) estado(s)", df_vendas['estado'].unique())

# Filtrando o dataframe de vendas com base nos filtros aplicados e criando uma cópia
df_vendas['data'] = pd.to_datetime(df_vendas['data'], format='%d/%m/%Y')
df_vendas_filtrado = df_vendas.loc[(df_vendas['data'] >= pd.to_datetime(data_inicio)) & 
                                   (df_vendas['data'] <= pd.to_datetime(data_fim))].copy()

if estados_selecionados:
    df_vendas_filtrado = df_vendas_filtrado.loc[df_vendas_filtrado['estado'].isin(estados_selecionados)].copy()

# Total de produtos, vendas e lucro filtrados
total_produtos = df_produtos['produto'].nunique()
total_vendas = df_vendas_filtrado['vendas'].sum()
total_lucro = df_vendas_filtrado['lucro'].sum()
vendas_por_estado = df_vendas_filtrado.groupby('estado')['vendas'].sum()

# Função para formatar valores monetários
def formatar_monetario(valor):
    return f'R$ {valor:,.2f}'.replace(",", "v").replace(".", ",").replace("v", ".")

# Estilos de CSS para cartões
def set_css_style():
    st.markdown("""
        <style>
        .card-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
        }
        .card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            font-size: 14px;
            width: 22%;
            text-align: center;
            height: 120px; /* Altura fixa para padronizar */
        }
        .card-title {
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }
        .big-font {
            font-size: 36px !important;
            color: #2c3e50 !important;
        }
        </style>
        """, unsafe_allow_html=True)

set_css_style()

# Título do dashboard
st.title('Dashboard de Produtos e Vendas')

# --- Distribuição Widescreen ---
st.markdown("### Indicadores Gerais")

# Criar a linha de cartões com alinhamento no topo e tamanho padronizado
st.markdown("""
    <div class='card-container'>
        <div class='card'>
            <div class='card-title'>Total de Produtos</div>
            <div class='big-font'>{}</div>
        </div>
        <div class='card'>
            <div class='card-title'>Total de Vendas</div>
            <div class='big-font'>{}</div>
        </div>
        <div class='card'>
            <div class='card-title'>Lucro Total</div>
            <div class='big-font'>{}</div>
        </div>
        <div class='card'>
            <div class='card-title'>Estados com Vendas</div>
            <div class='big-font'>{}</div>
        </div>
    </div>
""".format(total_produtos, formatar_monetario(total_vendas), formatar_monetario(total_lucro), len(vendas_por_estado)), unsafe_allow_html=True)

# --- Gráficos ---
st.markdown("### Análises de Vendas e Produtos")

# Gráfico de barras por estado
grafico_col1, grafico_col2 = st.columns(2)

# Agrupar as vendas por estado e por mês
df_vendas_filtrado['mes'] = df_vendas_filtrado['data'].dt.to_period('M')  # Cria uma coluna de período por mês
df_vendas_agrupado = df_vendas_filtrado.groupby(['mes', 'estado'])['vendas'].sum().reset_index()

# Converter a coluna 'mes' para string para evitar problemas de serialização
df_vendas_agrupado['mes'] = df_vendas_agrupado['mes'].astype(str)

# Gráfico de barras mostrando vendas por estado (agora agrupado por mês)
with grafico_col1:
    fig_bar_estado = px.bar(df_vendas_agrupado, x='mes', y='vendas', color='estado', 
                            title='Vendas por Estado (Agrupado por Mês)',
                            labels={'vendas':'Vendas', 'mes':'Mês'},
                            template='plotly_white')
    fig_bar_estado.update_layout(height=400)
    st.plotly_chart(fig_bar_estado)

# Gráfico de linha para evolução de vendas por mês
with grafico_col2:
    fig_line = px.line(df_vendas_agrupado, x='mes', y='vendas', 
                       title='Evolução de Vendas (Geral por Mês)',
                       labels={'vendas':'Vendas', 'mes':'Mês'},
                       template='plotly_white',
                       markers=True)  # Adicionar marcadores nos pontos
    
    # Adicionar anotação com os valores diretamente nas linhas
    fig_line.update_traces(text=df_vendas_agrupado['vendas'].apply(lambda x: f'R${x:,.2f}'),
                           textposition="top right",
                           mode='lines+markers+text')  # Combina linhas, marcadores e texto
    
    fig_line.update_layout(height=400)
    st.plotly_chart(fig_line)

# --- Mapa Interativo e Top 10 Produtos Mais Vendidos ---
st.markdown("### Mapa de Vendas e Top 10 Produtos Mais Vendidos")

# Total de vendas por estado (para o cálculo das porcentagens)
vendas_por_estado = df_vendas_filtrado.groupby('estado')['vendas'].sum().reset_index()

# Normalizar os dados para exibir as esferas no mapa (tamanhos proporcionais)
vendas_por_estado['percentual'] = 100 * (vendas_por_estado['vendas'] / vendas_por_estado['vendas'].sum())

# Adicionar a coluna de latitude e longitude dos estados (Exemplo: fictício)
df_loc = pd.DataFrame({
    'estado': ['SP', 'RJ', 'MG', 'RS'],
    'latitude': [-23.5505, -22.9068, -19.9167, -30.0346],
    'longitude': [-46.6333, -43.1729, -43.9345, -51.2177]
})
df_vendas_loc = pd.merge(vendas_por_estado, df_loc, how='left', on='estado')

# Gráfico Mapa Interativo (Esferas proporcionais por estado)
with grafico_col1:
    if 'latitude' in df_vendas_loc.columns and 'longitude' in df_vendas_loc.columns:
        fig_mapa = px.scatter_mapbox(df_vendas_loc, lat="latitude", lon="longitude", 
                                     size="percentual", hover_name="estado", 
                                     hover_data={"percentual": ':.2f', 'vendas': True},
                                     zoom=3, title="Mapa Proporcional das Vendas por Estado")
        fig_mapa.update_layout(mapbox_style="open-street-map")
        fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_mapa)
    else:
        st.error("Dados de latitude e longitude estão faltando para alguns estados.")

# Top 10 produtos mais vendidos
with grafico_col2:
    st.markdown("#### Top 10 Produtos Mais Vendidos")
    top_10_produtos = df_vendas_filtrado.groupby('produto')['vendas'].sum().nlargest(10).reset_index()
    st.table(top_10_produtos)