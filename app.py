import streamlit as st
import requests

# 1. Premium Visual Branding & Theme Setup
st.set_page_config(
    page_title="AI Document Finder",
    page_icon="🔍",
    layout="wide",  # Uses the full horizontal screen for a modern dashboard look
    initial_sidebar_state="collapsed"
)

# Custom Minimalist CSS Injection for Polished Typography and Clean Buttons
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; max-width: 900px; }
    h1 { font-weight: 800; color: #1E293B; letter-spacing: -0.05em; margin-bottom: 0.5rem; }
    .stButton>button { 
        width: 100%; border-radius: 8px; font-weight: 600; 
        background-color: #2563EB; color: white; border: none;
        transition: all 0.2s ease;
    }
    .stButton>button:hover { background-color: #1D4ED8; transform: translateY(-1px); }
    </style>
""", unsafe_allow_html=True)

# Main Title Headers
st.title("🔍 Intelligent Document Finder AI")
st.caption("⚡ Modern full-stack semantic search engine powered by vector indexing backends.")
st.write("---")

# 🧠 Initialize state memory structures so text outputs survive button rerun clicks
if "ai_answer" not in st.session_state:
    st.session_state.ai_answer = None
if "current_question" not in st.session_state:
    st.session_state.current_question = None

# 📊 Isolated function to fetch database log history arrays cleanly
def display_chat_history():
    st.markdown("### 📜 System Log History")
    st.caption("Relational database transaction table logs retrieved directly out of SQLite.")
    try:
        # 🔧 Updated to target port 8000 where your FastAPI runs natively
        history_response = requests.get("http://localhost:8000/history")
        if history_response.status_code == 200:
            logs = history_response.json()["history"]
            if not logs:
                st.info("No prior workspace query entries indexed in database logs yet.")
            else:
                # Loop through logs backwards to show the newest question first
                for log in logs:
                    with st.container():
                        st.markdown(f"**🧑 User Search:** {log['user']}")
                        st.markdown(f"**🤖 System Output:** {log['ai']}")
                        st.markdown("<div style='border-bottom: 1px solid #E2E8F0; margin: 10px 0;'></div>", unsafe_allow_html=True)
    except Exception:
        st.error("⚠️ Connection Error: Unable to access relational SQL history endpoints.")

# 📑 Modern Workspace Tab Layout Split
tab1, tab2, tab3 = st.tabs(["📁 Knowledge Base Ingestion", "💬 AI Search Engine", "📊 System History Logs"])

# --- TAB 1: DATA INGESTION ---
with tab1:
    st.markdown("### 📁 Ingest Local Reference Files")
    st.write("Upload unstructured raw text data down into the background permanent vector storage layers.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        doc_id = st.text_input("Assign Unique Reference ID:", placeholder="e.g., standard_operating_procedures_2026")
    with col2:
        doc_text = st.text_area("Document Context / Body Text Content:", placeholder="Paste text data strings here...")
        
    if st.button("Index Document to Vector DB", key="ingest_btn"):
        if doc_id and doc_text:
            payload = {"docs_id": doc_id, "text": doc_text}
            try:
                # Using st.status for a highly polished operational tracking look
                with st.status("Processing database matrix chunking operations...", expanded=True) as status:
                    response = requests.post("http://localhost:8000/add_docs", json=payload)
                    if response.status_code == 200:
                        status.update(label="✅ Vector database write complete!", state="complete", expanded=False)
                        st.success(f"Success: {response.json()['message']}")
                    else:
                        status.update(label="❌ Upload Pipeline Encountered Issues", state="error")
                        st.error(f"Error Code {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Link Error: Verify that your FastAPI backend is live on port 8000.")
        else:
            st.warning("⚠️ Attention: Please satisfy both inputs before initializing vector database writes.")

# --- TAB 2: CONVERSATIONAL QUERY LAYER ---
with tab2:
    st.markdown("### 💬 Ask the AI Document Finder")
    st.write("The AI scans millions of vectors to ground its response using *only* your uploaded context data.")
    
    user_query = st.text_input("Enter your query:", placeholder="e.g., What are the corporate clothing parameters on Fridays?")
    
    if st.button("Search System & Generate Answer", key="query_btn"):
        if user_query:
            payload = {"prompt": user_query}
            try:
                with st.spinner("Executing similarity search operations and generating response..."):
                    response = requests.post("http://localhost:8000/query", json=payload)
                if response.status_code == 200:
                    # 🔧 FIX: Save response variables cleanly to cache state so they don't erase on page reruns
                    st.session_state.ai_answer = response.json()["ai_answer"]
                    st.session_state.current_question = user_query
                else:
                    st.error(f"❌ Core Error: Server returned error status code {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Link Error: Verify that your FastAPI backend is live on port 8000.")
        else:
            st.warning("⚠️ Attention: Type a query prompt sequence first.")

    # 🔧 FIX: Render output window strings independently using native Chat UI elements
    if st.session_state.ai_answer:
        st.write("---")
        st.markdown("#### 🎯 Execution Engine Output")
        
        # Renders a neat user question speech bubble
        with st.chat_message("user"):
            st.write(st.session_state.current_question)
            
        # Renders a polished robot answer response block instantly on 1st click
        with st.chat_message("assistant"):
            st.write(st.session_state.ai_answer)

# --- TAB 3: SYSTEM TRANSACTION LOGS ---
with tab3:
    display_chat_history()
