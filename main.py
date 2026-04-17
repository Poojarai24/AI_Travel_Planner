import streamlit as st
import os
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.serpapi_tools import SerpApiTools

from config import GROQ_API_KEY, SERP_API_KEY

# API SETUP
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["SERP_API_KEY"] = SERP_API_KEY

# PAGE CONFIG
st.set_page_config(
    page_title="TripCraft-Travel Planner",
    page_icon="🌍",
    layout="wide"
)

#  GLOBAL CSS 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@400;500;600&display=swap');

/* ── Root tokens ── */
:root {
    --sand:   #F5F0E8;
    --clay:   #C8A882;
    --earth:  #8B6B4A;
    --deep:   #2C1F14;
    --sky:    #3B82C4;
    --mist:   #EAF1F8;
    --white:  #FFFFFF;
    --radius: 14px;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--sand) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--deep);
}

[data-testid="stSidebar"] {
    background-color: var(--deep) !important;
    border-right: none;
}
[data-testid="stSidebar"] * {
    color: var(--sand) !important;
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input,
[data-testid="stSidebar"] .stSelectSlider div,
[data-testid="stSidebar"] .stMultiSelect div {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(200,168,130,0.35) !important;
    border-radius: 8px !important;
    color: var(--sand) !important;
}

/* ── Hero header ── */
.rg-hero {
    text-align: center;
    padding: 3.5rem 1rem 2rem;
}
.rg-hero h1 {
    font-family: 'DM Serif Display', serif;
    font-size: clamp(2.6rem, 6vw, 4.2rem);
    color: var(--deep);
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin: 0 0 0.4rem;
}
.rg-hero h1 span {
    color: var(--earth);
    font-style: italic;
}
.rg-hero p {
    font-size: 1.05rem;
    color: #6B5B45;
    margin: 0;
    letter-spacing: 0.01em;
}

/* ── Generate button ── */
[data-testid="stButton"] > button {
    background: var(--deep) !important;
    color: var(--sand) !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.7rem 2.2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    transition: background 0.2s, transform 0.15s !important;
    cursor: pointer !important;
}
[data-testid="stButton"] > button:hover {
    background: var(--earth) !important;
    transform: translateY(-1px) !important;
}

/* ── Travel plan card ── */
.rg-plan-card {
    background: var(--white);
    border-radius: var(--radius);
    border: 1px solid rgba(139,107,74,0.15);
    padding: 2rem 2.5rem;
    margin-top: 1.5rem;
    box-shadow: 0 4px 24px rgba(44,31,20,0.07);
}
.rg-plan-card h2 {
    font-family: 'DM Serif Display', serif;
    color: var(--deep);
    font-size: 1.6rem;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Q&A section ── */
.rg-qa-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    color: var(--deep);
    margin-top: 0.5rem;
    margin-bottom: 0.3rem;
}
.rg-qa-answer {
    background: var(--mist);
    border-left: 3px solid var(--sky);
    border-radius: 0 var(--radius) var(--radius) 0;
    padding: 1rem 1.4rem;
    margin-top: 0.8rem;
    font-size: 0.97rem;
    line-height: 1.7;
}

/* ── Divider tweak ── */
hr {
    border-color: rgba(139,107,74,0.18) !important;
    margin: 2rem 0 !important;
}

/* ── Spinner override ── */
[data-testid="stSpinner"] p { color: var(--earth) !important; }

/* ── Markdown inside plan ── */
.rg-plan-card h3 { color: var(--earth); font-family: 'DM Serif Display', serif; }
.rg-plan-card a  { color: var(--sky); }

/* ── Sidebar label style ── */
[data-testid="stSidebar"] label { font-size: 0.88rem; opacity: 0.75; }
</style>
""", unsafe_allow_html=True)

#  LINK VALIDATION (parallel, fast) 
def _check_url(url):
    try:
        res = requests.head(url, timeout=2, allow_redirects=True)
        return url, res.status_code < 400
    except:
        return url, False

def validate_links(text):
    url_pattern = r"(https?://[^\s]+)"
    lines = text.split("\n")

    # Collect all URLs and which lines they appear on
    line_urls = []
    all_urls  = []
    for line in lines:
        urls = re.findall(url_pattern, line)
        line_urls.append(urls)
        all_urls.extend(urls)

    if not all_urls:
        return text

    # Check all URLs in parallel (max 10 workers, 2 s timeout each)
    results = {}
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(_check_url, u): u for u in set(all_urls)}
        for f in as_completed(futures):
            url, ok = f.result()
            results[url] = ok

    # Keep a line if it has no URLs, or at least one valid URL
    valid_lines = []
    for line, urls in zip(lines, line_urls):
        if not urls or any(results.get(u, False) for u in urls):
            valid_lines.append(line)

    return "\n".join(valid_lines)

#  SIDEBAR 
with st.sidebar:
    st.markdown("### Travel Planner")
    st.caption("Plan your perfect trip in seconds.")
    st.divider()

    destination = st.text_input("🌍 Where would you like to go?", "")
    duration    = st.number_input("📅 How many days?", 1, 30, 5)
    budget      = st.select_slider(
        "💰 Budget Level",
        options=["Budget", "Moderate", "Luxury"],
        value="Moderate"
    )
    travel_style = st.multiselect(
        "🎯 Travel Style",
        ["Culture", "Nature", "Adventure", "Relaxation", "Food", "Shopping"],
        ["Culture"]
    )
    st.divider()
    st.caption("Powered by Groq · LLaMA 3.3 · SerpAPI")

#  AGENT SETUP 
travel_agent = Agent(
    name="Travel Planner",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[SerpApiTools()],
    instructions=[
        "You are a travel planning assistant.",
        "Use SerpAPI to fetch real-time information.",
        "Always include actual clickable URLs from search results.",
        "Do NOT generate fake links.",
        "Do NOT include tool syntax like <function=...>.",
        "Return clean markdown with proper links."
    ],
    tool_choice="auto",
    show_tool_calls=False,
    markdown=True
)

#  SESSION STATE 
if "travel_plan" not in st.session_state:
    st.session_state.travel_plan = None

#  HERO 
st.markdown("""
<div class="rg-hero">
    <h1>Trip<span>Craft</span></h1>
    <p>Your AI travel companion — itineraries crafted in moments, memories made forever.</p>
</div>
""", unsafe_allow_html=True)

#  GENERATE BUTTON 
col1, col2, col3 = st.columns([1, 1.2, 1])
with col2:
    generate = st.button("✨ Generate My Itinerary", use_container_width=True)

if generate:
    if not destination:
        st.warning("Please enter a destination in the sidebar.")
    else:
        with st.spinner("🔍 Crafting your perfect trip..."):
            prompt = f"""
            Create a detailed {duration}-day travel plan for {destination}.

            Budget: {budget}
            Travel Style: {', '.join(travel_style)}

            IMPORTANT:
            - Use real-time data when needed
            - Prefer reliable links
            - Avoid broken or outdated links

            Include:
            - Best time to visit
            - Hotel recommendations
            - Day-wise itinerary
            - Restaurants
            - Local transport
            - Estimated total cost
            """
            try:
                response = travel_agent.run(prompt)
            except Exception as e:
                st.warning("⚠️ Tool call failed. Retrying safely...")
                fallback_prompt = f"""
                Create a {duration}-day travel plan for {destination}.
                Provide useful suggestions. Links are optional.
                """
                response = travel_agent.run(fallback_prompt)
                with open("error.txt", "a", encoding="utf-8") as f:
                    f.write("\n--- TOOL FAILURE ---\n")
                    f.write(str(e) + "\n")

            if hasattr(response, "content") and response.content:
                clean_output = response.content.replace("∣", "|").strip()
                clean_output = validate_links(clean_output)
                st.session_state.travel_plan = clean_output
                # No st.rerun() — plan renders immediately below
            else:
                st.error("No response generated. Please try again.")

#  SHOW PLAN 
if st.session_state.travel_plan:
    # st.markdown('<div class="rg-plan-card"><h2>🧳 Your Itinerary</h2>', unsafe_allow_html=True)
    st.markdown(st.session_state.travel_plan)
    st.markdown('</div>', unsafe_allow_html=True)

# Q&A 
st.divider()
st.markdown('<p class="rg-qa-header">🤔 Have a question about your trip?</p>', unsafe_allow_html=True)

question = st.text_input("", placeholder="e.g. What's the best way to get from the airport?")

col_a, col_b, col_c = st.columns([1, 0.8, 1])
with col_b:
    ask = st.button("Get Answer", use_container_width=True)

if ask:
    if not st.session_state.travel_plan:
        st.warning("Generate a travel plan first.")
    elif not question:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Finding answer..."):
            short_context = "\n".join(st.session_state.travel_plan.split("\n")[:40])
            context_prompt = f"""
            You are answering questions based on a travel plan.

            Travel Plan:
            {short_context}

            User Question:
            {question}

            Give a clear, helpful answer based ONLY on the travel plan.
            """
            try:
                response = travel_agent.run(context_prompt)
                if hasattr(response, "content") and response.content:
                    st.markdown('<div class="rg-qa-answer">', unsafe_allow_html=True)
                    st.markdown(response.content)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("No answer generated.")
            except Exception as e:
                st.error("Error while answering question.")
                with open("error.txt", "a", encoding="utf-8") as f:
                    f.write("\n--- TOOL FAILURE ---\n")
                    f.write(str(e) + "\n")