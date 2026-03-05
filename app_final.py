import os
import streamlit as st
import tempfile
import time

# --- Required Libraries ---
# Local Embedding & General Utils
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Cloud & Local LLM Providers
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import OllamaLLM

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Fin-Insight: Dual-Engine RAG",
    page_icon="📈",
    layout="wide"
)

# --- 2. Sidebar: Model Selection & Status ---
with st.sidebar:
    st.title("⚙️ System Control")
    st.divider()
    
    # Selection Toggle
    engine_choice = st.radio(
        "Select Intelligence Engine:",
        ["Gemini 2.5 Flash (Cloud Hybrid)", "Ollama Llama3 (Full Local)"],
        index=0,
        help="Switch between high-performance cloud or private local processing."
    )
    
    st.divider()
    st.subheader("Current Config")
    if "Gemini" in engine_choice:
        st.success("Mode: Cloud Reasoning")
        st.info("Brain: Gemini 2.5\nEyes: Local BGE-Small")
    else:
        st.warning("Mode: Privacy/Offline")
        st.info("Brain: Ollama (Local)\nEyes: Local BGE-Small")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- 3. Shared Resource: Local Embedding (BAAI/bge-small-en-v1.5) ---
@st.cache_resource
def load_embeddings():
    # Using Local Embeddings to bypass Gemini 429 limits
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={'device': 'cpu'}
    )

embeddings = load_embeddings()

# --- 4. Initialize the Selected LLM ---
def initialize_llm(mode):
    if "Gemini" in mode:
        # Use key from your provided gemini script
        os.environ["GOOGLE_API_KEY"] = "Your_Google_API_Key_Here"
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)
    else:
        # Based on your ollama script logic
        return OllamaLLM(model="mistral", temperature=0.5)

llm = initialize_llm(engine_choice)

# --- 5. Main UI & PDF Upload ---
st.title("📈 Financial PDF Explorer")
st.caption("Upload your 10-K or financial reports for instant AI analysis.")

uploaded_files = st.file_uploader("Upload PDFs", accept_multiple_files=True, type=["pdf"])

if uploaded_files:
    # Use session_state to share vector store between model switches
    if "vector_store" not in st.session_state:
        with st.spinner("Indexing documents locally..."):
            all_docs = []
            with tempfile.TemporaryDirectory() as temp_dir:
                for file in uploaded_files:
                    temp_path = os.path.join(temp_dir, file.name)
                    with open(temp_path, "wb") as f:
                        f.write(file.getbuffer())
                    
                    loader = PyPDFLoader(temp_path)
                    all_docs.extend(loader.load())

                # Split documents logic from both versions
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                docs = text_splitter.split_documents(all_docs)
                
                # Create FAISS vector store locally
                st.session_state.vector_store = FAISS.from_documents(docs, embeddings)
        st.success(f"✅ Successfully indexed {len(docs)} chunks!")

    # --- 6. Chat Interface ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask about financial trends, risks, or numbers...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Build History String logic from your files
        chat_history_str = ""
        if len(st.session_state.messages) > 1:
            for msg in st.session_state.messages[:-1]:
                role = "User" if msg["role"] == "user" else "Assistant"
                chat_history_str += f"{role}: {msg['content']}\n\n"
        
        # Retrieval Setup
        retriever = st.session_state.vector_store.as_retriever(search_kwargs={"k": 4})
        
        template = (
            "You are a professional financial assistant.\n"
            "Use the provided context to answer the user request.\n\n"
            "Context: {context}\n"
            "History: " + chat_history_str
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", "{input}"),
        ])

        # Create Retrieval Chain
        doc_chain = create_stuff_documents_chain(llm, prompt)
        qa_chain = create_retrieval_chain(retriever, doc_chain)

        with st.spinner(f"{engine_choice} is analyzing..."):
            response = qa_chain.invoke({"input": user_input})
            ans = response["answer"]
            
        with st.chat_message("assistant"):
            st.markdown(ans)
            # Add Source Context (inspired by your Ollama version)
            with st.expander("🔍 View Reference Context"):
                for i, doc in enumerate(response["context"]):
                    st.caption(f"Source {i+1} (Page {doc.metadata.get('page','?')})")
                    st.write(doc.page_content[:300] + "...")
                
        st.session_state.messages.append({"role": "assistant", "content": ans})

else:
    st.info("Welcome! Please upload financial PDF documents in the sidebar to start.")