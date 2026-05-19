from fastapi import APIRouter
from modules.chat.chat_service import (
  process_chat,
  process_chat_with_lcel,
  process_chat_with_rag,
  process_chat_with_rag_tool,
)
from modules.chat.dto.chat_dto import ChatHistoryDTO, ChatReqDTO, ChatResDTO

router = APIRouter(prefix='/chat')


@router.post('/')
def handle_chat(body: ChatReqDTO) -> ChatResDTO:
  message = body.message
  history = body.history

  chat_list = [chat for chat in history]
  chat_list.append(ChatHistoryDTO(role='user', content=message))

  result = process_chat(chat_list)

  return ChatResDTO(message=result.content, history=chat_list)


@router.post('/with-rag')
def handle_chat_with_rag(body: ChatReqDTO) -> ChatResDTO:
  message = body.message
  history = body.history

  chat_list = [chat for chat in history]
  chat_list.append(ChatHistoryDTO(role='user', content=message))

  result = process_chat_with_rag(chat_list)

  return ChatResDTO(message=result.content, history=chat_list)


@router.post('/with-lcel')
def handle_chat_with_lcel(body: ChatReqDTO) -> ChatResDTO:
  message = body.message
  history = body.history

  chat_list = [chat for chat in history]
  chat_list.append(ChatHistoryDTO(role='user', content=message))

  result = process_chat_with_lcel(chat_list)
  return ChatResDTO(message=result.content, history=chat_list)


@router.post('/with-rag-tool')
def handle_chat_with_rag_tool(body: ChatReqDTO) -> ChatResDTO:
  message = body.message
  history = body.history

  chat_list = [chat for chat in history]
  chat_list.append(ChatHistoryDTO(role='user', content=message))

  result = process_chat_with_rag_tool(chat_list)
  agent_answer = result.get('answer')
  agent_context_docs = result.get('context')

  return ChatResDTO(message=agent_answer, history=chat_list, context=agent_context_docs)
