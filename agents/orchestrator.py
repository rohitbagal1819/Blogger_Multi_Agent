"""Plans the work before the other agents run."""
from .common import BlogState, ask

def orchestrator(state: BlogState) -> dict:
    print("\n[Orchestrator] Planning the blog...")
    plan = ask(
        "Create a concise plan for a helpful, accurate blog article. "
        "Include audience, key questions, and suggested sections.\n"
        f"Topic: {state['topic']}"
    )
    return {"plan": plan}
