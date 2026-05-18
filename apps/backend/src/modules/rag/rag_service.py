from pathlib import Path
from uuid import uuid7

from ai_agents.rag.embedding import (
  batch_embedding,
  embedding,
  get_splitter,
  get_vector_store,
  make_chunk_id,
  split_text_into_chunks,
)
from ai_agents.tavily.tavily_client import (
  TavilyClient,
)
from ai_agents.tavily.tavily_crawl import TavilyCrawlResult
from constants.vector_collection import VECTOR_STORE_COLLECTION_NAME
from langchain_core.documents import Document
from modules.rag.dto.crawl_documents import (
  CrawlDocumentsResDTO,
  generate_crawl_document_res_dto,
)
from pydantic import BaseModel
from server_config.logger import Logger


def filter_pending_documents(document_names: list[str]) -> list[str]:
  if not document_names:
    return []

  store = get_vector_store()
  probe_ids = [make_chunk_id(name, 0) for name in document_names]
  existing = store.get_by_ids(probe_ids)
  existing_names = {doc.metadata.get('document_name') for doc in existing}

  return [name for name in document_names if name not in existing_names]


class IngestDocumentsResDTO(BaseModel):
  ingested: list[str]
  skipped: list[str]


def ingest_documents(files_by_name: dict[str, Path]) -> IngestDocumentsResDTO:
  pending_names = filter_pending_documents(list(files_by_name.keys()))

  if not pending_names:
    return IngestDocumentsResDTO(ingested=[], skipped=sorted(files_by_name.keys()))

  splitter = get_splitter()

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

  return IngestDocumentsResDTO(ingested=sorted(pending_names), skipped=skipped_names)


async def crawl_documents(url_list: list[str]) -> CrawlDocumentsResDTO:
  tavily = TavilyClient()
  logger = Logger(__name__)

  full_document_id_list: list[str] = []
  full_chunk_id_list: list[str] = []

  logger.log(f'Start crawling documents for URLs ({url_list})')

  # Crawl documents and process the crawl result (embed and store)
  for url in url_list:
    raw_res = tavily.crawler.invoke(
      {'url': url, 'max_depth': 3, 'extract_depth': 'advanced'}
    )
    parsed_res = TavilyClient.parse_crawler_response(raw_response=raw_res)

    logger.log(f'Successfully crawled documents from {url}')

    documents = parsed_res.results

    document_id_list, chunk_id_list = await _process_crawled_document(
      documents=documents
    )
    full_document_id_list.extend(document_id_list)
    full_chunk_id_list.extend(chunk_id_list)

  logger.log(
    f"""Crawling completed: {len(url_list)} URLs, {len(full_document_id_list)} documents & {len(full_chunk_id_list)} chunks."""  # noqa: E501
  )

  return generate_crawl_document_res_dto(
    document_id_list=full_document_id_list,
    chunk_id_list=full_chunk_id_list,
  )


async def _process_crawled_document(
  documents: list[TavilyCrawlResult],
) -> tuple[list[str], list[str]]:
  """
  Chunk, embed and store crawled documents into database.

  Returns:
    List of stored document chunk ID.
  """
  full_document_id_list: list[str] = []
  full_chunk_id_list: list[str] = []
  full_chunk_doc_list: list[Document] = []

  for doc in documents:
    doc_id = str(uuid7())
    doc_content = doc.raw_content
    metadata = {
      'doc_id': doc_id,
      'source_url': doc.url,
    }

    chunk_map = split_text_into_chunks(
      text=doc_content,
      document_id=doc_id,
      metadata=metadata,
    )

    full_document_id_list.append(doc_id)
    full_chunk_id_list.extend([key for key in chunk_map.keys()])
    full_chunk_doc_list.extend([value for value in chunk_map.values()])

  await batch_embedding(
    documents=full_chunk_doc_list,
    ids=full_chunk_id_list,
    collection_name=VECTOR_STORE_COLLECTION_NAME.CLAWLED_DOCUMENTS,
  )

  return full_document_id_list, full_chunk_id_list
