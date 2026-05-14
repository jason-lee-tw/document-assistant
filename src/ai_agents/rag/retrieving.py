from ai_agents.rag.vector_store import get_vector_store


def get_retriever():
  store = get_vector_store()
  return store.as_retriever(search_kwargs={'k': 3})
