# gestao.py (versão para Streamlit Cloud com banco remoto)
import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Dados de conexão com MySQL remoto (ex: PlanetScale, Railway, etc.)
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = conn.cursor(dictionary=True)

st.title("Atividades")

aba = st.sidebar.selectbox(
    "Menu", ["Cadastrar Usuário", "Cadastrar Atividade", "Atividades Gerais"])

if aba == "Cadastrar Usuário":
    st.subheader("Novo Usuário")
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Salvar Usuário"):
        try:
            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha))
            conn.commit()
            st.success("Usuário cadastrado com sucesso!")
        except mysql.connector.IntegrityError:
            st.error("Erro: este e-mail já está cadastrado.")

elif aba == "Cadastrar Atividade":
    st.subheader("Nova Atividade")
    cursor.execute("SELECT * FROM setores")
    setores = cursor.fetchall()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    if setores and usuarios:
        setor_opcoes = {setor['nome']: setor['id'] for setor in setores}
        usuario_opcoes = {usuario['nome']: usuario['id']
                          for usuario in usuarios}

        setor_nome = st.selectbox("Setor", list(setor_opcoes.keys()))
        usuario_nome = st.selectbox("Responsável", list(usuario_opcoes.keys()))
        nome_atividade = st.text_input("Nome da Atividade")
        data_inicio = st.date_input("Data de Início", value=datetime.today())
        data_fim = st.date_input("Data de Término", value=datetime.today())

        if st.button("Salvar Atividade"):
            setor_id = setor_opcoes[setor_nome]
            usuario_id = usuario_opcoes[usuario_nome]
            try:
                cursor.execute("INSERT INTO atividades (nome, setor_id, data_inicio, data_fim, usuario_id) VALUES (%s, %s, %s, %s, %s)",
                               (nome_atividade, setor_id, data_inicio, data_fim, usuario_id))
                conn.commit()
                st.success("Atividade cadastrada com sucesso!")
            except mysql.connector.Error as e:
                st.error(f"Erro ao cadastrar atividade: {e}")
    else:
        st.info("É necessário ter pelo menos um setor e um usuário cadastrados.")

elif aba == "Atividades Gerais":
    st.subheader("Visualização Geral das Atividades")
    cursor.execute("SELECT * FROM setores")
    setores = cursor.fetchall()
    setor_filtro = st.selectbox(
        "Filtrar por Setor", ["Todos"] + [setor['nome'] for setor in setores])

    query = """
        SELECT a.nome AS atividade, s.nome AS setor, u.nome AS responsavel,
               a.data_inicio, a.data_fim
        FROM atividades a
        JOIN setores s ON a.setor_id = s.id
        JOIN usuarios u ON a.usuario_id = u.id
    """
    valores = ()
    if setor_filtro != "Todos":
        query += " WHERE s.nome = %s"
        val
