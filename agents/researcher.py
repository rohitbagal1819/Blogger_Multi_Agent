"""Researches a topic with Gemini Google Search grounding."""
from .common import BlogState, ask

def researcher(state: BlogState) -> dict:
    print("[Researcher] Finding current information...")
    research = ask(
        "Research the topic thoroughly. Summarize key facts, definitions, "
        "and context accurately. Do not invent sources.\n"
        f"Topic: {state['topic']}\nPlan: {state['plan']}",
        search=False,
    )
    return {"research": research}
