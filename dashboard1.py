import streamlit as st
import pandas as pd
import plotly.express as px

# Link da planilha no Google Sheets (exemplo)
sheet_url = "https://docs.google.com/spreadsheets/d/11kY8TYVY1qY0wQP4smjoSfYXDN3s6S0y8h2PyxAyPCk/pub?output=csv"

# Carregar os dados do Google Sheets usando pandas
df = pd.read_csv(sheet_url)

# Limpando espaços em branco nos nomes das colunas (se necessário)
df.columns = df.columns.str.strip()

# Definir a variável com o número total de produtos únicos
numero_total_produtos = df['produto'].nunique()

# Função para ajustar o estilo dos cartões com CSS
def set_css_style():
    st.markdown("""
        <style>
        .card {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            font-size: 14px;
            width: 180px;
            margin-bottom: 10px;
            margin-left: 10px;
            color: black; /* Garante que o texto dentro dos cartões seja preto */
        }
        .card-title {
            font-size: 16px;
            font-weight: bold;
            color: black; /* Garante que o título seja preto */
        }
        .big-font {
            font-size: 30px !important;
            color: black !important; /* Garante que o texto grande seja preto */
        }
        </style>
        """, unsafe_allow_html=True)

# Aplicar o CSS
set_css_style()

# Exemplo de cartão com texto estilizado
st.markdown('<p class="big-font">Número de Produtos: {}</p>'.format(numero_total_produtos), unsafe_allow_html=True)

# Título do dashboard
st.title('Dashboard de Frutas e Legumes')

# --- Adicionar cartões no topo esquerdo ---
# Exibir os cartões com CSS aplicado
total_produtos = df['produto'].nunique()
total_frutas = df[df['categoria'] == 'Fruta']['produto'].nunique()
total_legumes = df[df['categoria'] == 'Legume']['produto'].nunique()
total_verduras = df[df['categoria'] == 'Verdura']['produto'].nunique()

# Criando uma coluna para colocar os cartões no canto esquerdo
st.sidebar.markdown("<div class='card'><div class='card-title'>Total de Produtos</div><div>" + str(total_produtos) + "</div></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='card'><div class='card-title'>Frutas</div><div>" + str(total_frutas) + "</div></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='card'><div class='card-title'>Legumes</div><div>" + str(total_legumes) + "</div></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='card'><div class='card-title'>Verduras</div><div>" + str(total_verduras) + "</div></div>", unsafe_allow_html=True)

# --- Restante do dashboard ---
# Layout com duas colunas para os gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader('Dados de Vendas')
    st.dataframe(df)

with col2:
    fig = px.bar(df, x='produto', y='vendas', color='produto', 
                 title="Vendas por produto", labels={'vendas':'Quantidade Vendida'},
                 template='plotly_dark')
    st.plotly_chart(fig)

# Criar um gráfico de pizza (Pie chart) como exemplo adicional
fig_pie = px.pie(df, values='vendas', names='produto', title='Distribuição de Vendas por produto')

# Exibir o gráfico de pizza
st.plotly_chart(fig_pie)

# --- Adicionar mapa interativo ---
# Supondo que você tenha colunas 'Latitude' e 'Longitude' no CSV
st.subheader("Mapa de Localização dos Produtos")

# Verificando se existem colunas de latitude e longitude
if 'latitude' in df.columns and 'longitude' in df.columns:
    # Filtrar apenas valores válidos de latitude e longitude
    df_valid = df[(df['latitude'] >= -90) & (df['latitude'] <= 90) &
                  (df['longitude'] >= -180) & (df['longitude'] <= 180)]
    
    if not df_valid.empty:
        # Criar mapa interativo
        st.map(df_valid[['latitude', 'longitude']])
    else:
        st.write("Os dados de latitude e longitude estão fora dos intervalos válidos.")
else:
    st.write("Os dados de latitude e longitude não estão disponíveis.")
