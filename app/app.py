import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, ConversationalAgent
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from dotenv import load_dotenv
import os
from google.cloud.bigquery.client import Client

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'app\data\core-shard-442902-h7-3fded6207039.json'
bq_client = Client()

st.set_page_config(page_title='FieldGuide', page_icon='📚', layout='centered', initial_sidebar_state='auto')

st.sidebar.header("Bem-vindo ao FieldGuide!")
st.sidebar.image("https://i.imgur.com/mlvt8or.png", use_column_width=True)
st.sidebar.write("### Selecione a página desejada:")
page = st.sidebar.selectbox("", ["Introdução (TP1)","Dados (TP2)", "BeautifulSoup (TP2)", "TP3 - Selenium, FastAPI, LLM", "App"])

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

    st.image(r"app\data\Beige Modern Chic Business Model Canvas Brainstorm.png")
    st.image(r"app\data\Project Charter - Projeto Bloco Ciência de Dados Aplicada-1.png")

    st.markdown("### Links:")
    st.markdown("#### Inspiração Principal")
    st.write("[Mapa de Carreiras](https://www.vagas.com.br/mapa-de-carreiras/)")
    st.markdown("#### Possíveis Fontes de Dados")
    st.write("[API Feed de Vagas](https://apifeeddevagas.docs.apiary.io/#reference/0/feed-de-vagas/feed-de-vagas)")
    st.write("[Cadastro Nacional de Cursos Superiores](https://emec.mec.gov.br/emec/nova)")
    st.write("[API Profissões](https://api.sienge.com.br/docs/html-files/professions-v1.html#/)")
    st.write("[Tabela de Pontos Sisu](https://www.guiadacarreira.com.br/blog/tabela-de-pontos-do-enem-para-cada-curso)")
    st.write("[Catho](https://www.catho.com.br/vagas/)")
    st.write("[Vagas.com](https://www.vagas.com.br)")

    file = (r'app\data\relatorio_consulta_publica_avancada_curso_25_08_2024_00_05_33.csv')
    data = read_csv(file)

    st.markdown("### Exemplo de tabela de dados:")
    st.write("O exemplo a seguir utiliza uma tabela vinda do site citado acima (Cadastro Nacional de Cursos Superiores), ela mostra apenas cursos de 'Dados' e os dados não foram tratados, portanto há diversas colunas que não serão utilizadas no projeto final. Eu pretendo ampliar estes dados para todo o Brasil e utilizar APIs, porém ainda não consegui fazer funcionar mas estou trabalhando em me capacitar para tal.")
    dataframe = st.dataframe(data)

if page == "Dados (TP2)":
    st.title("Dados Relatório Consulta Pública Avançada Curso")
    file = (r'app\data\relatorio_consulta_publica_avancada_curso_25_08_2024_00_05_33.csv')
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

if page == "BeautifulSoup (TP2)":
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
    with open(r'app\data\professions.txt','w') as f:
        for item in profs_at:
            f.write(item + '\n')
            
if page == "TP3 - Selenium, FastAPI, LLM":
    st.title("TP3 - Selenium, FastAPI, LLM")
    st.write("Esta parte do trabalho não é tão grande quanto as últimas. Não obtive êxito após testar em alguns sites diferentes, porém quero demonstrar que tenho interesse em utilizá-lo para coletar dados de sites como 'vagas.com.br' e 'catho.com.br'.")
    st.write("Com isso eu poderia coletar dados de vagas de emprego e salários, por exemplo, e disponibilizar para o usuário juntamente dos cursos. Com isto, já correlaciono ao uso de IA, possivelmente fazendo textos que explicam detalhes e como se relacionam cada vaga com certos cursos.")
    st.write("Com o conhecimento que ganharei neste trimestre e com o que já aprendi, pretendo fazer um projeto mais robusto e completo, com mais funcionalidades e informações.")
    st.write("Sobre o FastAPI, eu não consegui implementar nada ainda, mas pretendo utilizá-lo para criar uma API que disponibilize todos dados que coletarei.")
    st.write("Esperava fazer mais nesta etapa mas apenas tive uma aula sobre as funcionalidades da FastAPI e não pratiquei com Selenium mas a proposta de negócio está mais clara para mim e estou mais confiante para fazer um projeto mais completo.")
    st.write("Novas pastas foram inclusas ('FastAPI' e 'Selenium' na pasta 'services') com os protótipos de código que eu pretendo utilizar.")
    st.write("Exemplos de como demonstrar dados no projeto tirados do Mapa VAGAS de Carreiras:")

    col1, col2 = st.columns(2)
    with col1:
        st.image('https://i.imgur.com/Y5wA5nY.png')
    with col2:
        st.image('https://i.imgur.com/x0q8RvQ.png')

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
tools = [WikipediaQueryRun(name="Wikipedia", description="Searches Wikipedia for information", api_wrapper=api_wrapper,)]
    

prefix = """
        Você deve apenas trabalhar em Português Brasileiro. Você é a I.A do FieldGuide, um sistema criado para dar informações de carreira para os usuários.
         Considere que você receberá um curso ou profissão de entrada e deverá retornar informações sobre ele.
         No caso de um curso, informe quais profissões são possíveis a partir deste curso, e no caso contrário, quais cursos levam à tal profissão escolhida.
         Caso hajam mais de uma opção de resposta, informe todos ao usuário.
         Você tem acesso à ferramenta de pesquisa na Wikipedia, portanto, utilize-a para buscar informações sobre o que foi perguntado.
         Se não souber a resposta, informe ao usuário que não encontrou informações sobre o que foi perguntado. Seja educado, prestativo e formal sempre.
        """

suffix = """
Chat History:
{chat_history}
Latest Question: {input}
{agent_scratchpad}
"""
prompt = ConversationalAgent.create_prompt(
    tools,
    prefix = prefix,
    suffix = suffix,
    input_variables = {"input", "chat_history", "agent_scratchpad"}
)

msg = StreamlitChatMessageHistory()
if "memory" not in st.session_state:
    st.session_state["memory"] = ConversationBufferMemory(
        messages = msg,
        memory_key = "chat_history",
        return_messages=True
    )
memory = st.session_state["memory"]

llm_chain = LLMChain(
    llm = ChatGoogleGenerativeAI(temperature=0.5, model="gemini-1.5-pro", api_key=GEMINI_API_KEY),
    prompt=prompt
)

agent = ConversationalAgent(
    llm_chain=llm_chain,
    memory=memory,
    max_interactions=10,
    tools = tools
)

agent_executor = AgentExecutor(agent=agent, memory=memory, tools=tools)

if page == "App":
    t1, t2 = st.tabs(["Introdução", "Chat Interativo"])
    with t1:
        st.header("Aqui começa o aplicativo FieldGuide em sua forma final!")
        st.write("Este aplicativo foi feito para ajudar você a escolher sua carreira, mostrando cursos superiores e profissões que você pode seguir.")
        st.write("Primeiramente escolha um curso ou profissão de interesse e depois converse com nossa IA interativa para saber mais sobre o assunto.")
        all_courses = [
            "Administração",
            "Administração Pública",
            "Agroecologia",
            "Agronegócio",
            "Agronomia",
            "Análise de Sistemas",
            "Antropologia",
            "Arquitetura e Urbanismo",
            "Arquivologia",
            "Artes",
            "Artes Cênicas",
            "Astronomia",
            "Biblioteconomia",
            "Biologia",
            "Biomedicina",
            "Bioquímica",
            "Canto",
            "Cenografia",
            "Ciência da Computação",
            "Ciências Biológicas",
            "Ciências Contábeis",
            "Ciências Econômicas",
            "Ciências Sociais",
            "Cinema e Audiovisual",
            "Composição e Regência",
            "Computação",
            "Comunicação e Marketing",
            "Comunicação Social",
            "Desenho Industrial",
            "Design",
            "Design de Ambientes",
            "Design de Games",
            "Design de Interiores",
            "Design de Moda",
            "Design de Produto",
            "Design Digital",
            "Design Gráfico",
            "Direção",
            "Direito",
            "Educação Física",
            "Enfermagem",
            "Engenharia Acústica",
            "Engenharia Aeroespacial",
            "Engenharia Aeronáutica",
            "Engenharia Agrícola",
            "Engenharia Agroindustrial",
            "Engenharia Agronômica",
            "Engenharia Ambiental",
            "Engenharia Automotiva",
            "Engenharia Bioenergética",
            "Engenharia Biomédica",
            "Engenharia Bioquímica",
            "Ofertas Bacharelado em Direito",
            "Engenharia Biotecnológica",
            "Engenharia Cartográfica",
            "Engenharia Civil",
            "Engenharia da Computação",
            "Engenharia da Mobilidade",
            "Engenharia de Agrimensura",
            "Engenharia de Agronegócios",
            "Engenharia de Alimentos",
            "Engenharia de Aquicultura",
            "Engenharia de Automação",
            "Engenharia de Bioprocessos",
            "Engenharia de Biossistemas",
            "Engenharia de Biotecnologia",
            "Engenharia de Energia",
            "Engenharia de Gestão",
            "Engenharia de Informação",
            "Engenharia de Instrumentação, Automação e Robótica",
            "Engenharia de Manufatura",
            "Engenharia de Materiais",
            "Engenharia de Minas",
            "Engenharia de Pesca",
            "Engenharia de Petróleo",
            "Engenharia de Produção",
            "Engenharia de Recursos Hídricos",
            "Engenharia de Saúde e Segurança",
            "Engenharia de Sistemas",
            "Engenharia de Software",
            "Engenharia de Telecomunicações",
            "Engenharia de Transporte e Logística",
            "Engenharia Elétrica",
            "Engenharia Eletrônica",
            "Engenharia em Sistemas Digitais",
            "Engenharia Ferroviária e Metroviária",
            "Engenharia Física",
            "Engenharia Florestal",
            "Engenharia Geológica",
            "Engenharia Hídrica",
            "Engenharia Industrial",
            "Engenharia Mecânica",
            "Engenharia Mecatrônica",
            "Engenharia Metalúrgica",
            "Engenharia Naval",
            "Engenharia Química",
            "Engenharia Têxtil",
            "Estatística",
            "Farmácia",
            "Filosofia",
            "Física",
            "Fisioterapia",
            "Fonoaudiologia",
            "Geografia",
            "Gestão Ambiental",
            "Gestão da Informação",
            "Gestão de Políticas Públicas",
            "Gestão de Serviços de Saúde",
            "Gestão do Agronegócio",
            "Gestão Pública",
            "História",
            "Hotelaria",
            "Jornalismo",
            "Letras",
            "Marketing",
            "Matemática",
            "Mecânica Industrial",
            "Medicina",
            "Medicina Veterinária",
            "Moda",
            "Música",
            "Nutrição",
            "Odontologia",
            "Pedagogia",
            "Políticas Públicas",
            "Propaganda e Marketing",
            "Psicologia",
            "Publicidade e Propaganda",
            "Química",
            "Rádio, TV e Internet",
            "Relações Internacionais",
            "Relações Públicas",
            "Secretariado Executivo",
            "Serviço Social",
            "Sistemas de Informação",
            "Tecnologias Digitais",
            "Teologia",
            "Terapia Ocupacional",
            "Tradutor e Intérprete",
            "Turismo",
            "Zootecnia"
        ]
        selected_course = st.selectbox("Veja todos os cursos", all_courses)
        profs_at = st.session_state['professions']
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        sel_let = st.selectbox("Profissões por letra", alphabet)
        if sel_let:
            st.markdown(
                f"<div style='height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px;'>{''.join([f'<p>{prof}</p>' for prof in profs_at if prof[0] == sel_let])}</div>",
                unsafe_allow_html=True
            )

    with t2:
        st.header("Converse com nossa IA Interativa!")
        query = st.text_input("Não se esqueça de informá-la de seu curso ou profissão de interesse!", placeholder="Digite aqui...")
        if query:
            with st.spinner("Aguarde..."):
                result = agent_executor.run(query)
                st.info(result, icon="🤖")
        