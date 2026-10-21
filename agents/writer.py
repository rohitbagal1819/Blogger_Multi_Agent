"""Writes a Blogger-ready article."""
from .common import BlogState, ask_json

def writer(state: BlogState) -> dict:
    feedback = ""
    if state.get("review"):
        print("[Writer] Regenerating article with reviewer feedback...")
        feedback = f"\nPrevious review notes to address and improve upon:\n{state['review']}"
    else:
        print("[Writer] Drafting the article...")

    article = ask_json(
        "Write an original, clear blog post as simple Blogger body HTML. "
        "Return JSON with exactly: title, content. Use headings, paragraphs, "
        "lists when useful. No Markdown fences, scripts, forms, or iframes.\n"
        f"Topic: {state['topic']}\nPlan: {state['plan']}\nResearch: {state['research']}{feedback}"
    )
    if not article.get("title") or not article.get("content"):
        raise RuntimeError("Writer response must include title and content.")
    return {"title": article["title"], "content": article["content"]}
