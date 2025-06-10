import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from datetime import datetime

def conectar():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        dbname=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"]
        sslmode='require'  # ← obrigatório no Supabase!
    )

def obter_setores():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome FROM setores ORDER BY nome")
    setores = cur.fetchall()
    conn.close()
    return setores

def obter_usuarios():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome FROM usuarios ORDER BY nome")
    usuarios = cur.fetchall()
    conn.close()
    return usuarios

def salvar_usuario(nome, email, senha):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha))
    conn.commit()
    conn.close()

def salvar_atividade(nome, setor_id, data_inicio, data_fim, usuario_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO atividades (nome, setor_id, data_inicio, data_fim, usuario_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (nome, setor_id, data_inicio, data_fim, usuario_id))
    conn.commit()
    conn.close()

def obter_atividades(setor_id=None):
    conn = conectar()
    cur = conn.cursor()
    if setor_id:
        cur.execute("""
            SELECT a.nome, s.nome AS setor, u.nome AS responsavel, a.data_inicio, a.data_fim
            FROM atividades a
            JOIN setores s ON a.setor_id = s.id
            JOIN usuarios u ON a.usuario_id = u.id
            WHERE s.id = %s
            ORDER BY a.data_inicio
        """, (setor_id,))
    else:
        cur.execute("""
            SELECT a.nome, s.nome AS setor, u.nome AS responsavel, a.data_inicio, a.data_fim
            FROM atividades a
            JOIN setores s ON a.setor_id = s.id
            JOIN usuarios u ON a.usuario_id = u.id
            ORDER BY a.data_inicio
        """)
    dados = cur.fetchall()
    conn.close()
    return dados

st.set_page_config(page_title="Gestão de Atividades CGPPI 2025", layout="wide")
st.sidebar.image("logo.png", width=200)
st.title("Atividades CGPPI - IFGoiano - Campus Campos Belos")

menu = st.sidebar.selectbox("Menu", ["Cadastrar Usuário", "Cadastrar Atividade", "Atividades Gerais"])

if menu == "Cadastrar Usuário":
    st.subheader("Novo Usuário")
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Salvar Usuário"):
        salvar_usuario(nome, email, senha)
        st.success("Usuário cadastrado com sucesso!")

elif menu == "Cadastrar Atividade":
    st.subheader("Nova Atividade")
    setores = obter_setores()
    usuarios = obter_usuarios()
    setor_dict = {nome: id for id, nome in setores}
    usuario_dict = {nome: id for id, nome in usuarios}
    setor_nome = st.selectbox("Setor", list(setor_dict.keys()))
    atividade_nome = st.text_input("Nome da Atividade")
    data_inicio = st.date_input("Data de Início", datetime.today())
    data_fim = st.date_input("Data de Término", datetime.today())
    usuario_nome = st.selectbox("Responsável", list(usuario_dict.keys()))
    if st.button("Salvar Atividade"):
        salvar_atividade(atividade_nome, setor_dict[setor_nome], data_inicio, data_fim, usuario_dict[usuario_nome])
        st.success("Atividade cadastrada com sucesso!")

elif menu == "Atividades Gerais":
    st.subheader("Visualização Geral de Atividades")
    setores = obter_setores()
    setor_dict = {nome: id for id, nome in setores}
    setor_filtro = st.selectbox("Filtrar por Setor", ["Todos"] + list(setor_dict.keys()))
    setor_id = setor_dict[setor_filtro] if setor_filtro != "Todos" else None
    dados = obter_atividades(setor_id)
    df = pd.DataFrame(dados, columns=["Atividade", "Setor", "Responsável", "Início", "Fim"])
    st.dataframe(df)
    fig = px.timeline(df, x_start="Início", x_end="Fim", y="Atividade", color="Setor", title="Gráfico de Gantt das Atividades")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
