import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

from modules.rag.rag_service import ingest_documents as ingest_documents_fn

router = APIRouter(prefix='/rag')


@router.post('/')
def ingest_documents():
  folder_path = os.getenv('PENDING_DIGEST_FOLDER_PATH')
  if not folder_path:
    raise HTTPException(
      status_code=500,
      detail='`PENDING_DIGEST_FOLDER_PATH` is not defined.',
    )

  folder = Path(folder_path)
  if not folder.is_dir():
    raise HTTPException(
      status_code=500,
      detail=f'Folder `{folder_path}` does not exist.',
    )

  files_by_name = {f.name: f for f in folder.iterdir() if f.is_file()}
  result = ingest_documents_fn(files_by_name)

  return {
    'ingested': result.ingested,
    'skipped': result.skipped,
  }
