#%%
import re
import torch
import streamlit as st
from pathlib import Path
import whisper
from TTS.api import TTS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain_text_splitters import RecursiveCharacterTextSplitter
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig

# Constants
LLLM_MODEL = "deepseek-r1:latest"
TTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"

TEMPLATE = """You are a helpful and accurate question-answering assistant.
Your primary goal is to answer the user's `Question` based on the `Context` provided below.

If the `Context` does not contain sufficient information to answer the question, please state clearly that you do not have enough information from the provided context. Do not make up answers.

Keep your answer concise.

Question: {question}
Context: {context}
Answer:"""

# Session state initialization
if "vector_store" not in st.session_state:
    st.session_state.vector_store = InMemoryVectorStore(OllamaEmbeddings(model=LLLM_MODEL))

@st.cache_resource
def load_models():
    """Load ML models once and cache them"""
    return {
        "whisper": whisper.load_model("medium.en"),
        "tts": TTS(TTS_MODEL).to("cuda" if torch.cuda.is_available() else "mps"),
        "llm": OllamaLLM(model=LLLM_MODEL)
    }

def clean_text(text):
    """Clean the text by removing think tags"""
    return re.compile(r"<think>.*?</think>", flags=re.DOTALL).sub("", text).strip()

def process_audio(uploaded_file, models):
    """Handle audio processing pipeline"""
    with st.spinner("Processing audio...This might take a moment for larger files."):
        # Save uploaded file
        audio_path = Path("uploaded_audio.wav")
        audio_path.write_bytes(uploaded_file.getbuffer())
        
        st.info("Transcribing audio...")
        text = models["whisper"].transcribe(str(audio_path))["text"]
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        st.session_state.vector_store.add_texts(splitter.split_text(text))
        st.success("Transcript indexed and ready for Q&A!")

        return audio_path, text

def main():
    """Main function to run the Streamlit app"""
    st.set_page_config(
        page_title="AI Audio Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🎧 AI Audio Assistant")
    st.markdown("""
    Welcome to your AI Audio Assistant! Drop in a podcast or lecture, and I’ll transcribe it 📝, answer your questions 💬, and even reply in the speaker’s voice 🎙️.
    """)

    with st.status("Loading AI models... This might take a moment, especially on first run.", expanded=True) as status:
        models = load_models()
    st.success("All systems go! Models are ready to assist.")

    # Create two columns for side-by-side layout
    col1, col2 = st.columns(2, gap="large")

    # Left column - Audio Upload & Transcript
    with col1:
        with st.container(border=True):
            st.subheader("1. Upload Your Audio 🎤")
            uploaded_file = st.file_uploader("Choose an audio file (WAV or MP3)", type=["wav", "mp3"])

            if uploaded_file:
                audio_path, transcript = process_audio(uploaded_file, models)

                st.markdown("### Original Audio Playback")
                st.audio(str(audio_path), format='audio/wav') 

                with st.expander("View Full Transcript 📝"): 
                    st.write(transcript)
            else:
                st.info("Upload an audio file to get started!")

    # Right column - Q&A Section
    with col2:
        with st.container(border=True):
            st.subheader("2. Ask a Question About the Audio ❓")
            question = st.text_input(
                "Enter your question here:",
                placeholder="e.g., What AI projects were mentioned?",
                key="question_input" 
            )

            if question:
                if not uploaded_file:
                    st.warning("Please upload an audio file first before asking a question.")
                else:
                    with st.spinner("Generating answer... This may take a moment as the AI processes your query."):
                        # Retrieve relevant documents from the vector store 
                        docs = st.session_state.vector_store.similarity_search(question)
                        context = "\n\n".join(doc.page_content for doc in docs) 

                        # Invoke the LLM with the question and context
                        prompt = ChatPromptTemplate.from_template(TEMPLATE)
                        answer = clean_text((prompt | models["llm"]).invoke({"question": question, "context": context}))

                        st.markdown("### 💡 Answer:")
                        st.success(f"{answer}") 

                        # Generate audio response using TTS
                        output_path = "response.wav"
                        try:
                            models["tts"].tts_to_file(
                                text=answer,
                                speaker_wav=str(audio_path),
                                language="en",
                                file_path=output_path
                            )
                            st.markdown("### 🎙️ Listen to the Answer:")
                            st.audio(output_path, format='audio/wav') 
                        except Exception as e:
                            st.error(f"Error generate audio response: {e}")
            else:
                st.info("Type your question above to get an answer from the audio content.")


if __name__ == "__main__":
    # Add these classes to PyTorch's safe globals list for compatibility 
    torch.serialization.add_safe_globals([
        XttsConfig,
        XttsAudioConfig,
        BaseDatasetConfig,
        XttsArgs
    ])
    main()

#%%
