import os
import uuid
import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime

from openai import OpenAI
from prompt_loader import load_prompts

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Models
# -----------------------
class BlogResponse(BaseModel):
    id: str
    topic: str
    created_at: str
    seo: dict
    final_post: str

# -----------------------
# File Helpers
# -----------------------
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_markdown(blog_id: str, content: str):
    filepath = os.path.join(OUTPUT_DIR, f"{blog_id}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def save_json(blog_id: str, data: dict):
    filepath = os.path.join(OUTPUT_DIR, f"{blog_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_blog_json(blog_id: str):
    filepath = os.path.join(OUTPUT_DIR, f"{blog_id}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------
# Utility
# -----------------------
def format_sse(data: str):
    return f"data: {data}\n\n"


# -----------------------
# STREAMING GENERATION
# -----------------------
@app.get("/generate-blog-stream")
async def generate_blog_stream(topic: str):
    topic = topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    prompt_chain = load_prompts()
    system_msg = prompt_chain[0]
    steps = prompt_chain[1:]

    conversation = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"Main topic: {topic}"}
    ]

    blog_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    last_output = ""

    async def event_stream():
        nonlocal last_output

        yield format_sse("Starting generation...")

        for i, step in enumerate(steps):
            yield format_sse(f"Running step {i+1}/{len(steps)}...")

            conversation.append({"role": "user", "content": step})

            result = client.chat.completions.create(
                model=MODEL_NAME,
                messages=conversation
            )
            out = result.choices[0].message.content
            last_output = out
            conversation.append({"role": "assistant", "content": out})

            yield format_sse(f"Step {i+1} complete.")
            await asyncio.sleep(0.05)

        # Build metadata to save
        seo_meta = {
            "title": topic,
            "description": last_output[:300] + "...",
            "raw": topic,
        }

        full_blog = {
            "id": blog_id,
            "topic": topic,
            "created_at": created_at,
            "seo": seo_meta,
            "final_post": last_output
        }

        # SAVE FILES 💾
        save_markdown(blog_id, last_output)
        save_json(blog_id, full_blog)

        yield format_sse("DONE::" + json.dumps(full_blog))

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# -----------------------
# NON-STREAM GENERATION (still available)
# -----------------------
@app.post("/generate-blog", response_model=BlogResponse)
def generate_blog(request: dict):
    topic = request.get("topic", "").strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    prompt_chain = load_prompts()
    system_message = prompt_chain[0]
    user_messages = prompt_chain[1:]

    conversation = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Main topic: {topic}"},
    ]

    for step in user_messages:
        conversation.append({"role": "user", "content": step})
        result = client.chat.completions.create(
            model=MODEL_NAME,
            messages=conversation
        )
        output_text = result.choices[0].message.content
        conversation.append({"role": "assistant", "content": output_text})

    final_post = output_text

    blog_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    seo_meta = {
        "title": topic,
        "description": final_post[:300] + "...",
        "raw": topic,
    }

    response = {
        "id": blog_id,
        "topic": topic,
        "created_at": created_at,
        "seo": seo_meta,
        "final_post": final_post,
    }

    save_markdown(blog_id, final_post)
    save_json(blog_id, response)

    return response


# -----------------------
# Blog Fetching
# -----------------------
@app.get("/blog/{blog_id}", response_model=BlogResponse)
def get_blog(blog_id: str):
    blog = load_blog_json(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found.")
    return blog

@app.get("/blogs")
def list_blogs():
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".json")]
    blogs = []
    for file in files:
        with open(os.path.join(OUTPUT_DIR, file), "r") as f:
            blogs.append(json.load(f))
    return blogs
