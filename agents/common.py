"""Shared state and Gemini helpers."""
import json
import logging
import os
from pathlib import Path
from typing import TypedDict
from dotenv import load_dotenv
from google import genai
from google.genai import types

logging.getLogger("google_genai").setLevel(logging.ERROR)

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

class BlogState(TypedDict, total=False):
    topic: str
    plan: str
    research: str
    title: str
    content: str
    review: str
    approved: bool
    cancelled: bool
    result: str

def ask(prompt: str, search: bool = False, json_mode: bool = False) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key or key == "your_gemini_api_key_here":
        raise RuntimeError("Add your Gemini key to .env first.")
    options = {}
    if search:
        options["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    if json_mode:
        options["response_mime_type"] = "application/json"
    client = genai.Client(api_key=key)
    for _ in range(2):
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            contents=prompt,
            config=types.GenerateContentConfig(**options),
        )
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            text_parts = [
                part.text for part in response.candidates[0].content.parts
                if getattr(part, "text", None) and not getattr(part, "thought", False)
            ]
            full_text = "".join(text_parts).strip()
            if full_text:
                return full_text
        if getattr(response, "text", None):
            return response.text
    raise RuntimeError("Gemini returned an empty response.")

def ask_json(prompt: str) -> dict:
    return json.loads(ask(prompt, json_mode=True), strict=False)
