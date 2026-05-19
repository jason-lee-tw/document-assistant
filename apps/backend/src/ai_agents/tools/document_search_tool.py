from ai_agents.rag.vector_store import get_vector_store
from constants.vector_collection import VECTOR_STORE_COLLECTION_NAME
from langchain.tools import tool
from langchain_core.documents import Document


@tool(response_format='content_and_artifact')
def retrieve_context(query: str) -> tuple[str, list[Document]]:
  """
  Retrive relevant documents to help answer user queries.

  Params:
    query: String to do semantic search for the relevant documents.
  """

  retriever = get_vector_store(
    collection_name=VECTOR_STORE_COLLECTION_NAME.CLAWLED_DOCUMENTS
  ).as_retriever()
  docs = retriever.invoke(query, k=4)

  serialized = '\n'.join(
    (
      f"""---

## Document {index + 1}

### Source
{doc.metadata.get('source_url', 'Unknown')}

### Content
```
{doc.page_content}
```
"""
    )
    for index, doc in enumerate(docs)
  )

  return serialized, docs
