import os
from datetime import date, datetime, timedelta

from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel

from research import research

load_dotenv()
llm = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.5-flash"

# Uses pydantic here
class Finding(BaseModel):
    claim : str
    source_ids : list[int]

class Briefing(BaseModel):
    pass