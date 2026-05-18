import os
from typing import Any

from ai_agents.tavily.tavily_crawl import TavilyCrawlResponse
from fastapi import HTTPException
from langchain_tavily import TavilyCrawl, TavilyExtract, TavilyMap
from server_config.logger import Logger


class TavilyClient:
  crawler: TavilyCrawl
  extractor: TavilyExtract
  mapper: TavilyMap

  def __init__(self):
    API_KEY = os.getenv('TAVILY_API_KEY')

    if API_KEY is None:
      raise HTTPException(status_code=500, detail='Tavily is not configured.')

    self.crawler = TavilyCrawl(api_key=API_KEY)
    self.mapper = TavilyMap(api_key=API_KEY)
    self.extractor = TavilyExtract(api_key=API_KEY)

  def parse_crawler_response(raw_response: Any) -> TavilyCrawlResponse:
    logger = Logger(__name__)

    if not isinstance(raw_response, dict):
      message = f'Invalid raw_response: {raw_response}'
      logger.error(message)
      raise ValueError(message)

    if 'error' in raw_response:
      error = raw_response['error']
      logger.error(error)
      raise error

    return TavilyCrawlResponse.model_validate(raw_response, strict=True)
