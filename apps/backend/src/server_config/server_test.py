from unittest.mock import patch

from fastapi import FastAPI
from server_config.server import start_app


def test_app_is_fastapi_instance():
  app = start_app()
  assert isinstance(app, FastAPI)


def test_app_is_instrumented_for_tracing():
  with patch('server_config.server.FastAPIInstrumentor') as mock_instrumentor:
    app = start_app()
    mock_instrumentor.instrument_app.assert_called_once_with(app)
