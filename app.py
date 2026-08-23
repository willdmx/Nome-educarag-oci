"""Interface Streamlit do EducaRAG OCI."""

from __future__ import annotations

import logging
from typing import Any

import streamlit as st

from src.llm import (
    LOCAL_MODE,
    OCI_MODE,
    generate_answer_with_mode,
    get_configured_mode,
)
from src.rag import get_retriever


LOGGER = logging.getLogger(__name__)
MAX_QUESTION_LENGTH = 500

EXAMPLE_QUESTIONS = (
    "Como faço para obter meu certificado?",
    "Qual é o prazo para solicitar reembolso?",
    "Como redefinir minha senha?",
    "Como funciona o programa de bolsas?",
    "Como cancelar uma matrícula?",
)


st.set_page_config(
    page_title="EducaRAG OCI",
    page_icon="🎓",
    layout="centered",
)


@st.cache_resource(show_spinner=False)
def _load_retriever() -> Any:
    """Carrega e indexa a base apenas uma vez por processo Streamlit."""

    return get_retriever()


def _select_example(question: str) -> None:
    st.session_state["question_input"] = question
    st.session_state.pop("query_result", None)


def _unique_metadata_values(
    metadata: list[dict[str, Any]], field: str
) -> list[str]:
    values: list[str] = []
    for item in metadata:
        raw_value = item.get(field)
        if raw_value is None:
            continue
        value = str(raw_value).strip()
        if not value or value.lower() == "nan" or value in values:
            continue
        values.append(value)
    return values


def _run_query(question: str) -> dict[str, Any]:
    if len(question) > MAX_QUESTION_LENGTH:
        raise ValueError(
            f"A pergunta deve ter no máximo {MAX_QUESTION_LENGTH} caracteres."
        )

    context, metadata = _load_retriever().retrieve(question, top_k=3)
    generation = generate_answer_with_mode(question, context)
    return {
        "question": question,
        "answer": generation.answer,
        "mode": generation.mode,
        "metadata": metadata,
        "has_sufficient_context": bool(context),
    }


def _render_mode_indicator(mode: str) -> None:
    st.sidebar.subheader("Modo de resposta")
    if mode == OCI_MODE:
        st.sidebar.success(OCI_MODE)
        st.sidebar.caption("O contexto recuperado será enviado ao endpoint configurado.")
    else:
        st.sidebar.info(LOCAL_MODE)
        st.sidebar.caption("A resposta mais relevante da base será exibida diretamente.")


def _render_examples() -> None:
    with st.expander("Perguntas de exemplo", expanded=True):
        first_column, second_column = st.columns(2)
        for index, question in enumerate(EXAMPLE_QUESTIONS):
            target_column = first_column if index % 2 == 0 else second_column
            with target_column:
                st.button(
                    question,
                    key=f"example_{index}",
                    on_click=_select_example,
                    args=(question,),
                    use_container_width=True,
                )


def _render_result(result: dict[str, Any]) -> None:
    metadata = result.get("metadata", [])
    has_sufficient_context = result.get("has_sufficient_context", True)
    sources = (
        _unique_metadata_values(metadata, "fonte") if has_sufficient_context else []
    )
    categories = (
        _unique_metadata_values(metadata, "categoria")
        if has_sufficient_context
        else []
    )

    st.divider()
    st.subheader("Resposta")
    question = str(result.get("question", "")).strip()
    if question:
        st.caption(f"Pergunta consultada: {question}")
    st.write(result["answer"])

    if result.get("mode") == LOCAL_MODE:
        st.caption("Resposta apresentada pelo modo de recuperação local.")

    details_column, categories_column = st.columns(2)
    with details_column:
        st.markdown("**Fontes consultadas**")
        if sources:
            for source in sources:
                st.write(f"• {source}")
        else:
            st.caption("Nenhuma fonte com relevância suficiente.")

    with categories_column:
        st.markdown("**Categorias encontradas**")
        if categories:
            for category in categories:
                st.write(f"• {category}")
        else:
            st.caption("Nenhuma categoria com relevância suficiente.")


def main() -> None:
    st.title("EducaRAG OCI")
    st.markdown(
        "Agente inteligente de suporte educacional com RAG e Oracle Cloud "
        "Infrastructure."
    )
    st.caption(
        "As respostas usam exclusivamente a base de conhecimento fictícia do projeto."
    )

    previous_result = st.session_state.get("query_result")
    active_mode = (
        previous_result.get("mode")
        if isinstance(previous_result, dict)
        else get_configured_mode()
    )
    _render_mode_indicator(active_mode)

    st.sidebar.divider()
    st.sidebar.markdown(
        "**Projeto acadêmico desenvolvido para o Challenge Alura Agente — "
        "Oracle Next Education.**"
    )

    _render_examples()

    with st.form("question_form"):
        st.text_area(
            "Digite sua pergunta",
            key="question_input",
            placeholder="Ex.: Como faço para obter meu certificado?",
            height=110,
            max_chars=MAX_QUESTION_LENGTH,
        )
        submitted = st.form_submit_button(
            "Perguntar", type="primary", use_container_width=True
        )

    if submitted:
        st.session_state.pop("query_result", None)
        question = st.session_state.get("question_input", "").strip()
        if not question:
            st.warning("Digite uma pergunta antes de continuar.")
        elif len(question) > MAX_QUESTION_LENGTH:
            st.warning(
                f"A pergunta deve ter no máximo {MAX_QUESTION_LENGTH} caracteres."
            )
        else:
            try:
                with st.spinner("Consultando a base de conhecimento..."):
                    st.session_state["query_result"] = _run_query(question)
                st.rerun()
            except Exception as exc:
                LOGGER.error(
                    "Falha ao consultar a base (%s).", type(exc).__name__
                )
                st.error(
                    "Não foi possível consultar a base de conhecimento. "
                    "Verifique se o arquivo CSV está disponível e tente novamente."
                )

    result = st.session_state.get("query_result")
    if isinstance(result, dict):
        _render_result(result)

    st.divider()
    st.caption(
        "Projeto acadêmico desenvolvido para o Challenge Alura Agente — "
        "Oracle Next Education."
    )


if __name__ == "__main__":
    main()
