import subprocess
import os

def extract_audio(video_path: str, audio_path: str) -> str:
    """Extract audio from a video file."""
    if os.path.exists(audio_path):
        os.remove(audio_path)
    
    command = [
        "ffmpeg",
        "-i", video_path,
        "-q:a", "0",
        "-map", "a",
        audio_path,
        "-y"
    ]
    try:
        subprocess.run(command, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL, 
                        check=True)
        return audio_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
    """Chunk text into smaller chunks with optional overlap."""
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunks.append(text[start:end])
        start += chunk_size - overlap
        if start < 0:
            start = 0
    return chunks

def chunked_summarize(text: str, summarizer: callable, max_chunk_size: int = 2000) -> str:
    """Summarize text in chunks and combine the summaries."""

    #1. Chunk the text
    chunks = chunk_text(text, max_chunk_size, overlap = 200)

    #2. Summarize each chunk
    partial_summaries = [summarizer(chunk) for chunk in chunks]

    #3. Combine the summaries
    combined_summary_input =  " ".join(partial_summaries)

    #4. Final summarization
    final_summary = summarizer(combined_summary_input)

    return final_summary