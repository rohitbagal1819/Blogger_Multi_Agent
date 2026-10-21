"""Blogger API client with local OAuth token refresh and recovery."""
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
SCOPES = ["https://www.googleapis.com/auth/blogger"]

def service():
    token_file, client_file = ROOT / "token.json", ROOT / "credentials.json"
    creds = None
    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        except (OSError, ValueError):
            token_file.unlink(missing_ok=True)
    if creds and not creds.valid and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:
            token_file.unlink(missing_ok=True)
            creds = None
    if not creds or not creds.valid:
        if not client_file.exists():
            raise FileNotFoundError("Download a Google Desktop OAuth client JSON and save it as credentials.json.")
        creds = InstalledAppFlow.from_client_secrets_file(str(client_file), SCOPES).run_local_server(port=0)
    token_file.write_text(creds.to_json(), encoding="utf-8")
    return build("blogger", "v3", credentials=creds, cache_discovery=False)

def get_blogs(api):
    return api.blogs().listByUser(userId="self").execute().get("items", [])

def check_blogger():
    blogs = get_blogs(service())
    if not blogs:
        raise RuntimeError("OAuth succeeded, but this Google account has no Blogger blogs.")
    print("Blogger authentication succeeded. Available blogs:")
    for blog in blogs:
        print(f"- {blog['name']} | ID: {blog['id']}")

def choose_blog(api) -> str:
    blog_id = os.getenv("BLOGGER_BLOG_ID", "").strip()
    if blog_id:
        return blog_id
    blogs = get_blogs(api)
    if not blogs:
        raise RuntimeError("No Blogger blogs were found for this Google account.")
    if len(blogs) == 1:
        return blogs[0]["id"]
    for number, blog in enumerate(blogs, 1):
        print(f"{number}. {blog['name']} (ID: {blog['id']})")
    while True:
        try:
            choice = int(input("Choose blog number: "))
            if 1 <= choice <= len(blogs):
                return blogs[choice - 1]["id"]
        except ValueError:
            pass
        print("Enter a valid number from the list.")

def safe_html(content: str) -> str:
    """Remove active HTML elements before sending generated content to Blogger."""
    return re.sub(r"<(script|iframe|object|embed|form)\b[^>]*>.*?</\1\s*>", "", content, flags=re.I | re.S)

def publish(title: str, content: str) -> str:
    api = service()
    blog_id = choose_blog(api)
    try:
        post = api.posts().insert(
            blogId=blog_id, body={"title": title, "content": safe_html(content)}, isDraft=False
        ).execute()
    except HttpError as exc:
        hint = " Check Blogger API access and the Google account's blog permissions." if exc.resp.status in (401, 403) else ""
        raise RuntimeError(f"Blogger API error {exc.resp.status}.{hint} Details: {exc}") from exc
    return post.get("url", f"Post created (ID: {post.get('id', 'unknown')}).")
