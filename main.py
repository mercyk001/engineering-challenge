import asyncio
import json
from datetime import datetime
from scraper.kenyalaw import KenyaLawScraper

async def test_scraper():
   
    
    test_urls = [
        "http://kenyalaw.org/caselaw",  #exampleurl
        
    ]
    
    async with KenyaLawScraper() as scraper:
        cases = []
        
        for url in test_urls:
            case = await scraper.scrape_case_page(url)
            if case:
                cases.append(case.to_dict())
        
        
        if cases:
            filename = f"data/test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(cases, f, indent=2)
            print(f"\n Saved {len(cases)} cases to {filename}")
        else:
            print("\n No cases scraped")
        
        return cases

if __name__ == "__main__":
    print("Testing Kenya Law Scraper.")
    asyncio.run(test_scraper())