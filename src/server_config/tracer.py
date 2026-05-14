import logging
import os

from openinference.instrumentation.langchain import LangChainInstrumentor
from phoenix.otel import register

logger = logging.getLogger(__name__)


def register_phoenix_tracer():
  endpoint = os.getenv('PHOENIX_COLLECTOR_ENDPOINT', 'http://localhost:4317')
  try:
    register(
      endpoint=endpoint,
      project_name='rag-document-assistant',
      protocol='grpc',
      batch=True,
    )
    LangChainInstrumentor().instrument()
  except Exception as e:
    logger.warning('Phoenix tracer registration failed (tracing disabled): %s', e)
