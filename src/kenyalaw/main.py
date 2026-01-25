from __future__ import annotations
import asyncio
from pathlib import Path
import typer

from .pipeline import CrawlConfig, JudgmentsCrawler
from .storage.fs import FileStore
from .storage.elastic import ElasticIndexer

app = typer.Typer()

@app.command()
def crawl_judgments(
    es_url: str = "http://localhost:9200",
    out_dir: str = "./data",
):
    # Seed with one court list; expand to all courts/years next. :contentReference[oaicite:12]{index=12}
    cfg = CrawlConfig(
        seed_list_urls=[
            "https://new.kenyalaw.org/judgments/KESC/",
        ],
        concurrency=20,
    )
    fs = FileStore(root=Path(out_dir))
    es = ElasticIndexer(es_url=es_url, index_name="kenyalaw_docs")
    crawler = JudgmentsCrawler(cfg, fs, es)

    import asyncio
    asyncio.run(crawler.run())
    
    
  
  

if __name__ == "__main__":
    app()
