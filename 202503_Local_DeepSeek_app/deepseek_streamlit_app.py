#%%
# Import libraries
import json
import os
import re
import tempfile
from io import BytesIO
import pandas as pd
import plotly.express as px
import streamlit as st
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain_nvidia_ai_endpoints import ChatNVIDIA

#%%
# get your deepseek api from https://build.nvidia.com/deepseek-ai/deepseek-r1/deploy
deepseek_api = your_api

# %%
# streamlit app
# Set page config
st.set_page_config(
    page_title="Transaction Dashboard",
    page_icon="💰",
    layout="wide"
)

@st.cache_data
def load_data(file_content, api):
    try:
        # Create a file-like object from the uploaded file: reading without saving it to disk
        file_stream = BytesIO(file_content)
        
        # Save to a temporary file (PyPDFLoader requires a file path)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(file_stream.getbuffer())
            temp_file_path = temp_file.name
        
        try:
            # Load the PDF
            loader = PyPDFLoader(temp_file_path)
            data = loader.load()
            
            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000, 
                chunk_overlap=200  
            )
            texts = text_splitter.split_documents(data)

            # Initialize deepseek through NVIDIA NIM
            client = ChatNVIDIA(
                model="deepseek-ai/deepseek-r1",
                api_key=api,
                temperature=1,
                top_p=0.8,
                max_tokens=4096 
            )

            # Create RAG chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=client, 
                chain_type="stuff",
                retriever=FAISS.from_documents(
                    texts,
                    HuggingFaceEmbeddings()  
                ).as_retriever(search_kwargs={"k": 5}),
                return_source_documents=False
            )

            query = f"""Analyze this card invoice and categorize transactions into exactly 5 categories:
                    - Groceries
                    - Entertainment
                    - Restaurants
                    - Transportation
                    - Other

                    Return ONLY a JSON array with:
                    - date (YYYY-MM-DD)
                    - description (string, item name)
                    - category (string, matching above list)
                    - amount (float)

                    Example:
                    {{
                        "transactions": [
                            {{
                                "date": "2025-02-15",
                                "description": "Hemköp",
                                "category": "Groceries",
                                "amount": 23.45
                            }}
                        ]
                    }} """
            result = qa_chain.invoke({"query": query})

            # Extract JSON content
            json_match = re.search(r'```json(.*?)```', result["result"], re.DOTALL)
            if not json_match:
                raise ValueError("No JSON data found in LLM response")
                
            json_str = json_match.group(1).strip()
            data_out = json.loads(json_str)

            return data_out
            
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None

# Streamlit app
st.title("💰 Transaction Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF invoice", type="pdf")

if uploaded_file is not None:
    if deepseek_api:
        try:
            # Read the uploaded file content
            file_content = uploaded_file.read()
            
            # Process the file
            with st.spinner("Processing PDF..."):
                data = load_data(file_content, api=deepseek_api)
            
            if data and "transactions" in data:
                # Create dataframe
                df = pd.DataFrame(data["transactions"])
                
                if not df.empty:
                    try:
                        df['date'] = pd.to_datetime(df['date'])
                        df['amount'] = df['amount'].astype(float)
                        
                        # Display results
                        st.success("PDF processed successfully!")
                        st.dataframe(df)
                        
                        # Show summary statistics
                        st.subheader("Summary by Category")
                        summary = df.groupby('category')['amount'].agg(['sum', 'count'])
                        st.dataframe(summary)
                        
                        # Color palette
                        COLOR_PALETTE = {
                            'Groceries': '#66C2A5',
                            'Restaurants': '#FC8D62',
                            'Transportation': '#8DA0CB',
                            'Entertainment': '#E78AC3',
                            'Other': '#A6D854'
                        }

                        # =====================================================================
                        # 1. Create the visualizations
                        # =====================================================================

                        # Daily totals line chart
                        daily_totals = df.groupby('date')['amount'].sum().reset_index()
                        fig1 = px.line(
                            daily_totals,
                            x='date',
                            y='amount',
                            labels={'amount': 'Amount (SEK)', 'date': ''},
                            markers=True,
                            color_discrete_sequence=['#2CA02C']
                        )
                        fig1.update_traces(
                            line_width=2.5,
                            marker_size=8,
                            hovertemplate="<b>%{x|%b %d}</b><br>Total: <b>%{y:.2f} SEK</b>"
                        )
                        fig1.update_layout(
                            xaxis=dict(showgrid=False, tickformat='%b %d', linecolor='#e6e6e6'),
                            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', linecolor='#e6e6e6'),
                            plot_bgcolor='white',
                            margin=dict(l=40, r=20, t=40, b=40)
                        )

                        # Category breakdown pie chart
                        category_totals = df.groupby('category')['amount'].sum().reset_index()
                        fig2 = px.pie(
                            category_totals,
                            values='amount',
                            names='category',
                            hole=0.5,
                            color='category',
                            color_discrete_map=COLOR_PALETTE
                        )
                        fig2.update_traces(
                            textposition='inside',
                            textinfo='percent',
                            hovertemplate="<b>%{label}</b><br>%{value:.2f} SEK (%{percent})",
                            marker=dict(line=dict(color='white', width=1))
                        )
                        fig2.update_layout(
                            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                            margin=dict(l=20, r=20, t=40, b=40)
                        )

                        # Tables
                        stats_data = {
                            "Metric": ["Total Amount", "Transaction Count", "Largest Transaction", "Smallest Transaction"],
                            "Value": [
                                f"{df['amount'].sum():.2f} SEK",
                                len(df),
                                f"{df['amount'].max():.2f} SEK",
                                f"{df['amount'].min():.2f} SEK"
                            ]
                        }

                        top_merchants = df['description'].value_counts().head(5).reset_index()
                        top_merchants.columns = ['Merchant', 'Visit Count']

                        # =====================================================================
                        # 2. Display in Streamlit
                        # =====================================================================

                        # Tables row
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("### Transaction Statistics")
                            st.dataframe(
                                pd.DataFrame(stats_data),
                                hide_index=True,
                                use_container_width=True
                            )

                        with col2:
                            st.markdown("### Top 5 Merchants")
                            st.dataframe(
                                top_merchants,
                                hide_index=True,
                                use_container_width=True
                            )

                        # Charts row
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("### Daily Transaction Trends")
                            st.plotly_chart(fig1, use_container_width=True)

                        with col2:
                            st.markdown("### Spending by Category")
                            st.plotly_chart(fig2, use_container_width=True)

                        # =====================================================================
                        # 3. RAG Section at the Bottom
                        # =====================================================================

                        st.markdown("---")
                        st.header("🔍 Ask Questions About Your Transactions")

                        @st.cache_resource
                        def setup_rag_chain(_df):
                            # Convert to documents
                            documents = []
                            for i, row in _df.iterrows():
                                content = (f"Date: {row['date']}, "
                                        f"Description: {row['description']}, "
                                        f"Category: {row['category']}, "
                                        f"Amount: {row['amount']} SEK")
                                
                                metadata = {
                                    'date': row['date'],
                                    'description': row['description'],
                                    'category': row['category'],
                                    'amount': row['amount'],
                                    'index': i
                                }
                                
                                documents.append(Document(page_content=content, metadata=metadata))

                            # Define QA prompt template
                            qa_prompt = """
                            Use the following transaction records to answer the question. 
                            If you don't know the answer, just say you don't know, don't try to make up an answer.

                            Context:
                            {context}

                            Question: {question}
                            Answer:"""

                            # Initialize LLM
                            llm = Ollama(model="deepseek-r1:14b")

                            # Create and return QA chain
                            return RetrievalQA.from_chain_type(
                                llm=llm,
                                chain_type="stuff",
                                retriever=FAISS.from_documents(
                                    documents,
                                    HuggingFaceEmbeddings()
                                ).as_retriever(search_kwargs={"k": 5}),
                                chain_type_kwargs={
                                    "prompt": PromptTemplate.from_template(qa_prompt)
                                },
                                return_source_documents=True
                            )

                        # Initialize RAG chain
                        qa_chain = setup_rag_chain(df)

                        # Question input
                        question = st.text_input("Ask a question about your transactions:", 
                                                placeholder="E.g., 'When did I go to Odenplan Thai Market?'")

                        if question:
                            with st.spinner("Searching your transactions..."):
                                try:
                                    response = qa_chain.invoke({"query": question})
                                    st.markdown(f"**Answer:** {response['result']}")
                                    
                                    # Show source transactions if available
                                    if response.get('source_documents'):
                                        st.markdown("**Relevant transactions used:**")
                                        sources = []
                                        for doc in response['source_documents']:
                                            sources.append({
                                                'Date': doc.metadata['date'],
                                                'Description': doc.metadata['description'],
                                                'Category': doc.metadata['category'],
                                                'Amount': f"{doc.metadata['amount']} SEK"
                                            })
                                        st.dataframe(pd.DataFrame(sources), hide_index=True)
                                except Exception as e:
                                    st.error(f"Error processing your question: {str(e)}")
                        
                    except KeyError:
                        st.error("LLM failed to extract transaction data properly")
                    except Exception as e:
                        st.error(f"Error processing transactions: {str(e)}")
                else:
                    st.warning("No transactions found in the PDF")
            else:
                st.error("Failed to process PDF or no transaction data returned")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")