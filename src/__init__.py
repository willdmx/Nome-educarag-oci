"""Componentes centrais do agente EducaRAG OCI."""

from .rag import (
    DEFAULT_KNOWLEDGE_BASE_PATH,
    KnowledgeBaseError,
    MIN_RELEVANCE_SCORE,
    QueryError,
    RAGError,
    RAGRetriever,
    get_retriever,
    retrieve_context,
)

__all__ = [
    "DEFAULT_KNOWLEDGE_BASE_PATH",
    "KnowledgeBaseError",
    "MIN_RELEVANCE_SCORE",
    "QueryError",
    "RAGError",
    "RAGRetriever",
    "get_retriever",
    "retrieve_context",
]
