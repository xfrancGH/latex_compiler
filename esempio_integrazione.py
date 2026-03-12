"""
esempio_integrazione.py
========================
Mostra come usare LatexCompiler in tre contesti diversi:
  1. Script standalone
  2. Dentro Streamlit (sostituzione del blocco chiamata.py)
  3. Override da variabile d'ambiente (utile per CI/CD)
"""

# L'import ora punta a compiler.py invece che a latex_compiler.py
from compiler import LatexCompiler


# ============================================================
#  1. USO STANDALONE
# ============================================================
def esempio_standalone():
    compiler = LatexCompiler()          # legge latex_config.toml
    print(f"Modalità attiva: {compiler.mode}")

    compiler.compile_zip(
        zip_input="./test/miei_file_tex.zip",
        output_path="./test/output_verifiche.zip",
    )


# ============================================================
#  2. INTEGRAZIONE IN STREAMLIT
# ============================================================
def blocco_streamlit():
    import streamlit as st
    from compiler import LatexCompiler

    col_local, col_hf, col_render = st.columns(3)

    with col_local:
        if st.button("⚙️ Locale", use_container_width=True):
            _run_streamlit_compilation(mode="local")

    with col_hf:
        if st.button("🚀 HuggingFace", type="secondary", use_container_width=True):
            _run_streamlit_compilation(mode="huggingface")

    with col_render:
        if st.button("☁️ Render", type="secondary", use_container_width=True):
            _run_streamlit_compilation(mode="render")


def _run_streamlit_compilation(mode: str):
    import os
    import streamlit as st
    from compiler import LatexCompiler

    zip_data = st.session_state.get("current_latex_zip")
    if not zip_data:
        st.error("Nessuno ZIP caricato in sessione.")
        return

    # Inietta i token dai secrets Streamlit nelle variabili d'ambiente
    token_map = {
        "huggingface": ("HF_TOKEN",         "HF_TOKEN"),
        "render":      ("RENDER_API_KEY",    "RENDER_API_KEY"),
    }
    if mode in token_map:
        secret_key, env_key = token_map[mode]
        token = st.secrets.get(secret_key, "")
        if token:
            os.environ[env_key] = token

    prog_bar  = st.progress(0)
    status    = st.empty()

    try:
        status.info(f"⏳ Compilazione in corso ({mode})...")
        prog_bar.progress(30)

        result_bytes = LatexCompiler(mode=mode).compile_zip(zip_data)

        prog_bar.progress(100)
        status.success("✅ PDF generati!")
        st.session_state["current_pdf_zip"] = result_bytes
        st.session_state["pdf_ready"] = True

        import time; time.sleep(0.8)
        st.rerun()

    except Exception as e:
        prog_bar.empty()
        status.error(f"⚠️ {e}")


# ============================================================
#  3. OVERRIDE DA VARIABILE D'AMBIENTE
#
#     export LATEX_MODE=render
#     export RENDER_API_KEY=xxxx
#     python esempio_integrazione.py
# ============================================================
def esempio_env_override():
    import os
    mode = os.environ.get("LATEX_MODE")     # None → usa il .toml

    LatexCompiler(mode=mode).compile_zip(
        "./test/miei_file_tex.zip",
        output_path="./test/out.zip",
    )


# ============================================================
#  4. UTILIZZO DA RIGA DI COMANDO (già incluso in compiler.py)
#
#  python compiler.py miei_file_tex.zip                        # usa il .toml
#  python compiler.py miei_file_tex.zip --mode local
#  python compiler.py -o ./test/outHF.zip ./test/miei_file_tex.zip --mode huggingface
#  python compiler.py -o ./test/outRD.zip ./test/miei_file_tex.zip --mode render
# ============================================================

if __name__ == "__main__":
    esempio_standalone()
    # blocco_streamlit()
