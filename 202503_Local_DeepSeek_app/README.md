# Local LLM Streamlit App for Transaction Analysis  

A Streamlit app that processes invoices, generates reports, and provides Q&A assistance — powered by local AI, with a little cloud help for the heavy lifting.

## 🛠 Features  
- **Upload a document** for example a credit card invoice (PDF) 
- **Extract and analyze transactions** using a cloud-based LLM (can also be done locally if hardware allows)
- **Generate reports** with tables & graphs
- **Ask questions about your transactions** using a local LLM  

## ⚙️ Tech Stack  
- **LLM:** DeepSeek-R1
- **Vector DB:** FAISS (by Meta AI)  
- **Embeddings:** Hugging Face  
- **App Framework:** Streamlit  
- **Cloud Processing:** NVIDIA NIM
- **Local Processing:** Ollama

## 💻 To start the Streamlit app, open a terminal and run: 
```bash
streamlit run deepseek_streamlit_app.py
```

## 📖 Read the Full Story on Medium
[**Build an LLM App with Local DeepSeek – No Budget, Just a Laptop**](https://medium.com/@t40r417/build-an-llm-app-with-local-deepseek-no-budget-just-a-laptop-973478a93903)  
