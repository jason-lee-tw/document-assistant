import os

from langchain.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector


def get_embedding_model() -> Embeddings:
  OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')

  if OLLAMA_BASE_URL is None:
    raise RuntimeError('`OLLAMA_BASE_URL` is not defined.')

  # EmbeddingGemma dimension is from 128 to 768
  return OllamaEmbeddings(
    model='embeddinggemma:latest', dimensions=768, base_url=OLLAMA_BASE_URL
  )


def get_vector_store() -> VectorStore:
  DB_USER = os.getenv('DB_USER')
  DB_PASSWORD = os.getenv('DB_PASSWORD')
  DB_HOST = os.getenv('DB_HOST')
  DB_PORT = os.getenv('DB_PORT')
  DB_NAME = os.getenv('DB_NAME')

  if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise RuntimeError('Database environment variables are not fully defined.')

  connection_string = (
    f'postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
  )

  model = get_embedding_model()

  return PGVector(
    embeddings=model,
    connection=connection_string,
    use_jsonb=True,
    collection_name='rag-document-assistant-documents',
    collection_metadata={'topic': 'documents'},
  )
