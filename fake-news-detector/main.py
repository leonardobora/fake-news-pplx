import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    st.set_page_config(
        page_title="🔍 Fake News Detector",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔍 Fake News Detector")
    st.markdown("**Sistema de Detecção de Fake News com CrewAI e Perplexity API**")
    
    # Check API keys
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not perplexity_key or not openai_key:
        st.error("❌ Chaves de API não configuradas. Verifique o arquivo .env")
        st.stop()
    
    st.success("✅ Sistema configurado e pronto para análise!")
    
    # Input options
    input_type = st.selectbox("Tipo de entrada:", ["URL", "Texto"])
    
    if input_type == "URL":
        content = st.text_input("URL da notícia:", placeholder="https://exemplo.com/noticia")
    else:
        content = st.text_area("Texto da notícia:", height=200)
    
    if st.button("🔍 Analisar"):
        if content:
            with st.spinner("Analisando..."):
                st.info("Análise em progresso... (Este é um demo)")
                # Here would be the actual analysis logic
        else:
            st.warning("Por favor, insira uma URL ou texto para análise.")

if __name__ == "__main__":
    main()