from ai_agents.rag.vector_store import get_vector_store
from langchain_core.documents import Document


def make_chunk_id(document_name: str, chunk_index: int) -> str:
  return f'{document_name}#{chunk_index}'


def embedding(documents: list[Document], ids: list[str]) -> None:
  store = get_vector_store()
  store.add_documents(documents=documents, ids=ids)
