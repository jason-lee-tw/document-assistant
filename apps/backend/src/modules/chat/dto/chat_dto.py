from typing import Literal

from langchain_core.documents import Document
from pydantic import BaseModel


class ChatHistoryDTO(BaseModel):
  role: Literal['user', 'assistant', 'system', 'tool']
  content: str


class ChatReqDTO(BaseModel):
  message: str
  history: list[ChatHistoryDTO]


class ChatResDTO(ChatReqDTO):
  context: list[Document] | None = None
