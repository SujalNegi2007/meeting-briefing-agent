import json
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
response = client.search("Zomato Latest News", topic="news", max_results=3)
print(json.dumps(response, indent=2))