"""Reviews the draft and asks before any publication."""
import re
from html import unescape
from .common import BlogState, ask_json


def reviewer(state: BlogState) -> dict:
    print("[Reviewer] Reviewing the article...")

    article = ask_json(
        "Review and improve this blog for clarity, structure, and readability. "
        "Keep the HTML safe: no scripts, forms, or iframes. "
        "Return JSON with exactly: title, content, review.\n"
        f"Research: {state['research']}\nTitle: {state['title']}\nHTML: {state['content']}"
    )

    title = article.get("title")
    content = article.get("content")
    notes = article.get("review") or "No review notes returned."

    if not title or not content:
        raise RuntimeError("Reviewer response must include title and content.")

    preview = unescape(re.sub(r"<[^>]+>", " ", content))

    print("\nReview notes:")
    print(notes)
    print(f"\nTitle: {title}")
    print("\nPreview:")
    print(preview[:1800])

    while True:
        answer = input("\nPublish to Blogger? (yes/no): ").strip().lower()
        if answer == "yes":
            return {
                "title": title,
                "content": content,
                "review": notes,
                "approved": True,
                "cancelled": False,
            }
        if answer == "no":
            print("\n[Reviewer] Blog publish nahi karna hai.")
            while True:
                choice = input("\nAbhihi karna hai ya bad me bhi kar sakte hai -->Blog (1: Abhi / 2: Baad me): ").strip().lower()
                if choice in {"1", "abhi", "now", "yes", "regenerate"}:
                    print("\n[Reviewer] Generating a new output now...")
                    return {
                        "title": title,
                        "content": content,
                        "review": notes,
                        "approved": False,
                        "cancelled": False,
                    }
                if choice in {"2", "baad me", "bad me", "later", "exit", "cancel", "no"}:
                    print("\nWorkflow ended. No draft saved. Baad me dubara kar sakte hain.")
                    return {
                        "title": title,
                        "content": content,
                        "review": notes,
                        "approved": False,
                        "cancelled": True,
                    }
                print("Please enter 1 (Abhi generate karein) or 2 (Baad me karein).")
        if answer in {"exit", "quit", "cancel"}:
            print("\nWorkflow cancelled.")
            return {
                "title": title,
                "content": content,
                "review": notes,
                "approved": False,
                "cancelled": True,
            }
        print("Please type 'yes' to publish, 'no' to regenerate, or 'exit' to cancel.")
