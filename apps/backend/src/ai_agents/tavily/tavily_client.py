import os

from fastapi import HTTPException
from langchain_tavily import TavilyCrawl, TavilyExtract, TavilyMap
from pydantic import BaseModel


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


class TavilyCrawlResult(BaseModel):
  """Tavily crawl result for individual document"""

  url: str
  raw_content: str


class TavilyCrawlResponse(BaseModel):
  """Tavily API response for crawling documents"""

  base_url: str
  results: list[TavilyCrawlResult]
  response_time: float
  request_id: str
