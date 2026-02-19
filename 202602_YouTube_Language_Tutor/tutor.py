"""LLM interface - all Gemini API calls."""

import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def _get_model() -> str:
    """Auto-detect newest Gemini Flash model."""
    try:
        models = [
            m.name for m in client.models.list()
            if m.supported_actions and "generateContent" in m.supported_actions
            and "flash" in m.name.lower() and "gemini" in m.name.lower()
            and "thinking" not in m.name.lower() and "8b" not in m.name.lower()
        ]
        return sorted(models, reverse=True)[0].replace("models/", "") if models else "gemini-2.0-flash"
    except:
        return "gemini-2.0-flash"


MODEL = _get_model()
print(f" Using {MODEL}")


def _call(system: str, user: str) -> str:
    """Single API call."""
    response = client.models.generate_content(
        model=MODEL,
        contents=user,
        config=types.GenerateContentConfig(system_instruction=system),
    )
    return response.text


def summarise_transcript(transcript: str) -> str:
    return _call(
        f"Transcript:\n{transcript}",
        "Summarise in ~400 words. Preserve key facts. Plain prose."
    )


def generate_questions_and_vocabulary(transcript: str, lang: str) -> tuple[str, str]:
    text = _call(
        f"Transcript:\n{transcript}",
        f"Language: {lang}\n\n"
        f"TASK 1: Write 2 questions in {lang} only. Number 1-2. Add hints in {lang}.\n\n"
        f"TASK 2: List 4-5 key words/phrases for answering questions.\n"
        f"For each word, format like this:\n\n"
        f"**[{lang} word]**\n"
        f"Meaning: [English definition]\n"
        f"Example: [{lang} sentence] → [English translation]\n"
        f"Note: Only add 'Pronunciation:' line if the language uses non-Latin script (Arabic, Chinese, Japanese, Korean, etc.)\n\n"
        f"===QUESTIONS===\n[questions]\n===VOCABULARY===\n[vocabulary]"
    )
    if "===QUESTIONS===" in text and "===VOCABULARY===" in text:
        parts = text.split("===VOCABULARY===")
        return parts[0].replace("===QUESTIONS===", "").strip(), parts[1].strip()
    return text, ""


def generate_answers(questions: str, lang: str, transcript: str) -> str:
    excerpt = transcript[:1500].rsplit(" ", 1)[0]
    return _call(
        f"Transcript:\n{excerpt}",
        f"Questions:\n{questions}\n\nWrite answers in {lang} only. Number to match. Be concise."
    )


def summarise_chat(lang: str, exchanges: list[tuple[str, str]]) -> str:
    log = "\n".join(f"Student: {q}\nTutor: {a}" for q, a in exchanges)
    return _call(
        f"You are a {lang} tutor.",
        f"Summarise chat in {lang} only. 3-5 sentences. Focus on language points.\n\n{log}"
    )


class ChatSession:
    """Stateful chat with history."""
    
    def __init__(self, transcript: str, lang: str):
        self._system = (
            f"You are a {lang} tutor. Answer questions about video, vocabulary, grammar. "
            f"Reply in the same language the student uses.\n\nTranscript:\n{transcript}"
        )
        self._history = []
        self.exchanges = []
    
    def send(self, msg: str) -> str:
        self._history.append(types.Content(role="user", parts=[types.Part.from_text(text=msg)]))
        response = client.models.generate_content(
            model=MODEL,
            contents=self._history,
            config=types.GenerateContentConfig(system_instruction=self._system),
        )
        reply = response.text
        self._history.append(types.Content(role="model", parts=[types.Part.from_text(text=reply)]))
        self.exchanges.append((msg, reply))
        return reply
