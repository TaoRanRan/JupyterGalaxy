"""YouTube transcript fetcher - pure data layer."""

from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

MAX_TRANSCRIPT_CHARS = 24_000


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        return parsed.path[1:]
    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        return parse_qs(parsed.query)["v"][0]
    raise ValueError("Invalid YouTube URL")


def get_available_languages(url: str) -> list[tuple[str, str]]:
    """Return [(code, name), ...] for all available captions."""
    video_id = extract_video_id(url)
    transcript_list = YouTubeTranscriptApi().list(video_id)
    return [(t.language_code, t.language) for t in transcript_list]


def fetch_transcript(url: str, language_code: str) -> str:
    """Fetch and return raw transcript text."""
    video_id = extract_video_id(url)
    fetched = YouTubeTranscriptApi().fetch(video_id, languages=[language_code])
    return " ".join(snippet.text for snippet in fetched)


def chunk_if_needed(text: str) -> tuple[str, int, int]:
    """Trim transcript if too long. Returns (text, word_count, original_word_count)."""
    original_words = len(text.split())
    
    if len(text) <= MAX_TRANSCRIPT_CHARS:
        return text, original_words, original_words
    
    # Trim at sentence boundary
    chunk = text[:MAX_TRANSCRIPT_CHARS]
    for marker in [". ", "。", "? ", "! "]:
        idx = chunk.rfind(marker)
        if idx > MAX_TRANSCRIPT_CHARS * 0.7:
            chunk = chunk[:idx + 1]
            break
    
    return chunk, len(chunk.split()), original_words
