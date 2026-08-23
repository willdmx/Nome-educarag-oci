"""Recuperação de conhecimento local com TF-IDF e similaridade de cosseno."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re
import unicodedata
from typing import Any

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KNOWLEDGE_BASE_PATH = PROJECT_ROOT / "data" / "base_conhecimento.csv"
REQUIRED_COLUMNS = ("categoria", "pergunta", "resposta", "fonte")
DEFAULT_TOP_K = 3
MIN_RELEVANCE_SCORE = 0.20


class RAGError(RuntimeError):
    """Erro base do mecanismo de recuperação."""


class KnowledgeBaseError(RAGError):
    """A base de conhecimento não pôde ser carregada ou indexada."""


class QueryError(RAGError, ValueError):
    """A pergunta ou um parâmetro da consulta é inválido."""


def _normalize_text(value: str) -> str:
    """Normaliza Unicode, caixa e espaços sem remover informação textual."""

    normalized = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"\s+", " ", normalized).strip()


def _resolve_csv_path(csv_path: str | Path | None) -> Path:
    if csv_path is None:
        return DEFAULT_KNOWLEDGE_BASE_PATH

    path = Path(csv_path).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


class RAGRetriever:
    """Indexa uma base CSV e recupera os registros mais próximos da pergunta.

    Parameters
    ----------
    csv_path:
        Caminho da base de conhecimento. Quando omitido, usa
        ``data/base_conhecimento.csv`` na raiz do projeto.
    """

    def __init__(self, csv_path: str | Path | None = None) -> None:
        self.csv_path = _resolve_csv_path(csv_path)
        self._records = self._load_knowledge_base()
        self._documents = self._build_documents(self._records)
        self._vectorizer = TfidfVectorizer(
            lowercase=False,
            strip_accents="unicode",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        try:
            self._document_matrix = self._vectorizer.fit_transform(self._documents)
        except ValueError as exc:
            raise KnowledgeBaseError(
                f"Não foi possível criar o índice TF-IDF de '{self.csv_path}': {exc}"
            ) from exc

    @property
    def size(self) -> int:
        """Quantidade de registros válidos indexados."""

        return len(self._records)

    def _load_knowledge_base(self) -> pd.DataFrame:
        if not self.csv_path.exists():
            raise KnowledgeBaseError(
                f"Base de conhecimento não encontrada: '{self.csv_path}'."
            )
        if not self.csv_path.is_file():
            raise KnowledgeBaseError(
                f"O caminho da base de conhecimento não é um arquivo: '{self.csv_path}'."
            )

        try:
            records = pd.read_csv(
                self.csv_path,
                encoding="utf-8",
                dtype=str,
                keep_default_na=False,
            )
        except (OSError, UnicodeError, pd.errors.ParserError) as exc:
            raise KnowledgeBaseError(
                f"Falha ao ler a base de conhecimento '{self.csv_path}': {exc}"
            ) from exc

        missing_columns = [
            column for column in REQUIRED_COLUMNS if column not in records.columns
        ]
        if missing_columns:
            missing = ", ".join(missing_columns)
            raise KnowledgeBaseError(
                f"A base '{self.csv_path}' não possui as colunas obrigatórias: {missing}."
            )
        if records.empty:
            raise KnowledgeBaseError(
                f"A base de conhecimento '{self.csv_path}' está vazia."
            )

        records = records.loc[:, list(REQUIRED_COLUMNS)].copy()
        for column in REQUIRED_COLUMNS:
            records[column] = records[column].str.strip()

        invalid_rows = records.eq("").any(axis=1)
        if invalid_rows.any():
            line_numbers = ", ".join(
                str(index + 2) for index in records.index[invalid_rows].tolist()
            )
            raise KnowledgeBaseError(
                "A base contém campos obrigatórios vazios nas linhas do CSV: "
                f"{line_numbers}."
            )

        return records.reset_index(drop=True)

    @staticmethod
    def _build_documents(records: pd.DataFrame) -> list[str]:
        documents = (
            records["categoria"]
            + " "
            + records["pergunta"]
            + " "
            + records["resposta"]
        )
        return [_normalize_text(document) for document in documents.tolist()]

    def retrieve(
        self,
        question: str,
        top_k: int = DEFAULT_TOP_K,
    ) -> tuple[str, list[dict[str, Any]]]:
        """Retorna um contexto formatado e os metadados dos melhores registros."""

        if not isinstance(question, str):
            raise QueryError("A pergunta deve ser informada como texto.")

        normalized_question = _normalize_text(question)
        if not normalized_question:
            raise QueryError("Digite uma pergunta antes de consultar a base.")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
            raise QueryError("top_k deve ser um número inteiro maior que zero.")

        try:
            question_vector = self._vectorizer.transform([normalized_question])
            similarities = cosine_similarity(
                question_vector, self._document_matrix
            ).ravel()
        except ValueError as exc:
            raise QueryError(f"Não foi possível processar a pergunta: {exc}") from exc

        result_count = min(top_k, self.size)
        ranked_indexes = sorted(
            range(self.size),
            key=lambda index: (-float(similarities[index]), index),
        )[:result_count]

        has_sufficient_relevance = bool(
            question_vector.nnz
            and ranked_indexes
            and similarities[ranked_indexes[0]] >= MIN_RELEVANCE_SCORE
        )

        metadata: list[dict[str, Any]] = []
        context_blocks: list[str] = []
        for rank, index in enumerate(ranked_indexes, start=1):
            record = self._records.iloc[int(index)]
            item: dict[str, Any] = {
                "rank": rank,
                "score": float(similarities[index]),
                "categoria": record["categoria"],
                "pergunta": record["pergunta"],
                "resposta": record["resposta"],
                "fonte": record["fonte"],
            }
            metadata.append(item)
            if has_sufficient_relevance:
                context_blocks.append(
                    "\n".join(
                        (
                            f"[Documento {rank}]",
                            f"Categoria: {item['categoria']}",
                            f"Pergunta: {item['pergunta']}",
                            f"Resposta: {item['resposta']}",
                            f"Fonte: {item['fonte']}",
                        )
                    )
                )

        return "\n\n".join(context_blocks), metadata


@lru_cache(maxsize=8)
def _get_cached_retriever(resolved_path: str) -> RAGRetriever:
    return RAGRetriever(resolved_path)


def get_retriever(csv_path: str | Path | None = None) -> RAGRetriever:
    """Obtém um retriever em cache para evitar reindexação a cada interação."""

    return _get_cached_retriever(str(_resolve_csv_path(csv_path)))


def retrieve_context(
    question: str,
    top_k: int = DEFAULT_TOP_K,
    csv_path: str | Path | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Atalho funcional para recuperar contexto e metadados."""

    return get_retriever(csv_path).retrieve(question, top_k=top_k)
