#%%
"""YouTube Language Learning Tutor - main workflow."""

import os
import sys
import re
from datetime import datetime
from pathlib import Path
from transcript import get_available_languages, fetch_transcript, chunk_if_needed
from tutor import summarise_transcript, generate_questions_and_vocabulary, generate_answers, summarise_chat, ChatSession

SUMMARISE_THRESHOLD = 3_000


def prompt(text: str) -> str:
    try:
        return input(text).strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nSession ended.")
        sys.exit(0)


def divider(title: str):
    print(f"\n{'─' * 20} {title} {'─' * 20}\n")


def pick_language(url: str) -> str:
    print("\n  → Detecting captions...")
    languages = get_available_languages(url)
    if not languages:
        raise RuntimeError("No captions available.")
    if len(languages) == 1:
        print(f"  ✓ Using: {languages[0][1]} [{languages[0][0]}]")
        return languages[0][0]
    
    print(f"\n  Available languages ({len(languages)}):")
    for i, (code, name) in enumerate(languages, 1):
        print(f"    {i}. {name} [{code}]")
    
    while True:
        try:
            idx = int(prompt(f"\n  Select (1-{len(languages)}): ")) - 1
            if 0 <= idx < len(languages):
                print(f"  ✓ Selected: {languages[idx][1]} [{languages[idx][0]}]")
                return languages[idx][0]
        except ValueError:
            pass


def get_transcript(url: str, lang_code: str) -> str:
    print("\n  → Fetching transcript...")
    text, words, original = chunk_if_needed(fetch_transcript(url, lang_code))
    
    if words < original:
        print(f"  ⚠ Long video ({original} words) — using first {words} words")
    else:
        print(f"  ✓ Transcript ready ({words} words)")
    
    if words > SUMMARISE_THRESHOLD:
        print(f"  → Summarising...")
        text = summarise_transcript(text)
        print(f"  ✓ Condensed to ~{len(text.split())} words")
    
    return text


def chat_loop(session: ChatSession, lang: str):
    print("Type 'quit' to finish\n")
    print(f"Tutor: {session.send(f'Greet in {lang}, ask if questions. 2 sentences.')}\n")
    
    while True:
        msg = prompt("You: ")
        if not msg:
            continue
        if msg.lower() in ("quit", "exit", "q"):
            print("\nGreat work today!")
            break
        print(f"  → {msg}")
        print(f"\nTutor: {session.send(msg)}\n")


def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("✗ Set GEMINI_API_KEY\n  Get free key at: https://aistudio.google.com/app/apikey")
        sys.exit(1)
    
    print("\nYouTube Language Tutor\n")
    
    try:
        # Get inputs
        print("Enter YouTube URL")
        print("  Example: https://www.youtube.com/watch?v=...")
        url = prompt("  URL: ")
        print(f"  ✓ {url}")
        
        print("\nWhat language are you learning?")
        print("  Example: Spanish, French, Japanese")
        lang = prompt("  Language: ")
        print(f"  ✓ {lang}")
        
        # Fetch transcript
        divider("CAPTIONS")
        lang_code = pick_language(url)
        divider("TRANSCRIPT")
        transcript = get_transcript(url, lang_code)
        
        # Generate materials
        print("\n  → Generating questions & vocabulary...")
        questions, vocab = generate_questions_and_vocabulary(transcript, lang)
        print("  → Preparing answers...")
        answers = generate_answers(questions, lang, transcript)
        
        # Display
        divider("QUESTIONS")
        print(questions)
        input("\n  Press Enter to see vocabulary...")
        divider("VOCABULARY")
        print(vocab)
        input("\n  Press Enter to see answers...")
        divider("ANSWERS")
        print(answers)
        
        # Chat
        input("\n  Press Enter to start chat...")
        divider("CHAT")
        session = ChatSession(transcript, lang)
        chat_loop(session, lang)
        
        # Save
        if session.exchanges:
            print("\n  → Summarising chat...")
            chat_summary = summarise_chat(lang, session.exchanges)
        else:
            chat_summary = ""
        
        Path("sessions").mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        slug = re.sub(r"[^a-zA-Z]", "", lang).lower()
        path = Path(f"sessions/{slug}_{timestamp}.md")
        
        chat_section = f"\n---\n\n## Chat Summary\n{chat_summary}\n" if chat_summary else ""
        path.write_text(
            f"# {lang} Learning Session\n"
            f"**Date:** {datetime.now().strftime('%d %B %Y, %H:%M')}\n"
            f"**Video:** {url}\n\n---\n\n"
            f"## Questions\n{questions}\n\n---\n\n"
            f"## Vocabulary\n{vocab}\n\n---\n\n"
            f"## Answers\n{answers}\n{chat_section}",
            encoding="utf-8"
        )
        print(f"\n✓ Session saved to: {path}")
        
    except KeyboardInterrupt:
        print("\n\nSession cancelled. Keep practising!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

#%%
if __name__ == "__main__":
    main()

#%%