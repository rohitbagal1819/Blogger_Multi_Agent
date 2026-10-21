"""Terminal entry point; LangGraph controls the blog workflow."""
import sys
from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from agents.common import BlogState, ROOT
from agents.orchestrator import orchestrator
from agents.researcher import researcher
from agents.writer import writer
from agents.reviewer import reviewer
from services.blogger_client import publish, check_blogger

load_dotenv(ROOT / ".env")

def publish_post(state: BlogState) -> dict:
    url = publish(state["title"], state["content"])
    print(f"\nSuccessfully published: {url}")
    return {"result": url}

def next_step(state: BlogState) -> str:
    if state.get("cancelled"):
        return END
    return "publish" if state.get("approved") is True else "writer"

def build_graph():
    graph = StateGraph(BlogState)
    for name, node in [("orchestrator", orchestrator), ("researcher", researcher),
                       ("writer", writer), ("reviewer", reviewer),
                       ("publish", publish_post)]:
        graph.add_node(name, node)
    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_conditional_edges("reviewer", next_step,
                                {"publish": "publish", "writer": "writer", END: END})
    graph.add_edge("publish", END)
    return graph.compile()

def main():
    if "--check-blogger" in sys.argv:
        try:
            check_blogger()
        except Exception as exc:
            print(f"Blogger authentication check failed: {exc}")
            raise SystemExit(1) from exc
        return
    app = build_graph()
    print("Auto Blog Multi-Agent System | LangGraph + Gemini + Blogger")
    while True:
        topic = input("\nBlog topic (or 'exit'): ").strip()
        if topic.lower() == "exit":
            break
        if topic:
            try:
                app.invoke({"topic": topic}, config={"recursion_limit": 100})
            except Exception as exc:
                print(f"Workflow stopped safely: {exc}")

if __name__ == "__main__":
    main()
