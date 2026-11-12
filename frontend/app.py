import streamlit as st
import requests
import pandas as pd

# =========================
# CONFIGURAÇÃO
# =========================

st.set_page_config(
    page_title="Caderno de Erros",
    page_icon="📚",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"

# =========================
# MENU
# =========================

st.sidebar.title("📚 Caderno de Erros")

pagina = st.sidebar.radio(
    "Navegação",
    ["Início", "Cadastrar erro", "Consultar erros", "Revisar erros"]
)

# =========================
# PÁGINA INICIAL
# =========================

if pagina == "Início":

    st.title("📚 Caderno de Erros")

    st.subheader("Bem-vindo ao Caderno de Erros!")

    st.write("""
    O Caderno de Erros é uma aplicação que permite registrar,
    organizar e acompanhar erros cometidos durante os estudos.

    Seu objetivo é ajudar estudantes a identificar dificuldades
    e melhorar seu desempenho por meio da revisão.
    """)

    try:
        resposta = requests.get(f"{API_URL}/erros", timeout=10)

        if resposta.status_code == 200:

            dados = resposta.json()

            # TOTAL DE ERROS CADASTRADOS
            total_erros = len(dados)

            # TOTAL DE REVISÕES REALIZADAS
            total_revisoes = sum(
                len(erro.get("revisoes", []))
                for erro in dados
            )

            # EXIBIR INDICADORES
            coluna1, coluna2 = st.columns(2)

            with coluna1:
                st.metric(
                    "📚 Erros cadastrados",
                    total_erros
                )

            with coluna2:
                st.metric(
                    "🔄 Revisões realizadas",
                    total_revisoes
                )

    except requests.exceptions.RequestException:
        st.warning("Não foi possível conectar à API.")


# =========================
# CADASTRAR ERRO
# =========================

elif pagina == "Cadastrar erro":

    st.title("✏️ Cadastrar novo erro")

    with st.form("formulario_erro"):

        usuario = st.text_input("E-mail do estudante")

        materia = st.text_input("Matéria")

        assunto = st.text_input("Assunto")

        tipo = st.selectbox(
            "Tipo de erro",
            ["conceito", "interpretação", "cálculo", "distração", "outro"]
        )

        descricao = st.text_area(
            "Descrição do erro",
            placeholder="Explique o que você errou e por quê..."
        )

        dificuldade = st.slider(
            "Dificuldade",
            min_value=1,
            max_value=5,
            value=3
        )

        tags = st.text_input(
            "Tags",
            placeholder="Ex.: MongoDB, documentos, coleções"
        )

        enviar = st.form_submit_button("Cadastrar erro")

    if enviar:

        if not usuario or not materia or not assunto or not descricao:
            st.warning("Preencha os campos obrigatórios.")

        else:

            novo_erro = {
                "usuarioEmail": usuario,
                "materia": materia,
                "assunto": assunto,
                "tipo": tipo,
                "descricao": descricao,
                "dificuldade": dificuldade,
                "tags": [
                    tag.strip()
                    for tag in tags.split(",")
                    if tag.strip()
                ]
            }

            try:

                resposta = requests.post(
                    f"{API_URL}/erros",
                    json=novo_erro,
                    timeout=10
                )

                if resposta.status_code == 200:
                    st.success("Erro cadastrado com sucesso!")
                    st.balloons()

                else:
                    st.error("Não foi possível cadastrar o erro.")

            except requests.exceptions.RequestException:
                st.error("Não foi possível conectar à API.")

# =========================
# CONSULTAR ERROS
# =========================

elif pagina == "Consultar erros":

    st.title("📋 Consulta de erros")

    st.write("Visualize e filtre os erros registrados no seu caderno.")

    try:

        resposta = requests.get(
            f"{API_URL}/erros",
            timeout=10
        )

        if resposta.status_code == 200:

            dados = resposta.json()

            if dados:

                df = pd.DataFrame(dados)

                # FILTRO POR MATÉRIA
                if "materia" in df.columns:

                    materias = ["Todas"] + sorted(
                        df["materia"].dropna().unique().tolist()
                    )

                    materia = st.selectbox(
                        "📚 Filtrar por matéria",
                        materias
                    )

                    if materia != "Todas":
                        df = df[df["materia"] == materia]

                # FILTRO POR TIPO DE ERRO
                if "tipo" in df.columns:

                    tipos = ["Todos"] + sorted(
                        df["tipo"].dropna().unique().tolist()
                    )

                    tipo = st.selectbox(
                        "🔎 Filtrar por tipo",
                        tipos
                    )

                    if tipo != "Todos":
                        df = df[df["tipo"] == tipo]

                # FILTRO POR DIFICULDADE
                if "dificuldade" in df.columns:

                    dificuldades = st.multiselect(
                        "🎯 Filtrar por dificuldade",
                        sorted(df["dificuldade"].dropna().unique().tolist())
                    )

                    if dificuldades:
                        df = df[df["dificuldade"].isin(dificuldades)]

                st.divider()

                st.subheader("Erros encontrados")

                st.write(f"Total de erros exibidos: {len(df)}")

                # EXIBIR ERROS EM CARDS
                for _, erro in df.iterrows():

                    with st.expander(
                        f"📖 {erro.get('materia', 'Sem matéria')} — "
                        f"{erro.get('assunto', 'Sem assunto')}"
                    ):

                        st.write("**Descrição:**")
                        st.write(erro.get("descricao", "Não informada"))

                        st.write("**Tipo:**", erro.get("tipo", "Não informado"))

                        st.write(
                            "**Dificuldade:**",
                            erro.get("dificuldade", "Não informada")
                        )

                        st.write(
                            "**Quantidade de erros:**",
                            erro.get("quantidadeErros", 1)
                        )

                        st.write(
                            "**Status:**",
                            erro.get("status", "Não informado")
                        )

                        st.write(
                            "**Tags:**",
                            ", ".join(erro.get("tags", []))
                        )

            else:

                st.info("Você ainda não cadastrou nenhum erro.")

        else:

            st.error("Erro ao consultar os registros.")

    except requests.exceptions.RequestException:

        st.error("Não foi possível conectar à API.")
# =========================
# REVISAR ERROS
# =========================
elif pagina == "Revisar erros":

    st.title("🔄 Revisão de erros")

    st.write("Revise seus erros e acompanhe sua evolução.")

    try:

        resposta = requests.get(
            f"{API_URL}/erros",
            timeout=10
        )

        if resposta.status_code == 200:

            dados = resposta.json()

            if dados:

                st.subheader("📚 Escolha um erro para revisar")

                opcoes = {
                    f"{erro['materia']} - {erro['assunto']} "
                    f"(ID: {erro['_id']})": erro
                    for erro in dados
                }

                escolha = st.selectbox(
                    "Erro:",
                    list(opcoes.keys())
                )

                erro_selecionado = opcoes[escolha]

                st.divider()

                st.subheader("Detalhes do erro")

                st.write(
                    "**Matéria:**",
                    erro_selecionado.get("materia", "")
                )

                st.write(
                    "**Assunto:**",
                    erro_selecionado.get("assunto", "")
                )

                st.write(
                    "**Descrição:**",
                    erro_selecionado.get("descricao", "")
                )

                st.write(
                    "**Quantidade de erros:**",
                    erro_selecionado.get("quantidadeErros", 1)
                )

                st.divider()

                # HISTÓRICO DE REVISÕES
                st.subheader("📅 Histórico de revisões")

                historico = erro_selecionado.get("revisoes", [])

                if historico:

                    for revisao in reversed(historico):

                        data = revisao.get("data", "")
                        resultado_historico = revisao.get("resultado", "")
                        observacao_historico = revisao.get("observacao", "")

                        if resultado_historico == "acertou":
                            st.success(f"✅ Acertou — {data}")
                        else:
                            st.error(f"❌ Errou novamente — {data}")

                        if observacao_historico:
                            st.write(
                                f"Observação: {observacao_historico}"
                            )

                        st.divider()

                else:

                    st.info("Este erro ainda não possui revisões registradas.")

                # REGISTRAR NOVA REVISÃO
                st.subheader("Registrar resultado da revisão")

                resultado = st.radio(
                    "Como foi sua revisão?",
                    ["Acertei", "Errei novamente"]
                )

                observacao = st.text_area(
                    "Observação (opcional)",
                    placeholder="O que você aprendeu nessa revisão?"
                )

                if st.button("Registrar revisão"):

                    resultado_api = (
                        "acertou"
                        if resultado == "Acertei"
                        else "errou"
                    )

                    dados_revisao = {
                        "resultado": resultado_api,
                        "observacao": observacao
                    }

                    resposta_revisao = requests.patch(
                        f"{API_URL}/erros/"
                        f"{erro_selecionado['_id']}/revisoes",
                        json=dados_revisao,
                        timeout=10
                    )

                    if resposta_revisao.status_code == 200:

                        st.success("Revisão registrada com sucesso!")

                        if resultado == "Acertei":
                            st.balloons()
                        else:
                            st.warning(
                                "Esse erro foi contabilizado novamente."
                            )
                        st.rerun()

                    else:

                        st.error(
                            f"Erro ao registrar revisão: "
                            f"{resposta_revisao.text}"
                        )

            else:

                st.info("Cadastre um erro antes de realizar uma revisão.")

        else:

            st.error("Não foi possível consultar os erros.")

    except requests.exceptions.RequestException:

        st.error("Não foi possível conectar à API.")
