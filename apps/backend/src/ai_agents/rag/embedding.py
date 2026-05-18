import asyncio
from typing import Any

from ai_agents.rag.vector_store import get_vector_store
from constants.vector_collection import VECTOR_STORE_COLLECTION_NAME
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from server_config.logger import Logger

logger = Logger(__name__)

RETRY_DELAY_SECONDS = 0.5


def make_chunk_id(document_name: str, chunk_index: int) -> str:
  return f'{document_name}#{chunk_index}'


def embedding(
  documents: list[Document],
  ids: list[str],
  collection_name: VECTOR_STORE_COLLECTION_NAME | None = None,
) -> None:
  store = get_vector_store(collection_name)
  store.add_documents(documents=documents, ids=ids)


async def batch_embedding(
  documents: list[Document],
  ids: list[str],
  collection_name: VECTOR_STORE_COLLECTION_NAME | None = None,
  batch_size: int = 100,
  max_concurrency: int = 5,
  max_attempts: int = 3,
) -> None:
  store = get_vector_store(collection_name)
  batches = [
    (documents[i : i + batch_size], ids[i : i + batch_size])
    for i in range(0, len(documents), batch_size)
  ]
  total = len(batches)
  semaphore = asyncio.Semaphore(max_concurrency)

  results = await asyncio.gather(
    *[
      __process_batch_embedding(
        batch_number=index + 1,
        batch_docs=batch_docs,
        batch_ids=batch_ids,
        max_attempts=max_attempts,
        semaphore=semaphore,
        store=store,
        total_number_of_batch=total,
      )
      for index, (batch_docs, batch_ids) in enumerate(batches)
    ]
  )

  succeeded = sum(results)
  summary = f'Batch embedding finished: {succeeded}/{total} batches succeeded.'

  if succeeded != total:
    logger.warn(summary)
  else:
    logger.log(summary)


async def __process_batch_embedding(
  batch_number: int,
  batch_docs: list[Document],
  batch_ids: list[str],
  total_number_of_batch: int,
  semaphore: asyncio.Semaphore,
  max_attempts: int,
  store: VectorStore,
) -> bool:
  label = f'batch {batch_number}/{total_number_of_batch}'
  async with semaphore:
    for attempt in range(1, max_attempts + 1):
      try:
        logger.log(f'Processing {label}')
        await asyncio.to_thread(
          store.add_documents, documents=batch_docs, ids=batch_ids
        )
        logger.log(f'Completed {label}')
        return True
      except Exception as error:
        logger.error(
          f'Failed to process {label} (attempt {attempt}/{max_attempts}): {error}'
        )
        if attempt < max_attempts:
          await asyncio.sleep(RETRY_DELAY_SECONDS)
  logger.error(f'Giving up on {label} after {max_attempts} attempts')
  return False


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
