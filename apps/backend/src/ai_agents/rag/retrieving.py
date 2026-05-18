from ai_agents.rag.vector_store import get_vector_store


def get_retriever(collection_name: str | None = None):
  store = get_vector_store(collection_name)
  return store.as_retriever(search_kwargs={'k': 3})
