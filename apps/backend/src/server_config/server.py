import importlib
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from server_config.tracer import register_phoenix_tracer


def start_app():
  load_dotenv()
  register_phoenix_tracer()
  app = FastAPI(title='Chat Bot API', version='1.0.0', docs_url='/docs')

  src_root = Path(__file__).parent.parent

  for controller_file in sorted((src_root / 'modules').rglob('*_controller.py')):
    module_name = str(controller_file.relative_to(src_root).with_suffix('')).replace(
      '/', '.'
    )

    module = importlib.import_module(module_name)

    if hasattr(module, 'router'):
      app.include_router(module.router)

  return app
