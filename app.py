# import streamlit as st
# import os
# import requests
# import re

# from phi.agent import Agent
# from phi.model.groq import Groq
# from phi.tools.serpapi_tools import SerpApiTools

# from config import GROQ_API_KEY, SERP_API_KEY

# # API SETUP 
# os.environ["GROQ_API_KEY"] = GROQ_API_KEY
# os.environ["SERP_API_KEY"] = SERP_API_KEY

# # PAGE CONFIG 
# st.set_page_config(
#     page_title="TripCraft-Travel Planner",
#     page_icon="🌎",
#     layout="wide"
# )

# # LINK VALIDATION 
# def validate_links(text):
#     url_pattern = r"(https?://[^\s]+)"
#     valid_lines = []

#     for line in text.split("\n"):
#         urls = re.findall(url_pattern, line)

#         if urls:
#             valid = False
#             for url in urls:
#                 try:
#                     res = requests.head(url, timeout=3)
#                     if res.status_code < 400:
#                         valid = True
#                         break
#                 except:
#                     continue

#             if valid:
#                 valid_lines.append(line)
#         else:
#             valid_lines.append(line)

#     return "\n".join(valid_lines)

# # SIDEBAR 
# with st.sidebar:
#     st.title("Trip Settings")

#     destination = st.text_input("🌍 Where would you like to go?", "")
#     duration = st.number_input("📅 How many days?", 1, 30, 5)

#     budget = st.select_slider(
#         "💰 Budget Level",
#         options=["Budget", "Moderate", "Luxury"],
#         value="Moderate"
#     )

#     travel_style = st.multiselect(
#         "🎯 Travel Style",
#         ["Culture", "Nature", "Adventure", "Relaxation", "Food", "Shopping"],
#         ["Culture"]
#     )

# #AGENT SETUP 
# travel_agent = Agent(
#     name="Travel Planner",
#     model=Groq(id="llama-3.3-70b-versatile"),
#     tools=[SerpApiTools()],
#     instructions=[
#         "You are a travel planning assistant.",
#         "Use SerpAPI to fetch real-time information.",
#         "Always include actual clickable URLs from search results.",
#         "Do NOT generate fake links.",
#         "Do NOT include tool syntax like <function=...>.",
#         "Return clean markdown with proper links."
#     ],
#     tool_choice="auto",
#     show_tool_calls=False,
#     markdown=True
# )

# # SESSION 
# if "travel_plan" not in st.session_state:
#     st.session_state.travel_plan = None

# # UI 
# st.title("AI Travel Planner")

# # MAIN GENERATION 
# if st.button("✨ Generate Travel Plan"):

#     if not destination:
#         st.warning("Please enter a destination.")
#     else:
#         with st.spinner("🔍 Planning your trip..."):

#             prompt = f"""
#             Create a detailed {duration}-day travel plan for {destination}.

#             Budget: {budget}
#             Travel Style: {', '.join(travel_style)}

#             IMPORTANT:
#             - Use real-time data when needed
#             - Prefer reliable links
#             - Avoid broken or outdated links

#             Include:
#             - Best time to visit
#             - Hotel recommendations
#             - Day-wise itinerary
#             - Restaurants
#             - Local transport
#             - Estimated total cost
#             """

#             try:
#                 response = travel_agent.run(prompt)

#             except Exception as e:
#                 st.warning("⚠️ Tool call failed. Retrying safely...")

#                 # fallback without tool pressure
#                 fallback_prompt = f"""
#                 Create a {duration}-day travel plan for {destination}.
#                 Provide useful suggestions. Links are optional.
#                 """

#                 response = travel_agent.run(fallback_prompt)

#                 # log error
#                 with open("error.txt", "a", encoding="utf-8") as f:
#                     f.write("\n--- TOOL FAILURE ---\n")
#                     f.write(str(e) + "\n")

#             # OUTPUT 
#             if hasattr(response, "content") and response.content:
#                 clean_output = response.content.replace("∣", "|").strip()
#                 clean_output = validate_links(clean_output)

#                 st.session_state.travel_plan = clean_output
#                 st.rerun() # Refresh to show only the plan in the "SHOW EXISTING PLAN" section

#             else:
#                 st.error("No response generated. Try again.")

# # SHOW EXISTING PLAN 
# if st.session_state.travel_plan:
#     st.markdown("## 🧳 Your Travel Plan")
#     st.markdown(st.session_state.travel_plan)

# # Q&A (SAFE VERSION) -
# st.divider()

# question = st.text_input("🤔 Ask something about your trip")

# if st.button("Get Answer"):

#     if not st.session_state.travel_plan:
#         st.warning("Generate travel plan first.")
#     elif not question:
#         st.warning("Please enter a question.")
#     else:
#         with st.spinner("Finding answer..."):

#             # 🔥 LIMIT CONTEXT SIZE (IMPORTANT FIX)
#             short_context = "\n".join(st.session_state.travel_plan.split("\n")[:40])

#             context_prompt = f"""
#             You are answering questions based on a travel plan.

#             Travel Plan:
#             {short_context}

#             User Question:
#             {question}

#             Give a clear, helpful answer based ONLY on the travel plan.
#             """

#             try:
#                 response = travel_agent.run(context_prompt)

#                 if hasattr(response, "content") and response.content:
#                     st.info("### 💡 Q&A Response")
#                     st.markdown(response.content)
#                 else:
#                     st.warning("No answer generated.")

#             except Exception as e:
#                 st.error("Error while answering question.")

#                 with open("error.txt", "a", encoding="utf-8") as f:
#                     f.write("\n--- TOOL FAILURE ---\n")
#                     f.write(str(e) + "\n")

import streamlit as st
import os

from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.serpapi_tools import SerpApiTools

from config import GROQ_API_KEY, SERP_API_KEY

os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["SERP_API_KEY"] = SERP_API_KEY

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🌎",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  h1, h2, h3 { font-family: 'DM Serif Display', serif; }

  .chat-bubble-user {
      background: #1a1a2e; color: #e0e0ff;
      border-radius: 18px 18px 4px 18px;
      padding: 12px 18px; margin: 6px 0; max-width: 75%; float: right; clear: both;
  }
  .chat-bubble-assistant {
      background: #f0f4ff; color: #1a1a2e;
      border-radius: 18px 18px 18px 4px;
      padding: 12px 18px; margin: 6px 0; max-width: 85%; float: left; clear: both;
  }
  .chat-wrap { overflow: hidden; margin-bottom: 8px; }
  .plan-badge {
      background: #e8f5e9; border-left: 4px solid #43a047;
      padding: 10px 16px; border-radius: 8px;
      font-size: 0.85rem; color: #2e7d32; margin-bottom: 12px;
  }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("messages", []),          # chat history list of {role, content}
    ("travel_plan_summary", None),  # short summary used as context
    ("plan_destination", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Agent ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_agent():
    return Agent(
        name="Travel Planner",
        model=Groq(id="llama-3.3-70b-versatile"),
        tools=[SerpApiTools()],
        instructions=[
            "You are a friendly, concise travel planning assistant.",
            "Keep responses focused and under 800 words unless building an itinerary.",
            "Always include 1-2 working reference links when relevant.",
            "For itineraries, use Day-wise markdown structure.",
        ],
        show_tool_calls=False,
        markdown=True,
    )

travel_agent = get_agent()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("✈️ Trip Settings")
    st.caption("Configure your trip then hit **Generate Plan**.")

    destination = st.text_input("🌍 Destination", placeholder="e.g. Goa, Tokyo, Paris")
    duration    = st.number_input("📅 Days", 1, 30, 5)
    budget      = st.select_slider("💰 Budget", ["Budget", "Moderate", "Luxury"], value="Moderate")
    travel_style = st.multiselect(
        "🎯 Travel Style",
        ["Culture", "Nature", "Adventure", "Relaxation", "Food", "Shopping"],
        default=["Culture"],
    )

    generate_clicked = st.button("✨ Generate Travel Plan", use_container_width=True)

    if st.session_state.plan_destination:
        st.divider()
        st.success(f"Plan ready for **{st.session_state.plan_destination}**")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.travel_plan_summary = None
            st.session_state.plan_destination = None
            st.rerun()

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("🌎 AI Travel Planner")
st.caption("Generate a plan, then chat to refine it — ask about restaurants, costs, transport, alternatives, anything.")

# ── Generate Plan ─────────────────────────────────────────────────────────────
if generate_clicked:
    if not destination:
        st.warning("Please enter a destination first.")
    else:
        prompt = f"""
Create a detailed {duration}-day travel plan for {destination}.
Budget: {budget} | Travel Style: {', '.join(travel_style)}

Include:
- Best time to visit
- 2-3 hotel recommendations with rough prices
- Day-wise itinerary (brief per day)
- Must-try restaurants
- Local transport tips
- Estimated total cost
- 2-3 reference links

Keep the response well-structured in markdown. Be concise but complete.
"""
        with st.spinner("🔍 Researching your trip…"):
            try:
                response = travel_agent.run(prompt)
                plan_text = response.content if hasattr(response, "content") else str(response)

                # Store a truncated summary as context (avoid token overflow on follow-ups)
                summary_prompt = f"""
Summarize the following travel plan in 300 words, keeping:
- Destination, duration, budget
- Key hotels (names only)
- Day-wise highlights (1 line each)
- Estimated total cost

Travel Plan:
{plan_text[:3000]}
"""
                summary_resp = travel_agent.run(summary_prompt)
                summary = summary_resp.content if hasattr(summary_resp, "content") else plan_text[:1000]

                st.session_state.travel_plan_summary = summary
                st.session_state.plan_destination = destination
                st.session_state.messages = [
                    {"role": "assistant", "content": plan_text}
                ]
            except Exception as e:
                st.error(f"Failed to generate plan: {e}")

# ── Chat History Display ──────────────────────────────────────────────────────
if st.session_state.messages:
    if st.session_state.travel_plan_summary:
        st.markdown(
            f'<div class="plan-badge">📋 Active plan: <b>{st.session_state.plan_destination}</b> — '
            f'chat below to ask follow-up questions.</div>',
            unsafe_allow_html=True,
        )

    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="🌎"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("user", avatar="🧑‍💼"):
                st.markdown(msg["content"])

# ── Chat Input ────────────────────────────────────────────────────────────────
user_input = st.chat_input(
    "Ask anything about your trip…" if st.session_state.travel_plan_summary
    else "Generate a travel plan first, then ask questions here…"
)

if user_input:
    if not st.session_state.travel_plan_summary:
        st.warning("Please generate a travel plan first using the sidebar.")
    else:
        # Show user message immediately
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🧑‍💼"):
            st.markdown(user_input)

        # Build context-aware prompt using the SHORT summary (not full plan)
        context_prompt = f"""
You are helping a traveller plan their trip to {st.session_state.plan_destination}.

Here is a summary of their existing travel plan:
---
{st.session_state.travel_plan_summary}
---

Now answer this follow-up question clearly and concisely (under 400 words unless a new itinerary is requested):
{user_input}
"""
        with st.chat_message("assistant", avatar="🌎"):
            with st.spinner("Thinking…"):
                try:
                    response = travel_agent.run(context_prompt)
                    answer = response.content if hasattr(response, "content") else str(response)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    err_msg = f"⚠️ Error: {e}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})