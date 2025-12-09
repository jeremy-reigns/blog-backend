import os
import uuid
import json
import asyncio
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from openai import OpenAI
from prompt_loader import load_prompts

# PDF generation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# -----------------------
# Load ENV
# -----------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

# -----------------------
# CORS (for Vercel Frontend)
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for development; restrict later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# File Storage
# -----------------------
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
PDF_DIR = os.path.join(OUTPUT_DIR, "pdfs")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

def save_markdown(blog_id: str, content: str):
    with open(os.path.join(OUTPUT_DIR, f"{blog_id}.md"), "w", encoding="utf-8") as f:
        f.write(content)

def save_json(blog_id: str, data: dict):
    with open(os.path.join(OUTPUT_DIR, f"{blog_id}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_blog_json(blog_id: str):
    path = os.path.join(OUTPUT_DIR, f"{blog_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------
# Models
# -----------------------
class BlogResponse(BaseModel):
    id: str
    topic: str
    created_at: str
    seo: dict
    final_post: str

class SummarizeRequest(BaseModel):
    text: str
    style: str | None = "linkedin"

# -----------------------
# Helpers
# -----------------------
def format_sse(data: str):
    return f"data: {data}\n\n"


# -----------------------
# STREAMING BLOG GENERATION
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
    final_output = ""

    async def event_stream():
        nonlocal final_output

        yield format_sse("Starting generation...")

        for i, step in enumerate(steps):
            yield format_sse(f"Running step {i+1}/{len(steps)}...")

            conversation.append({"role": "user", "content": step})
            result = client.chat.completions.create(
                model=MODEL_NAME,
                messages=conversation
            )
            out = result.choices[0].message.content
            final_output = out
            conversation.append({"role": "assistant", "content": out})

            yield format_sse(f"Step {i+1} complete.")
            await asyncio.sleep(0.05)

        seo_meta = {
            "title": topic,
            "description": final_output[:250] + "...",
            "raw": topic,
        }

        full_blog = {
            "id": blog_id,
            "topic": topic,
            "created_at": created_at,
            "seo": seo_meta,
            "final_post": final_output
        }

        save_markdown(blog_id, final_output)
        save_json(blog_id, full_blog)

        yield format_sse("DONE::" + json.dumps(full_blog))

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# -----------------------
# NON-STREAM GENERATION
# -----------------------
@app.post("/generate-blog", response_model=BlogResponse)
def generate_blog(request: dict):
    topic = request.get("topic", "").strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    prompt_chain = load_prompts()
    conversation = [
        {"role": "system", "content": prompt_chain[0]},
        {"role": "user", "content": f"Main topic: {topic}"},
    ]

    for step in prompt_chain[1:]:
        conversation.append({"role": "user", "content": step})
        result = client.chat.completions.create(
            model=MODEL_NAME,
            messages=conversation
        )
        output_text = result.choices[0].message.content
        conversation.append({"role": "assistant", "content": output_text})

    blog_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    seo_meta = {
        "title": topic,
        "description": output_text[:300] + "...",
        "raw": topic,
    }

    response = {
        "id": blog_id,
        "topic": topic,
        "created_at": created_at,
        "seo": seo_meta,
        "final_post": output_text,
    }

    save_markdown(blog_id, output_text)
    save_json(blog_id, response)

    return response


# -----------------------
# GET BLOGS
# -----------------------
@app.get("/blog/{blog_id}", response_model=BlogResponse)
def get_blog(blog_id: str):
    blog = load_blog_json(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found.")
    return blog

@app.get("/blogs")
def list_blogs():
    blogs = []
    for file in os.listdir(OUTPUT_DIR):
        if file.endswith(".json"):
            with open(os.path.join(OUTPUT_DIR, file), "r") as f:
                blogs.append(json.load(f))
    return blogs


# -----------------------
# AI SUMMARY ENDPOINT
# -----------------------
@app.post("/summarize")
async def summarize(body: SummarizeRequest):
    style_prompt = (
        "Write a concise, high-impact LinkedIn post summarizing this article. "
        "Be engaging, sharp, and professional."
        if body.style == "linkedin" else
        "Summarize clearly and concisely."
    )

    prompt = f"""
    {style_prompt}

    Blog content:
    {body.text}
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    summary = completion.choices[0].message["content"]
    return {"summary": summary}


# -----------------------
# PDF EXPORT ENDPOINT
# -----------------------
@app.get("/export-pdf/{blog_id}")
def export_pdf(blog_id: str):
    blog = load_blog_json(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found.")

    pdf_path = os.path.join(PDF_DIR, f"{blog_id}.pdf")

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    text_obj = c.beginText(40, height - 50)
    text_obj.setFont("Helvetica", 11)

    for line in blog["final_post"].split("\n"):
        text_obj.textLine(line)

    c.drawText(text_obj)
    c.save()

    return FileResponse(pdf_path, media_type="application/pdf", filename=f"{blog_id}.pdf")
