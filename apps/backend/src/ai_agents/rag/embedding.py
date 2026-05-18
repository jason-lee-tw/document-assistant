from typing import Any

from ai_agents.rag.vector_store import get_vector_store
from constants.vector_collection import VECTOR_STORE_COLLECTION_NAME
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def make_chunk_id(document_name: str, chunk_index: int) -> str:
  return f'{document_name}#{chunk_index}'


def embedding(
  documents: list[Document],
  ids: list[str],
  collection_name: VECTOR_STORE_COLLECTION_NAME | None = None,
) -> None:
  store = get_vector_store(collection_name)
  store.add_documents(documents=documents, ids=ids)


def split_text_into_chunks(
  text: str, document_id: str, metadata: dict[str, Any]
) -> dict[str, Document]:
  splitter = get_splitter()
  chunk_list = splitter.split_text(text)
  document_map: dict[str, Document] = {}

  # Convert splitted text into Document
  for chunk_index, chunk_content in enumerate(chunk_list):
    chunk_id = make_chunk_id(
      document_name=document_id,
      chunk_index=chunk_index + 1,
    )
    final_metadata = {
      'chunk_id': chunk_id,
      **metadata,
    }
    chunk_doc = Document(
      page_content=chunk_content,
      metadata=final_metadata,
    )
    document_map[chunk_id] = chunk_doc

  return document_map


def get_splitter(chunk_size: int = 1000, chunk_overlap: int = 200):
  return RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
  )
