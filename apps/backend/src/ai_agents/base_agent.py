import os

from langchain.chat_models import BaseChatModel
from langchain.messages import AIMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage


class BaseAgent:
  __model: BaseChatModel

  def __init__(self):
    api_key = os.getenv('ANTHROPIC_API_KEY')
    self.__model = ChatAnthropic(
      api_key=api_key, temperature=0, model_name='claude-sonnet-4-6'
    )

  def chat(self, messages: list[BaseMessage]) -> AIMessage:
    res = self.__model.invoke(input=messages)
    message = res.content
    return AIMessage(content=message)

  def get_model(self) -> BaseChatModel:
    return self.__model
