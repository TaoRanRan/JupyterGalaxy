# YouTube Language Tutor

Turn any YouTube video into an interactive language lesson. Paste a URL, get comprehension questions, vocabulary breakdowns, answers, and a live AI tutor. 

**Free.** Runs on Google Gemini's free tier. Get a free API key: Visit [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

---

## 🛠 Features

- **Auto-detect captions** — Lists available languages.
- **Smart chunking** — Handles long videos by trimming at sentence boundaries
- **Token-optimized** — Questions + vocabulary in one API call, answers use excerpts only
- **Language mirroring** — Tutor replies in whatever language you use
- **Session saving** — Exports questions, vocab, answers, and chat summary as markdown

---

## 🧱 Project Structure

```
language_tutor/
├── main.py              # workflow + UI
├── tutor.py             # LLM interface
├── transcript.py        # YouTube data fetcher
├── requirements.txt
├── .env                 # GEMINI_API_KEY
└── sessions/            # saved markdown files

```

---

## ✅ Usage Example

```
YouTube Language Tutor

Enter YouTube URL
  Example: https://www.youtube.com/watch?v=...
  URL: https://www.youtube.com/watch?v=abc123
  ✓ https://www.youtube.com/watch?v=abc123

What language are you learning?
  Example: Spanish, French, Japanese
  Language: Spanish
  ✓ Spanish

────────────── CAPTIONS ──────────────

  → Detecting captions...
  ✓ Using: Spanish [es]

────────────── TRANSCRIPT ──────────────

  → Fetching transcript...
  ✓ Transcript ready (847 words)

  → Generating questions & vocabulary...
  → Preparing answers...

────────────── QUESTIONS ──────────────

1. ¿Cuál es el tema principal del video?
2. ¿Qué solución propone el autor?

  Press Enter to see vocabulary...

────────────── VOCABULARY ──────────────

**sin embargo**
Meaning: however, nevertheless
Example: Me gusta el café, sin embargo prefiero el té. → I like coffee, however I prefer tea.

**proponer**
Meaning: to propose, to suggest
Example: Ella propone una solución innovadora. → She proposes an innovative solution.

  Press Enter to see answers...

────────────── ANSWERS ──────────────

1. El tema principal es...
2. El autor propone...

  Press Enter to start chat...

────────────── CHAT ──────────────

Type 'quit' to finish

Tutor: ¡Hola! ¿Tienes preguntas sobre el video?

You: What does "sin embargo" mean?
  → What does "sin embargo" mean?

Tutor: "Sin embargo" means "however" or "nevertheless"...

You: quit

Great work today!

  → Summarising chat...

✓ Session saved to: sessions/spanish_2025-02-18_14-32.md
```

---

## 📖 Read the Full Story on Medium


