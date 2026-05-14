from fastapi import FastAPI

from server_config.server import start_app


def test_app_is_fastapi_instance():
  app = start_app()
  assert isinstance(app, FastAPI)
