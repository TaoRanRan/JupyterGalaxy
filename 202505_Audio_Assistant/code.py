#%%
import re
from pathlib import Path
import torch
import whisper
from IPython.display import Audio, Markdown, display
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_text_splitters import RecursiveCharacterTextSplitter
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig

# Constants 
AUDIO_DIR = Path(__file__).parent
AUDIO_DIR.mkdir(exist_ok=True)

PROMPT_TEMPLATE = """You are a helpful and accurate question-answering assistant.
Your primary goal is to answer the user's `Question` based on the `Context` provided.

If the `Context` doesn't contain sufficient information, state you don't know.
Keep answers concise.

Question: {question}
Context: {context}
Answer:"""

# Model Initialization
WHISPER_MODEL = whisper.load_model("medium.en")
EMBEDDINGS = OllamaEmbeddings(model="deepseek-r1:latest")
VECTOR_STORE = InMemoryVectorStore(EMBEDDINGS)
LLM_MODEL = OllamaLLM(model="deepseek-r1:latest")
TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True
)

# Device configuration
DEVICE = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"

# Add these classes to PyTorch's safe globals list for model compatibility 
torch.serialization.add_safe_globals([
    XttsConfig,
    XttsAudioConfig,
    BaseDatasetConfig,
    XttsArgs
])

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)

# Core functions
def transcribe_audio(file_path: Path) -> str:
    """Transcribe audio using Whisper ASR."""
    return WHISPER_MODEL.transcribe(str(file_path))["text"]


def process_text(text: str) -> None:
    """Process and index text documents."""
    chunks = TEXT_SPLITTER.split_text(text)
    VECTOR_STORE.add_texts(chunks)


def generate_answer(question: str) -> str:
    """Generate answer using RAG pipeline."""
    docs = VECTOR_STORE.similarity_search(question)
    context = "\n\n".join(doc.page_content for doc in docs)
    
    response = (ChatPromptTemplate.from_template(PROMPT_TEMPLATE) 
               | LLM_MODEL).invoke({"question": question, "context": context})
    
    return re.compile(r"<think>.*?</think>", flags=re.DOTALL).sub("", response).strip()


def synthesize_speech(text: str, reference_audio: Path, output_file: Path) -> None:
    """Convert text to speech using reference audio."""
    tts.tts_to_file(
        text=text,
        speaker_wav=str(reference_audio),
        language="en",
        file_path=str(output_file)
    )


#%%
# Sample usage
input_audio = AUDIO_DIR / "podcast.wav"
output_audio = AUDIO_DIR / "response.wav"

# Display original audio
display(Markdown("### Original Podcast Audio"), Audio(filename=str(input_audio)))

# Process pipeline
process_text(transcribe_audio(input_audio))

question = "What are the three AI projects mentioned?" #questions here

# Generate asnwer and display response audio
answer = generate_answer(question)
display(Markdown(f"**Answer:** {answer}"))
synthesize_speech(answer, input_audio, output_audio)
display(Markdown("### Generated Response Audio"), Audio(filename=str(output_audio)))

#%%