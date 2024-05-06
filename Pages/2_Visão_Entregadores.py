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

st.set_page_config(page_title='Visão Entregadores', page_icon='%', layout='wide')
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

def top_deliver(df, top_asc):
    r = (df.loc[:,['Delivery_person_ID' , 'City' , 'Time_taken(min)']].groupby(['Delivery_person_ID' , 'City']).min()
                                                                      .sort_values(['City' , 'Time_taken(min)'], ascending=top_asc)
                                                                      .reset_index())
    r1 = r.loc[r['City'] == 'Metropolitian' , :].head(10)
    r2 = r.loc[r['City'] == 'Semi-Urban' , :].head(10)
    r3 = r.loc[r['City'] == 'Urban' , :].head(10)
    r4 = pd.concat([r1 , r2 , r3]).reset_index(drop=True)
    return r4












#=============================================================================================================
#                                         ESTRUTURA DO CÓDIGO
#=============================================================================================================
# Acessando a planilha de dados (direto na máquina):
planilha = pd.read_csv('dataset/train.csv')
df = clean_code(planilha.copy())

#=============================================================================================================
#                                         BARRA LATERAL
#=============================================================================================================

#image_path = r'C:\Users\leoni\.vscode\repos\FTC\easy.png'
image = Image.open('easy.png')
st.sidebar.image(image, width=300)

st.sidebar.markdown('# Easy Company Transports')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione data limite:')
date_slider = st.sidebar.slider('Até qual data?', value=datetime(2022, 4, 13), min_value=datetime(2022, 2, 11), max_value=datetime(2022, 4, 6), format='DD-MM-YYYY')
st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect('Escolha as condições de trânsito', ['Low' , 'Medium' , 'High' , 'Jam'], default='Low')
st.sidebar.markdown("""___""")

weather_options = st.sidebar.multiselect('Escolha as condições de clima', ['conditions Cloudy' , 'conditions Fog' , 'conditions Sandstorms', 'conditions Stormy' , 'conditions Sunny', 'conditions Windy'], default='conditions Sunny')
st.sidebar.markdown("""___""")


# Converter a data do slider para string
date_slider_str = date_slider.strftime("%Y-%m-%d")

# Filtrar e exibir os dados
select_line = df['Order_Date'] < date_slider_str

df = df.loc[select_line, :]


select_line = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[select_line, :]

select_line = df['Weatherconditions'].isin(weather_options)
df = df.loc[select_line, :]

#=============================================================================================================
#                                        PÁGINAS
#=============================================================================================================
tab1, tab2, tab3 = st.tabs(['VISÃO ENTREGADORES' , '_' ,  '_'])
with tab1:
    with st.container():
        st.title('Métricas Gerais')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
           # A maior idade:
            b = df.loc[: , 'Delivery_person_Age'].max()
            col1.metric('Maior Idade', b)
        with col2:
            # A Menor Idade
            c = df.loc[: , 'Delivery_person_Age'].min()
            col2.metric('Menor Idade' , c)
        with col3:
            # A Melhor condição de Veículo
            b = df.loc[: , 'Vehicle_condition'].max()
            col3.metric('Melhor Condição' , b)
        with col4:
            # A pior condição de Veículo
            c = df.loc[: , 'Vehicle_condition'].min()
            col4.metric('Pior Condição', c)
        
    with st.container():
        st.markdown("""___""")
        st.title('Avaliações de Entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação Média/Entregador')
            d = df.loc[: , ['Delivery_person_ID' , 'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(d)
        with col2:
            st.markdown('##### Avaliação Média/Trânsito')
            f = df.loc[: , ['Road_traffic_density' , 'Delivery_person_Ratings']].groupby('Road_traffic_density').agg( {'Delivery_person_Ratings' : ['std' , 'mean']} )
            f.columns = ['delivery_std' , 'delivery_mean']
            f = f.reset_index()
            st.dataframe(f)

            st.markdown('##### Avaliação Média/CLima')
            k = df.loc[: , ['Weatherconditions' , 'Delivery_person_Ratings']].groupby('Weatherconditions').agg( {'Delivery_person_Ratings' : ['std' , 'mean']} )
            k.columns = ['delivery_std' , 'delivery_mean']
            k = k.reset_index()
            st.dataframe(k)
        
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Entregadores - Top Rápidos')
            r4 = top_deliver(df, top_asc=True)
            st.dataframe(r4)

        with col2:
            st.markdown('##### Entregadores - Top Lentos')
            r4 = top_deliver(df, top_asc=False)
            st.dataframe(r4)
            

            
            
