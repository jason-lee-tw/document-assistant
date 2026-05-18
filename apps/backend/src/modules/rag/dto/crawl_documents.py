from pydantic import BaseModel


class CrawlDocumentsReqDTO(BaseModel):
  url_list: list[str]


class CrawlDocumentSummaryDTO(BaseModel):
  number_of_document: int
  number_of_chunk: int


class CrawlDocumentDetailDTO(BaseModel):
  document_id_list: list[str]
  chunk_id_list: list[str]


class CrawlDocumentsResDTO(BaseModel):
  summary: CrawlDocumentSummaryDTO
  detail: CrawlDocumentDetailDTO


def generate_crawl_document_res_dto(
  document_id_list: list[str], chunk_id_list: list[str]
) -> CrawlDocumentsResDTO:
  summary = CrawlDocumentSummaryDTO(
    number_of_document=len(document_id_list),
    number_of_chunk=len(chunk_id_list),
  )
  detail = CrawlDocumentDetailDTO(
    document_id_list=document_id_list,
    chunk_id_list=chunk_id_list,
  )
  return CrawlDocumentsResDTO(
    summary=summary,
    detail=detail,
  )
