from dataclasses import dataclass
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ai_agents.rag.embedding import embedding, get_vector_store, make_chunk_id


def filter_pending_documents(document_names: list[str]) -> list[str]:
  if not document_names:
    return []

  store = get_vector_store()
  probe_ids = [make_chunk_id(name, 0) for name in document_names]
  existing = store.get_by_ids(probe_ids)
  existing_names = {doc.metadata.get('document_name') for doc in existing}

  return [name for name in document_names if name not in existing_names]


@dataclass
class IngestDocuments:
  ingested: list[str]
  skipped: list[str]


def ingest_documents(files_by_name: dict[str, Path]) -> IngestDocuments:
  pending_names = filter_pending_documents(list(files_by_name.keys()))

  if not pending_names:
    return IngestDocuments(ingested=[], skipped=sorted(files_by_name.keys()))

  splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

  documents: list[Document] = []
  ids: list[str] = []
  for name in pending_names:
    file = files_by_name[name]
    content = file.read_text(encoding='utf-8')
    chunks = splitter.split_text(content)
    for index, chunk in enumerate(chunks):
      chunk_id = make_chunk_id(name, index)
      documents.append(
        Document(
          page_content=chunk,
          metadata={
            'id': chunk_id,
            'source': str(file),
            'document_name': name,
            'chunk_index': index,
          },
        )
      )
      ids.append(chunk_id)

  embedding(documents=documents, ids=ids)

  skipped_names = sorted(name for name in files_by_name if name not in pending_names)

  return IngestDocuments(ingested=sorted(pending_names), skipped=skipped_names)
