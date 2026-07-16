from pathlib import Path

from openai import OpenAI


# Edit system_prompt.txt to change how the LLM cleans transcriptions
PROMPT_FILE = Path(__file__).parent / "system_prompt.txt"
SYSTEM_PROMPT = PROMPT_FILE.read_text().strip()

class Summarizer:
    def __init__(self, summarizer_base_url: str, summarizer_api_key: str, summarizer_model: str):
        self.llm_client = OpenAI(base_url=summarizer_base_url, api_key=summarizer_api_key)
        self.llm_model = summarizer_model

    def get_default_system_prompt(self):
        return SYSTEM_PROMPT

    def summarize_text(self, text: str) -> str:
        """Summarize text using a transformer model."""
        prompt_to_use = self.get_default_system_prompt()
        response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": prompt_to_use},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
                max_tokens=200,
            )

        summary = response.choices[0].message.content.strip()

        return summary