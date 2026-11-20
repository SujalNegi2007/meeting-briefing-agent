import os
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

from research import research

load_dotenv()
llm = genai.Client(api_key=os.getenv("LLM_API_KEY"))

# Copy an exact Flash model name from Google AI Studio if this one is not available.
MODEL = "gemini-3.5-flash"


# ---------- The structure the LLM must answer in ----------

class Finding(BaseModel):
    claim: str
    source_ids: list[int]


class Briefing(BaseModel):
    summary: str
    findings: list[Finding]
    discussion_points: list[str]
    open_questions: list[str]


# ---------- Prompt ----------

def format_sources(sources):
    blocks = []
    for number, s in enumerate(sources, start=1):
        date_text = s["date"] or "unknown"
        blocks.append(f"[{number}] {s['title']} (date: {date_text})\n{s['snippet'][:600]}")
    return "\n\n".join(blocks)


def build_prompt(name, meeting_dt, context, sources_text):
    context_line = f"Extra context: {context}\n" if context else ""
    return f"""You are preparing a one-page pre-meeting briefing.

Subject: {name}
{context_line}Meeting date: {meeting_dt.date()}

Below are numbered sources from the 30 days before the meeting.
Use ONLY these sources.

Rules:
- Every finding must be a factual claim supported by the sources.
  List the numbers of the supporting sources in source_ids.
- Never add facts that are not in the sources. If the sources do not say it, leave it out.
- Mention dates only when a source gives them. Never guess a date.
- Ignore sources that are clearly about a different company or person.
- If the sources are thin or off-topic, say so in the summary and return few or no findings.
- discussion_points and open_questions should be useful things to raise in the meeting, based on the findings.
- Keep it short: at most 6 findings, 3 to 4 discussion points, 3 to 4 open questions.

Sources:
{sources_text}
"""


# ---------- LLM call (with retries) ----------

def write_briefing(name, meeting_dt, context, sources):
    prompt = build_prompt(name, meeting_dt, context, format_sources(sources))
    last_error = None

    for attempt in range(3):
        try:
            response = llm.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": Briefing,
                    "temperature": 0.2,
                },
            )
            if response.parsed is not None:
                return response.parsed
            last_error = ValueError(f"Empty answer from the model: {response.text}")
        except Exception as error:
            last_error = error
        time.sleep(2 * (attempt + 1))

    raise RuntimeError(f"The language model failed after 3 tries: {last_error}")


# ---------- Verification ----------

def domain_of(url):
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def verify_findings(briefing, sources):
    """Check every claim against the real search results.

    - Source numbers that do not exist are ignored.
    - A claim with no valid source is removed.
    - A claim backed by 2+ different websites is 'verified'; otherwise 'single source'.
    """
    checked = []
    removed = 0

    for item in briefing.findings:
        valid_ids = []
        for number in item.source_ids:
            if 1 <= number <= len(sources) and number not in valid_ids:
                valid_ids.append(number)

        if not valid_ids:
            removed += 1
            continue

        cited = [sources[n - 1] for n in valid_ids]
        domains = {domain_of(s["url"]) for s in cited}
        status = "verified" if len(domains) >= 2 else "single source"
        checked.append({"claim": item.claim, "status": status, "sources": cited})

    # Verified claims first (sort is stable, so the rest keep their order)
    checked.sort(key=lambda c: c["status"] != "verified")
    return checked, removed


# ---------- Main entry point ----------

def generate(name, meeting_dt, context=""):
    sources = research(name, meeting_dt, context)

    if not sources:
        return {
            "name": name,
            "meeting_dt": meeting_dt,
            "summary": f"No recent news was found for {name} in the 30 days before the meeting.",
            "findings": [],
            "discussion_points": [],
            "open_questions": [],
            "removed": 0,
            "source_count": 0,
        }

    briefing = write_briefing(name, meeting_dt, context, sources)
    findings, removed = verify_findings(briefing, sources)

    return {
        "name": name,
        "meeting_dt": meeting_dt,
        "summary": briefing.summary,
        "findings": findings,
        "discussion_points": briefing.discussion_points,
        "open_questions": briefing.open_questions,
        "removed": removed,
        "source_count": len(sources),
    }


# ---------- Output ----------

def clean_title(title):
    return title.replace("[", "(").replace("]", ")")


def to_markdown(report):
    lines = [
        f"# Briefing: {report['name']}",
        f"Meeting: {report['meeting_dt']:%d %b %Y, %H:%M}",
        "",
        "## Summary",
        report["summary"],
        "",
        "## Findings",
    ]

    if not report["findings"]:
        lines.append("No findings could be backed by the sources.")

    for item in report["findings"]:
        if item["status"] == "verified":
            label = "Verified (2+ independent sources)"
        else:
            label = "Single source, double-check before relying on it"
        lines.append(f"- **{label}:** {item['claim']}")
        for s in item["sources"]:
            lines.append(f"  - {s['date'] or 'date unknown'}: [{clean_title(s['title'])}]({s['url']})")

    lines += ["", "## Discussion points"]
    lines += [f"- {point}" for point in report["discussion_points"]] or ["- None"]

    lines += ["", "## Open questions"]
    lines += [f"- {question}" for question in report["open_questions"]] or ["- None"]

    note = f"Based on {report['source_count']} articles from the 30 days before the meeting."
    if report["removed"]:
        note += f" {report['removed']} claim(s) without a valid source were removed."
    lines += ["", "---", note]

    return "\n".join(lines)


if __name__ == "__main__":
    meeting = datetime.now() + timedelta(days=2)
    print(to_markdown(generate("Zomato", meeting)))
