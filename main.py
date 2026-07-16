import os

from dotenv import load_dotenv

from transcriber import Transcriber
from summarizer import Summarizer
from utils import extract_audio, chunked_summarize

load_dotenv()

def video_to_summary(video_path: str, 
                transcriber: Transcriber,
                summarizer: Summarizer,
                use_chinking: bool = False) -> str:

    #1 Extract Audio
    audio_path = "temp_audio.wav"
    extract_audio(video_path, audio_path)

    #2 Transcribe Audio
    transcript = transcriber.transcribe_audio(audio_path)
    print("--------------------------------")
    print(f"Transcript: {transcript}")
    print("--------------------------------")

    #3 Summarize Text
    if use_chinking:
        summary = chunked_summarize(text = transcript, 
                                    summarizer = lambda txt: summarizer.summarize_text(txt), 
                                    max_chunk_size = 2000)

    else:
        summary = summarizer.summarize_text(transcript)

    if os.path.exists(audio_path):
        os.remove(audio_path)

    return summary


if __name__ == "__main__":
    video_path = "test_video.mp4"
    whisper_model = os.getenv("WHISPER_MODEL")
    llm_base_url = os.getenv("LLM_BASE_URL")
    llm_api_key = os.getenv("LLM_API_KEY")
    llm_model = os.getenv("LLM_MODEL")
    system_prompt = os.getenv("SYSTEM_PROMPT")

    if not os.path.exists(video_path):
        print(f"Video file {video_path} does not exist")
        exit(1)
    
    # transcript_file = "transcript.txt"
    # transcript = Path(transcript_file).read_text().strip()

    summarizer = Summarizer(
        summarizer_base_url=llm_base_url,
        summarizer_api_key=llm_api_key,
        summarizer_model=llm_model
    )
    transcriber = Transcriber(
        whisper_model=whisper_model
    )
    summary = video_to_summary(video_path, transcriber, summarizer, use_chinking=True)
    print(summary)