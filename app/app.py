import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import re

st.set_page_config(page_title='FieldGuide', page_icon='📚', layout='centered', initial_sidebar_state='auto')

st.sidebar.header("Bem-vindo ao FieldGuide!")
st.sidebar.image("https://i.imgur.com/mlvt8or.png", use_column_width=True)
st.sidebar.write("### Selecione a página desejada:")
page = st.sidebar.selectbox("", ["Introdução (TP1)","Dados", "BeautifulSoup",])

@st.cache_data
def read_csv(file):
    data = pd.read_csv(file, sep=';')
    return data

if page == "Introdução (TP1)":
    st.image("https://i.imgur.com/9SCBoG5.png", width=650)
    st.markdown("# Field Guide")
    st.markdown("## O Guia de Campo para sua Carreira")

    st.write("")

    st.write("Aplicação que acumula todas as informações para te ajudar a planejar sua vida profissional, mostrando cargos, habilidades necessárias para exercê-los e cursos superiores.")
    st.write("Este projeto procura ajudar principalmente alunos do Ensino Médio, que assim como eu, estavam confusos com seu futuro e ficaram dias procurando informações sobre suas possíveis carreiras futuras.")
    st.write("Nele você entra e pesquisa por uma proffisão e encontra tudo que você pode precisar para trabalhar na área.")

    st.image(r"Projeto_Bloco_Ciência_Dados_Aplicada\app\data\Beige Modern Chic Business Model Canvas Brainstorm.png")
    st.image(r"Projeto_Bloco_Ciência_Dados_Aplicada\app\data\Project Charter - Projeto Bloco Ciência de Dados Aplicada-1.png")

    st.markdown("### Links:")
    st.markdown("#### Inspiração Principal")
    st.write("[Mapa de Carreiras](https://www.vagas.com.br/mapa-de-carreiras/)")
    st.markdown("#### Possíveis Fontes de Dados")
    st.write("[API Feed de Vagas](https://apifeeddevagas.docs.apiary.io/#reference/0/feed-de-vagas/feed-de-vagas)")
    st.write("[Cadastro Nacional de Cursos Superiores](https://emec.mec.gov.br/emec/nova)")
    st.write("[API Profissões](https://api.sienge.com.br/docs/html-files/professions-v1.html#/)")
    st.write("[Tabela de Pontos Sisu](https://www.guiadacarreira.com.br/blog/tabela-de-pontos-do-enem-para-cada-curso)")
    st.write("[Catho](https://www.catho.com.br/vagas/)")

    file = (r'Projeto_Bloco_Ciência_Dados_Aplicada\app\data\relatorio_consulta_publica_avancada_curso_25_08_2024_00_05_33.csv')
    data = read_csv(file)

    st.markdown("### Exemplo de tabela de dados:")
    st.write("O exemplo a seguir utiliza uma tabela vinda do site citado acima (Cadastro Nacional de Cursos Superiores), ela mostra apenas cursos de 'Dados' e os dados não foram tratados, portanto há diversas colunas que não serão utilizadas no projeto final. Eu pretendo ampliar estes dados para todo o Brasil e utilizar APIs, porém ainda não consegui fazer funcionar mas estou trabalhando em me capacitar para tal.")
    dataframe = st.dataframe(data)

if page == "Dados":
    st.title("Dados Relatório Consulta Pública Avançada Curso")
    file = (r'Projeto_Bloco_Ciência_Dados_Aplicada\app\data\relatorio_consulta_publica_avancada_curso_25_08_2024_00_05_33.csv')
    data = read_csv(file)
    dataframe = st.dataframe(data)
    if 'complete' not in st.session_state:
        st.session_state['complete'] = dataframe
    st.download_button(
        label="Baixar dados completos",
        data=data.to_csv(index=False).encode('utf-8'),
        file_name='dados_completos.csv',
        mime='text/csv'
    )
    cols = list(data.columns)
    colunas = st.multiselect("Mostrar colunas", cols)
    if colunas:
        display = data[colunas]
        if 'multi' not in st.session_state:
            st.session_state['multi'] = display
        st.write(display)
        st.download_button(
            label="Baixar dados",
            data=display.to_csv(index=False).encode('utf-8'),
            file_name='dados.csv',
            mime='text/csv'
        )

    uploaded_file = st.file_uploader("Escolha um arquivo", type=["csv", "xlsx", "json"])
    if uploaded_file is not None:
        file_type = uploaded_file.name.split('.')[-1]
        if file_type == 'csv':
            data_u = pd.read_csv(uploaded_file)
        elif file_type == 'xlsx':
            data_u = pd.read_excel(uploaded_file)
        elif file_type == 'json':
            data_u = pd.read_json(uploaded_file)
        else:
            st.error("Tipo de arquivo não suportado!")
            data_u = None
        
        if data_u is not None:
            st.dataframe(data_u)
            st.download_button(
                label="Baixar dados Upload",
                data=data_u.to_csv(index=False).encode('utf-8'),
                file_name='uploaded.csv',
                mime='text/csv'
            )
            if 'uploaded' not in st.session_state:
                st.session_state['uploaded'] = data_u

if page == "BeautifulSoup":
    st.title("Aqui você pode encontrar todas as profissões disponíveis no site Quero Bolsa, organizadas por letra.")
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }
    resp = requests.get("https://querobolsa.com.br/carreiras-e-profissoes/todas", headers=HEADER, timeout=30)
    soup = bs(resp.content, 'html.parser')
    profissoes = soup.find_all('a', class_='z-link')
    profs = []
    for profissao in profissoes:
        profs.append(profissao.text)

    profs_at = profs[50:955]
    profs_at = [prof.strip().replace('\n', '') for prof in profs_at]
    for element in profs_at:
        if element == '':
            profs_at.remove(element)
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    
    sel_let = st.selectbox("Profissões por letra", alphabet)
                   
    st.markdown("---")
    st.markdown("#### (Role para ver todas)")
    st.markdown(
        f"<div style='height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px;'>{''.join([f'<p>{prof}</p>' for prof in profs_at if prof[0] == sel_let])}</div>",
        unsafe_allow_html=True
    )
    st.download_button(
        label="Baixar profissões",
        data='\n'.join(profs_at).encode('utf-8'),
        file_name='profissões.txt',
        mime='text/plain'
    )

    profs_at = profs_at
    if 'professions' not in st.session_state:
        st.session_state['professions'] = profs_at
    with open(r'Projeto_Bloco_Ciência_Dados_Aplicada\app\data\professions.txt','w') as f:
        for item in profs_at:
            f.write(item + '\n')