from pydantic import BaseModel


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
