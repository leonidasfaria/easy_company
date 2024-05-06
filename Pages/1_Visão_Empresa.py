
#=============================================================================================================
#                                         Instalando bibliotecas necessárias:
#=============================================================================================================
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import re
import pandas as pd
import folium
from haversine import haversine
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon='^', layout='wide')
#=============================================================================================================
#                                         FUNÇÕES [Modularizando]:
#=============================================================================================================
def clean_code (df):
    """ Função com responsabilidade de realizar a limpeza e ajuste dos dados:
    1. apagar dados nulos do tipo NaN
    2. apagar espaços vazios na string de texto
    3. converter strings em números
    4. ajustar o formato da data
    5. apagar strings que acompanha números na coluna horas 

    Input: dataframe
    Output: dataframe
    """
    # Limpando a planilha:
        # Vazios na string:
    df.loc[: , 'Road_traffic_density'] = df.loc[: , 'Road_traffic_density'].str.strip()
    df.loc[: , 'Delivery_person_ID'] = df.loc[: , 'Delivery_person_ID'].str.strip()
    df.loc[: , 'Type_of_vehicle'] = df.loc[: , 'Type_of_vehicle'].str.strip()
    df.loc[: , 'Type_of_order'] = df.loc[: , 'Type_of_order'].str.strip()
    df.loc[: , 'Festival'] = df.loc[: , 'Festival'].str.strip()
    df.loc[: , 'City'] = df.loc[: , 'City'].str.strip()
    df.loc[: , 'ID'] = df.loc[: , 'ID'].str.strip()

        # Dados inúteis - 'NaN'
    n1 = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[n1 , :].copy()
    n2 = df['multiple_deliveries'] != 'NaN '
    df = df.loc[n2 , :].copy()
    n3 = df['Weatherconditions'] != 'conditions NaN'
    df = df.loc[n3 , :].copy()
    n4 = df['City'] != 'NaN'
    df = df.loc[n4 , :].copy()
    n5 = df['Festival'] != 'NaN'
    df = df.loc[n5 , :].copy()

        # Convertendo strings em números:
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)

        # Convertendo strings em data:
    df['Order_Date'] = pd.to_datetime(df['Order_Date'] ,format='%d-%m-%Y')

        # Apagando string que acompanham números:
    df = df.reset_index(drop=True)
    for i in range(len(df)):
        df.loc[i, 'Time_taken(min)'] = int(''.join(re.findall(r'\d+', str(df.loc[i, 'Time_taken(min)']))))

    return df

def order_metric(df):
            
    # Pedidos/Dia
    y = ['Order_Date' , 'ID' ]
    df1 = df.loc[: , y].groupby([ 'Order_Date' ]).count().reset_index()
    df1.columns = ['Order_Date' , 'Qtde Entregas']
    # Criando o gráfico.
    fig = px.bar(df1, x='Order_Date' , y='Qtde Entregas' )
    return fig

def road_traffic_density (df):
    y = ['Road_traffic_density' , 'ID' ]
    df3 = df.loc[: , y].groupby([ 'Road_traffic_density' ]).count().reset_index()
    df3['Perc_Entrg'] = df3['ID']/df3['ID'].sum()
    fig =px.pie(df3 , values='Perc_Entrg' , names='Road_traffic_density')
    return fig

def road_traffic_density_city(df):
    y = ['Road_traffic_density' , 'ID', 'City' ]
    df4 = df.loc[: , y].groupby([ 'Road_traffic_density', 'City' ]).count().reset_index()
    fig = px.scatter(df4 , x='City' , y='Road_traffic_density' , size='ID' , color='Road_traffic_density')
    return fig 

def order_week (df):
    df2 = df.loc[: ,['Order_Date' , 'ID', 'Delivery_person_ID']]
    df2['Semana'] = df['Order_Date'].dt.strftime('%U')
    df2x = df2.loc[: , ['ID' , 'Semana']].groupby('Semana').count().reset_index()
    fig = px.line(df2x, x='Semana', y='ID')
    return fig

def delivery_week (df2):
    g = df2.loc[: , ['ID' , 'Semana'] ].groupby('Semana').count().reset_index()
    h = df2.loc[: , ['Delivery_person_ID', 'Semana'] ].groupby('Semana').nunique().reset_index()
    j = pd.merge(g , h , how='inner')
    j['Entrg_by_MotoBoy'] = j['ID']/j['Delivery_person_ID']
    fig = px.line(j , x='Semana' , y='Entrg_by_MotoBoy')
    return fig
#=============================================================================================================
#                                         ESTRUTURA DO CÓDIGO
#=============================================================================================================
# Acessando a planilha de dados (direto na máquina):
planilha = pd.read_csv('dataset/train.csv')
df = clean_code(planilha.copy())

#-------------------------------------------------------------------------------------------------------------
#                                         BARRA LATERAL
#-------------------------------------------------------------------------------------------------------------
#image_path = r'C:\Users\leoni\.vscode\repos\FTC\easy.png'
image = Image.open('easy.png')
st.sidebar.image(image, width=300)

st.sidebar.markdown('# Easy Company Transport')
st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect('Escolha as condições de trânsito', ['Low' , 'Medium' , 'High' , 'Jam'], default='Low')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione data limite:')
date_slider = st.sidebar.slider('Até qual data?', value=datetime(2022, 4, 13), min_value=datetime(2022, 2, 11), max_value=datetime(2022, 4, 6), format='DD-MM-YYYY')
st.sidebar.markdown("""___""")

# Converter a data do slider para string
date_slider_str = date_slider.strftime("%Y-%m-%d")

# Filtrar e exibir os dados
select_line = df['Order_Date'] < date_slider_str

df = df.loc[select_line, :]

select_line = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[select_line, :]

#-------------------------------------------------------------------------------------------------------------
#                                         BPÁGINAS
#-------------------------------------------------------------------------------------------------------------

tab1, tab2, tab3 = st.tabs(['VISÃO EMPRESA' , 'VISÃO ENTREGADORES' ,  'VISÃO CLIENTES'])
with tab1:
    with st.container():
        fig = order_metric(df)
        st.markdown('Pedidos/Dia')
        st.plotly_chart(fig, use_container_width=True)
     
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('Pedidos/Tráfego')
            fig = road_traffic_density (df)
            st.plotly_chart(fig, use_container_width=True)
                
        with col2:
            fig = road_traffic_density_city (df)
            st.markdown('Pedidos/Cidade & Tráfego')
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        fig = order_week (df)
        st.markdown('Pedidos/Semana')
        st.plotly_chart(fig, use_container_width=True )
    
    with st.container():
        df2 = df.loc[: ,['Order_Date' , 'ID', 'Delivery_person_ID']]
        df2['Semana'] = df['Order_Date'].dt.strftime('%U')
        fig = delivery_week (df2)
        st.markdown('Entregadores/Semana')        
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    with st.container():
        st.markdown('Ponto Central Cidade/Tráfego')
        p = df.loc[: , ['City' , 'Road_traffic_density' , 'Delivery_location_latitude' , 'Delivery_location_longitude' ]].groupby(['City' , 'Road_traffic_density']).median().reset_index()
        map = folium.Map()
        #Percorrendo a tabela para inserir alfinetes dos locais:
        for index, location_info in p.iterrows():
            folium.Marker([location_info['Delivery_location_latitude'] , location_info['Delivery_location_longitude']] , popup=location_info[['City' , 'Road_traffic_density']]).add_to(map)
        folium_static(map, width=1024, height=600)



