import streamlit as st
from utils.db import execute_query

st.set_page_config(page_title="Página de Exemplo", page_icon="🏁", layout="wide")

st.title("🏁 Página de Exemplo")
st.write("Aqui você construirá sua primeira funcionalidade (ex: Corridas).")

# Exemplo comentado de como você fará a chamada ao banco quando começar:
# try:
#     df = execute_query("SELECT * FROM season ORDER BY year DESC LIMIT 5")
#     st.dataframe(df)
# except Exception as e:
#     st.error(f"Erro ao consultar o banco: {e}")