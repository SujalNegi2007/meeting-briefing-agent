import os
from dotenv import load_dotenv
from tavily import TavilyClient 

load_dotenv()
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
response = client.search("Tavily Latest News", max_results=3)
for r in response["results"]:
    print(r["title"], r["url"])