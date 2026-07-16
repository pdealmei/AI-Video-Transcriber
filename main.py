import os
from transcriber import extract_audio, transcribe_audio
from summarizer import summarize_text
from utils import chunked_summarize

def video_to_summary(video_path: str, 
                model_size: str = "base",
                summary_model_name: str = "facebook/bart-large-cnn",
                use_chinking: bool = False) -> str:

    #1 Extract Audio
    audio_path = "temp_audio.wav"
    extract_audio(video_path, audio_path)

    #2 Transcribe Audio
    transcript = transcribe_audio(audio_path, model_size)
    print("--------------------------------")
    print(f"Transcript: {transcript}")
    print("--------------------------------")

    #3 Summarize Text
    if use_chinking:
        summary = chunked_summarize(text = transcript, 
                                    summarizer = lambda txt: summarize_text(txt, summary_model_name), 
                                    max_chunk_size = 2000)

    else:
        summary = summarize_text(transcript, summary_model_name)

    if os.path.exists(audio_path):
        os.remove(audio_path)

    return summary


if __name__ == "__main__":
    video_path = "test_video.mp4"
    summary = video_to_summary(video_path, "base", "facebook/bart-large-cnn", True)
    print(summary)