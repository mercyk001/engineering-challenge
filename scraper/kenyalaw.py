#import sys
#import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
from models.case import Case

class KenyaLawScraper:
    #BASE_URL = "https://kenyalaw.org/caselaw"...later check the website for more urls
    def __init__(self):
        self.base_url = "https://kenyalaw.org"
        self.session = None
        
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self 
    
    async def __aexit__(self, *args):
        await self.session.close()
        
    async def scrape_case_page(self, case_url: str) -> Optional[Case]:
        
        try:
            print(f"Scraping: {case_url}")
            
            
            async with self.session.get(case_url) as response:
                if response.status != 200:
                    print(f"Failed: {response.status}")
                    return None
                html = await response.text()
            
            
            soup = BeautifulSoup(html, 'html.parser')
            
           
            title = self._extract_title(soup)
            citation = self._extract_citation(soup)
            
            
            
            #DUMMY DATA
            
            case = Case(
                case_id=self._generate_case_id(citation),
                title=title or "case of YOOO and YAAA",
                citation=citation or "[2024] eKLR 1",
                court=self._extract_court(soup) or "High Court",
                judge=self._extract_judge(soup) or ["Justice Mercy "],
                judgement_date=self._extract_date(soup) or "2001-01-01",
                parties=self._extract_parties(soup) or {"plaintiff": ["Yooo"], "defendant": ["Yaaa"]},
                summary=self._extract_summary(soup) or "Case summary not available",
                url=case_url,
                pdf_url=self._extract_pdf_url(soup),
                raw_text=self._extract_full_text(soup) or "Full text not extracted"
            )
            
            print(f"Scraped: {case.title[:50]}...")
            return case
            
        except Exception as e:
            print(f"Error scraping! {case_url}: {e}")
            return None
    
    
    def _extract_title(self, soup):


        return "case of YOOO and YAAA"
    
    def _extract_citation(self, soup):
        """Extract case citation"""
        return "[2024] eKLR 1"
    
    def _extract_court(self, soup):
        return "High Court"
    
    def _extract_judge(self, soup):
        return ["Justice Mercy"]
    
    def _extract_date(self, soup):
        return "2001-01-01"
    
    def _extract_parties(self, soup):
        return {"plaintiff": ["Yooo"], "defendant": ["Yaaa"]}
    
    def _extract_summary(self, soup):
        return "Sample case summary"
    
    def _extract_pdf_url(self, soup):
        return None
    
    def _extract_full_text(self, soup):
        return "Full text of the case."
    
    def _generate_case_id(self, citation):
        """Generate a unique ID from citation"""
        if citation:
            return re.sub(r'[\[\]\s]', '_', citation.lower())
        return "case_unknown"  
        
           