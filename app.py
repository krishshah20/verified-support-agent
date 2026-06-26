import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from src.api.response_generator import ResponseGenerator

# Page config
st.set_page_config(page_title="FastAPI Support Agent", layout="wide")

st.title("🚀 FastAPI Support Agent")
st.markdown("Ask questions about FastAPI. Get verified answers with citations.")

# Initialize generator
@st.cache_resource
def load_generator():
    generator = ResponseGenerator()
    generator.load_chunks()
    return generator

generator = load_generator()

# Input
with st.container():
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input("Ask a question about FastAPI:", placeholder="e.g., How do I use dependency injection?")
    with col2:
        search_button = st.button("Search", use_container_width=True)

# Results
if search_button and query:
    with st.spinner("Searching and verifying..."):
        response = generator.generate_response(query, top_k=3)
    
    # Answer section
    st.markdown("---")
    st.subheader("📝 Answer")
    st.write(response['answer'])
    
    # Confidence
    confidence = response['confidence']
    if confidence > 0.7:
        st.success(f"✅ Confidence: {confidence:.1%}")
    elif confidence > 0.5:
        st.info(f"⚠️ Confidence: {confidence:.1%}")
    else:
        st.warning(f"❌ Confidence: {confidence:.1%}")
    
    # Citations
    st.markdown("---")
    st.subheader("📚 Verified Citations")
    
    if response['citations']:
        for i, cite in enumerate(response['citations'], 1):
            with st.expander(f"Citation {i} (Confidence: {cite['confidence']:.1%})"):
                st.write(cite['text'])
                st.caption(f"Source: {cite['source']} | ID: {cite['chunk_id']}")
    else:
        st.warning("No verified citations found.")
    
    # Stats
    st.markdown("---")
    st.subheader("📊 Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Chunks Retrieved", response['retrieved_chunks_count'])
    with col2:
        st.metric("Citations Verified", response['verified_citations_count'])
    with col3:
        st.metric("Confidence Score", f"{response['confidence']:.2f}")

# Footer
st.markdown("---")
st.caption("Week 1 RAG System | Retrieval + Citation Verification + Grounded Generation")