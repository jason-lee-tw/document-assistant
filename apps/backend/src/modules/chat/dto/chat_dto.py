from typing import Literal

from pydantic import BaseModel


class ChatHistoryDTO(BaseModel):
  role: Literal['user', 'assistant', 'system', 'tool']
  content: str


class ChatReqDTO(BaseModel):
  message: str
  history: list[ChatHistoryDTO]


class ChatResDTO(ChatReqDTO):
  pass
