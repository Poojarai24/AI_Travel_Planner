import streamlit as st
import os

from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.serpapi_tools import SerpApiTools

from config import GROQ_API_KEY, SERP_API_KEY

# Set API keys securely from .env
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["SERP_API_KEY"] = SERP_API_KEY

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🌎",
    layout="wide"
)

with st.sidebar:
    st.title("Trip Settings")

    destination = st.text_input("🌍 Where would you like to go?", "")
    duration = st.number_input("📅 How many days?", 1, 30, 5)

    budget = st.select_slider(
        "💰 Budget Level",
        options=["Budget", "Moderate", "Luxury"],
        value="Moderate"
    )

    travel_style = st.multiselect(
        "🎯 Travel Style",
        ["Culture", "Nature", "Adventure", "Relaxation", "Food", "Shopping"],
        ["Culture"]
    )

travel_agent = Agent(
    name="Travel Planner",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[SerpApiTools()],
    instructions=[
        "You are a travel planning assistant.",
        "Research destinations and provide live links.",
        "Always verify current information.",
        "Give working source links."
    ],
    show_tool_calls=True,
    markdown=True
)

if "travel_plan" not in st.session_state:
    st.session_state.travel_plan = None

st.title("🌎 AI Travel Planner")

if st.button("✨ Generate Travel Plan"):

    if not destination:
        st.warning("Please enter a destination.")
    else:
        with st.spinner("🔍 Planning your trip..."):

            prompt = f"""
            Create a detailed {duration}-day travel plan for {destination}.

            Budget: {budget}
            Travel Style: {', '.join(travel_style)}

            Include:
            - Best time to visit
            - Hotel recommendations
            - Day-wise itinerary
            - Restaurants
            - Local transport
            - Estimated total cost
            - Live reference links
            """

            response = travel_agent.run(prompt)

            if hasattr(response, "content"):
                st.session_state.travel_plan = response.content
                st.markdown(response.content)
            else:
                st.session_state.travel_plan = str(response)
                st.markdown(str(response))


st.divider()

# question = st.text_input("🤔 Ask something about your trip")

# if st.button("Get Answer"):

#     if not st.session_state.travel_plan:
#         st.warning("Generate travel plan first.")
#     elif not question:
#         st.warning("Please enter a question.")
#     else:
#         with st.spinner("Finding answer..."):

#             context_prompt = f"""
#             Here is the existing travel plan:
#             {st.session_state.travel_plan}

#             Answer this question clearly:
#             {question}
#             """

#             response = travel_agent.run(context_prompt)

#             if hasattr(response, "content"):
#                 st.markdown(response.content)
#             else:
#                 st.markdown(str(response))
