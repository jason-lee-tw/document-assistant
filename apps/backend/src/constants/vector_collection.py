from enum import StrEnum


class VECTOR_STORE_COLLECTION_NAME(StrEnum):
  DEFAULT = 'rag-document-assistant-documents'
  CLAWLED_DOCUMENTS = 'crawled_documents'
