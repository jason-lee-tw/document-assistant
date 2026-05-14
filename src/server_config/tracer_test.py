import os
from unittest.mock import patch

from server_config.tracer import register_phoenix_tracer


def test_register_uses_default_endpoint_when_env_not_set():
  env = {k: v for k, v in os.environ.items() if k != 'PHOENIX_COLLECTOR_ENDPOINT'}
  with (
    patch('server_config.tracer.register') as mock_register,
    patch('server_config.tracer.LangChainInstrumentor'),
    patch.dict(os.environ, env, clear=True),
  ):
    register_phoenix_tracer()
    mock_register.assert_called_once_with(
      endpoint='http://localhost:4317',
      project_name='chat-bot',
      protocol='grpc',
      batch=True,
    )


def test_register_uses_custom_endpoint_from_env():
  custom = 'http://phoenix-server:4317'
  with (
    patch('server_config.tracer.register') as mock_register,
    patch('server_config.tracer.LangChainInstrumentor'),
    patch.dict(os.environ, {'PHOENIX_COLLECTOR_ENDPOINT': custom}),
  ):
    register_phoenix_tracer()
    mock_register.assert_called_once_with(
      endpoint=custom,
      project_name='chat-bot',
      protocol='grpc',
      batch=True,
    )


def test_register_instruments_langchain():
  with (
    patch('server_config.tracer.register'),
    patch('server_config.tracer.LangChainInstrumentor') as mock_instrumentor,
  ):
    register_phoenix_tracer()
    mock_instrumentor.return_value.instrument.assert_called_once()


def test_register_logs_warning_and_continues_when_registration_fails():
  with (
    patch('server_config.tracer.register', side_effect=Exception('connection refused')),
    patch('server_config.tracer.LangChainInstrumentor'),
    patch('server_config.tracer.logger') as mock_logger,
  ):
    register_phoenix_tracer()
    mock_logger.warning.assert_called_once()
