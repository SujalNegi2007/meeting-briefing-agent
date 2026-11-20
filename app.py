from datetime import datetime

import streamlit as st

from briefing import generate, to_markdown

st.set_page_config(page_title="Meeting Briefing Agent", layout="centered")

st.title("Meeting Briefing Agent")
st.write(
    "Enter who you are meeting and when. You get a one-page briefing of the "
    "30 days before the meeting, with sources for every claim."
)

name = st.text_input("Company or person")
context = st.text_input(
    "Context (optional)",
    placeholder="For a person: their company or role",
)

col1, col2 = st.columns(2)
meeting_date = col1.date_input("Meeting date")
meeting_time = col2.time_input("Meeting time")

if st.button("Generate briefing", type="primary"):
    if not name.strip():
        st.warning("Please enter a company or person.")
    else:
        meeting_dt = datetime.combine(meeting_date, meeting_time)
        with st.spinner("Researching the last 30 days..."):
            try:
                report = generate(name.strip(), meeting_dt, context.strip())
                st.session_state["markdown"] = to_markdown(report)
            except Exception as error:
                st.error(f"Something went wrong: {error}")

# Kept in session_state so the briefing stays visible after the download button reruns the page
if "markdown" in st.session_state:
    st.markdown(st.session_state["markdown"])
    st.download_button(
        "Download briefing (.md)",
        st.session_state["markdown"],
        file_name="briefing.md",
    )
