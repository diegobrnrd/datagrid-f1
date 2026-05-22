import streamlit as st

def setup_sidebar():
    """Configura os elementos visuais da barra lateral."""
    
    # Logo oficial no topo (acima do menu)
    st.logo("https://upload.wikimedia.org/wikipedia/commons/3/33/F1.svg")
    
    # Rodapé da Sidebar (apenas o crédito do F1DB)
    with st.sidebar:
        st.caption("Powered by [F1DB](https://github.com/f1db/f1db) • CC BY 4.0")

def render_footer():
    """Renderiza o rodapé centralizado com seu nome e link do GitHub."""
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align:center; color: #666; font-size: 0.9rem;'>
            <p>🏎️ <b>DataGrid F1 Explorer</b></p>
            <p>Desenvolvido por 
                <a href="https://github.com/diegobrnrd" target="_blank" style="color: #E10600; text-decoration: none;">
                    <b>Diego Bernardo</b>
                </a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )