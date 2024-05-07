#=============================================================================================================
#                                         Instalando bibliotecas necessárias:
#=============================================================================================================
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import re
import pandas as pd
import folium
import numpy as np
from haversine import haversine
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Restaurantes', page_icon='^-', layout='wide')
#=============================================================================================================
#                                         FUNÇÕES [Modularizando]:
#=============================================================================================================

def distance_map(df):
    vigas = ['Restaurant_latitude' , 'Restaurant_longitude' , 'Delivery_location_latitude' , 'Delivery_location_longitude']
    df['km_point'] = df.loc[: , vigas].apply(lambda x: haversine((x['Restaurant_latitude'] , x['Restaurant_longitude']) , (x['Delivery_location_latitude'] , x['Delivery_location_longitude'])) , axis=1)
    df['km_point'] = df['km_point'].astype(int)
    avg_distance = df.loc[:, ['City', 'km_point']].groupby('City').mean().reset_index()
    fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['km_point'], pull=[0, 0.1, 0])])
    fig.update_layout(width=500, height=350)
    return fig

def avg_std_time_on_traffic(df):
    f = (df.loc[: , ['City' , 'Time_taken(min)' , 'Road_traffic_density']]
           .groupby(['City' , 'Road_traffic_density'])
           .agg({'Time_taken(min)' : ['mean' , 'std']}))
    f.columns = ['avg_time' , 'std_time']
    f = f.reset_index()
                        
    fig = px.sunburst(f, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(f['std_time']))
    fig.update_layout(width=500, height=350)
    return fig

def avg_std_graph(df):
    viga = ['City' , 'Time_taken(min)']
    f = df.loc[: , viga].groupby('City').agg({'Time_taken(min)' : ['mean' , 'std']})
    f.columns = ['avg_time' , 'std_time']
    f = f.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=f['City'], y=f['avg_time'], error_y=dict(type='data', array=f['std_time'])))
    fig.layout.update(barmode='group')
    return fig
        

def avg_std_time(df, festival, op):
    """
    Esta função calcula tempo médio e desvio padrão das entregas.
    Input:
    -df: dataframe com dados necessários
    -op: tipo de operação => média(avg) ou desvio padrão (std)
    Output:
    Dataframe com duas colunas e uma linha
    """
    f = df.loc[: , ['Festival' , 'Time_taken(min)']].groupby('Festival').agg({'Time_taken(min)' : ['mean' , 'std']})
    f.columns = ['avg_time' , 'std_time']
    f = f.reset_index()
    f = np.round(f.loc[f['Festival'] == festival , op], 2)
    return f

def distance(df):
    vigas = ['Restaurant_latitude' , 'Restaurant_longitude' , 'Delivery_location_latitude' , 'Delivery_location_longitude']
    df['km_point'] = df.loc[: , vigas].apply(lambda x: haversine((x['Restaurant_latitude'] , x['Restaurant_longitude']) , (x['Delivery_location_latitude'] , x['Delivery_location_longitude'])) , axis=1)
    df['km_point'] = df['km_point'].astype(int)
    avg = np.round(df['km_point'].mean(),2)
    return avg
            

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
tab1, tab2, tab3 = st.tabs(['Visão Entregadores', '_', '_'])
with tab1:
    with st.container():
        st.markdown('##### Métricas Gerais')
        col1, col2, col3, col4, col5, col6  = st.columns(6)
        with col1:
            x = len(df.loc[: , 'Delivery_person_ID'].unique())
            col1.metric('Entregadores Únicos', x)

        with col2:
            avg = distance(df)
            col2.metric('Distância Média', avg)
                 
        with col3:
            f = avg_std_time(df, 'Yes', 'avg_time')
            col3.metric('Avg_Time Entrega: Festival', f)

        #col4, col5, col6 = st.columns(3)
        with col4:
            f = avg_std_time(df, 'Yes', 'std_time')
            col4.metric('Std_Time Entrega: Festival', f)

        with col5:
            f = avg_std_time(df, 'No', 'avg_time')
            col5.metric('Avg_Time Entrega: NO-Festival', f)
        with col6:
            f = avg_std_time(df, 'No', 'std_time')
            col6.metric('Std_Time Entrega: NO-Festival', f)

    with st.container():
        st.markdown("""___""")
        st.markdown('##### Distribuição Tempo')

        fig = avg_std_graph(df)
        st.plotly_chart(fig)

    with st.container():
        st.markdown("""___""")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Tempo/Cidades')
            fig = avg_std_time_on_traffic(df)
            st.plotly_chart(fig)

        with col2:
            st.markdown('##### Distâncias/Cidades')
            fig = distance_map(df)
            st.plotly_chart(fig)

    with st.container():
        st.markdown("""___""")
        st.markdown('##### Entrega/Pedido/Cidade')
        viga = ['City' , 'Time_taken(min)' , 'Type_of_order']
        f = df.loc[: , viga].groupby(['City' , 'Type_of_order']).agg({'Time_taken(min)' : ['mean' , 'std']})
        f.columns = ['avg_time' , 'std_time']
        f = f.reset_index()
        st.dataframe(f, use_container_width=True)
        