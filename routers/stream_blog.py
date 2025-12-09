import os
import uuid
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from prompt_loader import load_prompts
from datetime import datetime

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1")

client = OpenAI(api_key=OPENAI_API_KEY)
router = APIRouter()


class TopicRequest(BaseModel):
    topic: str


def format_sse(data: str):
    return f"data: {data}\n\n"


@app.get("/generate-blog-stream")
async def generate_blog_stream(topic: str):
    topic = topic.strip()

    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    prompt_chain = load_prompts()
    system_message = prompt_chain[0]
    steps = prompt_chain[1:]

    conversation = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Main topic: {topic}"},
    ]

    def format_sse(data: str):
        return f"data: {data}\n\n"

    async def event_stream():
        yield format_sse("Starting generation...")

        for i, step in enumerate(steps):
            yield format_sse(f"Running step {i+1}/{len(steps)}...")

            conversation.append({"role": "user", "content": step})

            result = client.chat.completions.create(
                model=MODEL_NAME,
                messages=conversation,
            )
            out = result.choices[0].message.content
            conversation.append({"role": "assistant", "content": out})

            yield format_sse(f"Step {i+1} completed.")

            await asyncio.sleep(0.1)

        yield format_sse("DONE::" + out)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
