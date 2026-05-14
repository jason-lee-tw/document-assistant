from typing import Any

from fastapi import HTTPException
from langchain_core.documents import Document
from langchain_core.messages import (
  AIMessage,
  BaseMessage,
  HumanMessage,
  SystemMessage,
  ToolMessage,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableSerializable

from ai_agents.base_agent import BaseAgent
from ai_agents.rag.retrieving import get_retriever
from modules.chat.dto.chat_dto import ChatHistoryDTO


def _get_prompt_template() -> ChatPromptTemplate:
  template = ChatPromptTemplate.from_template(
    """# Instruction
Answer the message based only on the following context.

---

## Context
```
{context}
```

---

## User Question
```
{question}
```

---

## Tasks

Provide a detailed answer.
"""
  )

  return template


def _format_docs(docs: list[Document]) -> str:
  """Format retrieved documents into a string"""
  return '\n\n'.join(doc.page_content for doc in docs)


def _convert_chat_list(chat_list: list[ChatHistoryDTO]) -> list[BaseMessage]:
  """Convert chat history list to proper message list for LLM"""
  result: list[BaseMessage] = []

  for chat in chat_list:
    role = chat.role
    content = chat.content
    message: BaseMessage

    if role == 'user':
      message = HumanMessage(content=content)
    elif role == 'system':
      message = SystemMessage(content=content)
    elif role == 'assistant':
      message = AIMessage(content=content)
    elif role == 'tool':
      message = ToolMessage(content=content)
    else:
      raise HTTPException(
        status_code=400, detail=f'Invalid role `{role}` in chat history.'
      )

    result.append(message)

  return result


def _create_retrival_chain_with_lcel() -> RunnableSerializable[dict[str, Any], str]:
  from operator import itemgetter

  prompt_template = _get_prompt_template()
  llm_model = BaseAgent().get_model()
  output_parser = StrOutputParser()

  retriever = get_retriever()

  # This chain will be invoked with input dictionary ({'question': str})
  retrieval_chain = (
    # `RunnablePassthrough.assign` will add the output of the sub chain into
    # the input dictionary, then pipe into the next runnable
    RunnablePassthrough.assign(
      # itemgetter here simply get the value of `question` in the dictionary
      context=(itemgetter('question') | retriever | _format_docs)
    )
    | prompt_template
    | llm_model
    | output_parser
  )

  return retrieval_chain


def process_chat(chat_list: list[ChatHistoryDTO]) -> AIMessage:
  agent = BaseAgent()

  messages = _convert_chat_list(chat_list)
  agent_res = agent.chat(messages=messages)

  return agent_res


def process_chat_with_rag(chat_list: list[ChatHistoryDTO]) -> AIMessage:
  # Retrieve relevant documents
  user_query = chat_list[-1].content
  docs = get_retriever().invoke(user_query)
  context = _format_docs(docs=docs)

  # Generate prompt
  prompt_template = _get_prompt_template()
  message_list_with_context = prompt_template.format_messages(
    context=context, question=user_query
  )

  # Generate new message list
  new_chat_list = chat_list[:-1]
  for message in message_list_with_context:
    chat = ChatHistoryDTO(role='user', content=message.content)
    new_chat_list.append(chat)
  message_list = _convert_chat_list(new_chat_list)

  # Send message to LLM
  agent = BaseAgent()
  agent_res = agent.chat(messages=message_list)

  return agent_res


def process_chat_with_lcel(chat_list: list[ChatHistoryDTO]) -> AIMessage:
  user_query = chat_list[-1].content

  chain = _create_retrival_chain_with_lcel()
  result = chain.invoke({'question': user_query})

  return AIMessage(result)
