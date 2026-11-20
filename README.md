# Meeting Briefing Agent

Enter a company or person and a meeting time, and the agent writes a one-page briefing of what happened in the 30 days before the meeting: news, launches, hires, funding and other updates. Every finding links to its sources, and each one is labeled by how well it is backed up. Built for the Global AI Hackathon, Tavily Research Agent track.

Demo video: ADD LINK HERE

## The problem

Preparing for a meeting means searching for recent news by hand and hoping you did not miss or misread something. This agent does the searching and writing, and keeps every claim tied to a real article so nothing is invented.

## How it works

1. It runs four Tavily news searches (latest news, launches, hiring and leadership, funding and partnerships), limited to the 30 days before the meeting. Duplicate links are removed.
2. The articles are numbered and sent to Gemini, which is told to use only those sources. It answers in a fixed structure: a summary, findings with source numbers, discussion points, and open questions.
3. The code then checks every finding against the real search results. A finding with no valid source number is dropped. A finding backed by two or more different websites is labeled verified, and anything else is labeled single source.
4. If no articles are found, the agent says so and does not call the model.

## Setup

Tested with Python X.Y.

```
git clone https://github.com/SujalNegi2007/meeting-briefing-agent.git
cd meeting-briefing-agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On Linux or macOS, use `source .venv/bin/activate` instead of the activate line above.

Create a file named `.env` in the project folder:

```
TAVILY_API_KEY=your-tavily-key
LLM_API_KEY=your-gemini-key
```

Get a Tavily key at tavily.com and a Gemini key from Google AI Studio.

## Run

```
streamlit run app.py
```

Open http://localhost:8501, enter a company or person, pick the meeting date and time, and click Generate briefing. For a person, fill in the context box (their company or role) so the search does not mix them up with someone else. The briefing can be downloaded as a Markdown file.

You can also run `python briefing.py` to print a sample briefing in the terminal.

## Files

- research.py: date window, search queries, Tavily search
- briefing.py: prompt, Gemini call, verification, output
- app.py: Streamlit page

## Limitations

- Tavily's published date is an estimate, and some articles have no date. Those are shown as "date unknown".
- "Verified" means two different websites report the claim. It does not prove the claim is true, so check the links before relying on it.
- The model can still misread a snippet, which is why every claim shows its sources.

## Tools and AI use

Tavily Search API, Google Gemini API (google-genai), Streamlit, Pydantic, python-dotenv.

Gemini is the AI in the product: it turns the search results into the briefing.
