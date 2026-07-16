import asyncio
import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from summarizer import Summarizer
from transcriber import Transcriber
from utils import extract_audio, chunked_summarize

load_dotenv()

ALLOWED_EXTENSIONS = {".mp4"}
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "500"))


def video_to_summary(video_path: str, 
                transcriber: Transcriber,
                summarizer: Summarizer,
                use_chinking: bool = False,
                audio_path: str | None = None) -> dict[str, str]:

    if audio_path is None:
        audio_path = os.path.join(os.path.dirname(video_path), "temp_audio.wav")

    extract_audio(video_path, audio_path)

    transcript = transcriber.transcribe_audio(audio_path)

    if use_chinking:
        summary = chunked_summarize(
            text=transcript,
            summarizer=summarizer.summarize_text,
            max_chunk_size=2000,
        )
    else:
        summary = summarizer.summarize_text(transcript)

    if os.path.exists(audio_path):
        os.remove(audio_path)

    return {"transcript": transcript, "summary": summary}


@asynccontextmanager
async def lifespan(app: FastAPI):
    whisper_model = os.getenv("WHISPER_MODEL", "base.en")
    llm_base_url = os.getenv("LLM_BASE_URL")
    llm_api_key = os.getenv("LLM_API_KEY", "ollama")
    llm_model = os.getenv("LLM_MODEL")

    if not llm_base_url or not llm_model:
        raise RuntimeError("LLM_BASE_URL and LLM_MODEL must be set in the environment")

    app.state.transcriber = Transcriber(whisper_model=whisper_model)
    app.state.summarizer = Summarizer(
        summarizer_base_url=llm_base_url,
        summarizer_api_key=llm_api_key,
        summarizer_model=llm_model,
    )
    yield


app = FastAPI(title="AI Video Transcriber", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
        ).split(",")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProcessResponse(BaseModel):
    transcript: str
    summary: str


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/process", response_model=ProcessResponse)
async def process_video(
    request: Request,
    file: UploadFile = File(...),
    use_chunking: bool = True,
) -> ProcessResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file must be provided")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content = await file.read()
    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {MAX_UPLOAD_SIZE_MB} MB upload limit",
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, f"upload{suffix}")
        with open(video_path, "wb") as video_file:
            video_file.write(content)

        try:
            result = await asyncio.to_thread(
                video_to_summary,
                video_path,
                request.app.state.transcriber,
                request.app.state.summarizer,
                use_chunking,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process video: {exc}",
            ) from exc

    return ProcessResponse(**result)
