import streamlit as st

# A configuração da página DEVE ser o primeiro comando do Streamlit
st.set_page_config(
    page_title="DataGrid F1",
    page_icon="🏎️",
    layout="wide"
)

def main():
    st.title("🏎️ DataGrid F1")
    st.markdown("Bem-vindo ao esqueleto da aplicação F1DB.")
    st.info("Esta é a página inicial. Use o menu lateral para navegar entre as seções da aplicação.")
    
    st.write("Comece editando este arquivo ou criando novas páginas na pasta `pages/`.")

if __name__ == "__main__":
    main()