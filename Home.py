import streamlit as st
from PIL import Image
st.set_page_config(page_title="Home", page_icon=":)")

#image_path ='C:/Users/leoni/.vscode/repos/FTC/'
image = Image.open('easy.png')
st.sidebar.image(image, width=300)
st.sidebar.markdown('# Easy Company Transport')
st.sidebar.markdown("""___""")
st.write("### Easy Company Growth DashBoard ###")
st.markdown("""
            Criado para acompanhar métricas de crescimento dos Entregadores e Restaurantes.

            ### Como utilizar o DashBoard?

            => VISÂO EMPRESA

                => Visão Gerencial: Métricas Gerais
                => Visão Tática: Indicadores Semanais de Crescimento
                => Visão Geográfica: Insights de Geolocalização

            => VISÂO ENTREGADORES

                Acompanhamento dos indicadores semanais de crescimento no número de entregadores
            => VISÃO RESTAURANTES

                Acompanhamento dos indicadores semanais de crescimento na quantidade de pedidos 
            
            ### Ask for Help
                @leonidas_datasciense   
        """)