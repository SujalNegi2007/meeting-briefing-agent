from datetime import date, datetime, timedelta
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Here meeting_dt is a date like 2026-11-20 10:00:00
def get_window(meeting_dt):
    # Here we get start date which is 30 days before meeting date
    start = meeting_dt.date() - timedelta(days=30)
    # Here we get end date which is min b/w current date and meeting date as if meeting date is next week then we can't get articles from future.
    end = min(meeting_dt.date(), date.today())
    # Here converts python date object into exact string format like 2026-11-20T10:00:00 where T divides time and date 
    return start.isoformat(), end.isoformat()

# Checking if it is working correctly
# print(get_window(datetime(2026,11,20,10,15,5)))

def build_queries(name, context=""):
    subject = f"{name} {context}".strip()
    return [
        ("news", f"{subject} Latest News"),
        ("launch", f"{subject} product launch announcement"),
        ("hiring", f"{subject} appoints hires leadership"),
        ("funding", f"{subject} funding partnership acquisition"),
    ]

# Search Function
def search_one(query, start, end):
    response = client.search(query=query, topic="news", start_date=start, end_date=end, max_results=5)
    return response["results"]

# Main Function
def research(name, meeting_dt, context = ""):
    start, end = get_window(meeting_dt)
    seen_urls = set()
    findings = []
    
    for label, query in build_queries(name, context):
        try:
            results = search_one(query, start, end)
        except Exception as e:
            print(f"Search Failed for {query}: {e}")
            continue
        for r in results:
            url = r["url"]
            if url in seen_urls:
                continue
            seen_urls.add(url)
            findings.append({
                "title" : r["title"],
                "url" : url,
                # Here used r.get() instead of r[] because r[] will simply crash when published_date is not present.
                "date" : r.get("published_date"),
                "snippet" : r["content"],
                "found_by" : label,
            })
    return findings

if __name__ == "__main__":
    meeting = datetime(2026, 11, 20, 10, 0)
    for f in research("Zomato", meeting):
        print(f["date"], "|", f["title"])
        print("     ", f["url"])