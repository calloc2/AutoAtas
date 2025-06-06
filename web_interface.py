import streamlit as st
import tempfile
import os
import json
from main import extrair_dados_ata

st.title("AutoAtas")

# Campo para o usuário definir o nome do presidente
presidente_nome = st.text_input(
    "Nome do Presidente",
    value="Daniel Iglesias de Carvalho"
)

uploaded_files = st.file_uploader(
    "Selecione um ou mais arquivos PDF",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    st.write("Processando arquivos...")
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            dados = extrair_dados_ata(tmp_path, presidente_nome)
            txt_name = os.path.splitext(uploaded_file.name)[0] + ".txt"
            with open(txt_name, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            st.success(f"✅ {uploaded_file.name}: Processado com sucesso! Salvo como {txt_name}")
        except Exception as e:
            st.error(f"❌ {uploaded_file.name}: Erro ao processar ({e})")
        finally:
            os.remove(tmp_path)

st.markdown(
    """
    <hr style="margin-top:2em;margin-bottom:0.5em;">
    <div style="text-align:center; color:gray;">
        Desenvolvido por <b>Yuri Barbosa Takahashi</b> e <b>Gabriel Oliveira Aires</b>
    </div>
    """,
    unsafe_allow_html=True
)