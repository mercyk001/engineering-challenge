from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, List

from .http_client import HttpClient
from .models import DocumentRef, DocumentRecord
from .parsing.judgments import parse_list_page_for_case_links, parse_detail_page, canonical_doc_id
from .parsing.parties import extract_parties_from_title
from .storage.fs import FileStore
from .storage.elastic import ElasticIndexer

@dataclass
class CrawlConfig:
    base_url: str = "https://new.kenyalaw.org"
    # Example entrypoint: Supreme Court list page :contentReference[oaicite:10]{index=10}
    seed_list_urls: List[str] = None
    concurrency: int = 20

class JudgmentsCrawler:
    def __init__(self, cfg: CrawlConfig, fs: FileStore, es: ElasticIndexer) -> None:
        self.cfg = cfg
        self.fs = fs
        self.es = es

    async def discover(self, http: HttpClient) -> List[DocumentRef]:
        refs: List[DocumentRef] = []
        for list_url in self.cfg.seed_list_urls:
            html = await http.get_text(list_url)
            links = parse_list_page_for_case_links(html, base_url=self.cfg.base_url)
            for u in links:
                refs.append(DocumentRef(source="judgments", url=u, doc_id=canonical_doc_id(u)))
        # TODO: paginate (follow “Next” links), and expand by year/court.
        return refs

    async def fetch_one(self, http: HttpClient, ref: DocumentRef) -> DocumentRecord:
        html = await http.get_text(ref.url)
        title, metadata, pdf_url, docx_url = parse_detail_page(html, ref.url, base_url=self.cfg.base_url)

        parties = extract_parties_from_title(title)

        pdf_path = None
        checksum = None
        if pdf_url:
            pdf_bytes = await http.download_bytes(pdf_url)
            path = self.fs.pdf_path(ref.doc_id)
            checksum = self.fs.write_bytes_if_missing(path, pdf_bytes)
            pdf_path = str(path)

        # Raw text strategy (scaffold):
        # 1) Prefer DOCX download + docx text extract (often small and clean) :contentReference[oaicite:11]{index=11}
        # 2) Else parse HTML body text
        raw_text = html  # TODO: replace with cleaned extracted text

        return DocumentRecord(
            doc_id=ref.doc_id,
            source=ref.source,
            url=ref.url,
            title=title,
            raw_text=raw_text,
            metadata=metadata,
            parties=parties,
            pdf_url=pdf_url,
            docx_url=docx_url,
            pdf_path=pdf_path,
            checksum=checksum,
        )

    async def run(self) -> None:
        self.es.ensure_index()

        async with HttpClient(concurrency=self.cfg.concurrency) as http:
            refs = await self.discover(http)

            # bounded concurrency via gather chunks
            batch: List[DocumentRecord] = []
            sem = asyncio.Semaphore(self.cfg.concurrency)

            async def worker(r: DocumentRef) -> None:
                async with sem:
                    rec = await self.fetch_one(http, r)
                    batch.append(rec)

            tasks = [asyncio.create_task(worker(r)) for r in refs]
            await asyncio.gather(*tasks)

        # Bulk index
        self.es.bulk_upsert([rec.__dict__ for rec in batch])
