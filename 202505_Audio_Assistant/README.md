
# Ask Your Audio: An AI That Listens, Thinks, and Talks Back

This is a **Streamlit-based application** that allows users to upload audio (e.g., lectures, podcasts), transcribe it using Whisper, ask natural language questions about the content, and receive spoken answers generated in the original speaker’s voice.

---

## 🛠 Features

- **Upload Audio**: Supports WAV or MP3 formats.
- **Transcription**: Uses OpenAI's Whisper for audio transcription.
- **Q&A Engine**: Ask questions about the audio content using local DeepSeek-R1.
- **Voice Cloning**: Converts answers back into speech using the original speaker's voice via XTTS.

---

## ⚙️ Tech Stack

| Component        | Model                                                                 |
|------------------|-----------------------------------------------------------------------|
| Transcription     | [`whisper`](https://github.com/openai/whisper) (medium.en)           |
| LLM     | [`deepseek-r1`](https://ollama.com/library/deepseek-r1) via `langchain-ollama` |
| Text-to-Speech    | [`xtts_v2`](https://github.com/coqui-ai/TTS) multilingual speaker cloning |
| Embeddings & Vector Store | `OllamaEmbeddings` + `InMemoryVectorStore`               |

---

## 📖 Read the Full Story on Medium
[**Ask Your Audio: An AI That Listens, Thinks, and Talks Back**](https://medium.com/towards-artificial-intelligence/ask-your-audio-an-ai-that-listens-thinks-and-talks-back-0e2b206c3901)  

