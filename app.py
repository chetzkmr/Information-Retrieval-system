import streamlit as st
from src.helper import (
    get_pdf_text,
    get_text_chunks,
    get_vector_store,
    get_conversation_chain
)

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="PDF Chatbot",
    page_icon="🤖",
    layout="wide"
)


# -------------------------
# Session State
# -------------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# -------------------------
# Sidebar
# -------------------------
with st.sidebar:
    st.title("📂 Upload PDFs")

    pdf_docs = st.file_uploader(
        "Upload your PDF files",
        accept_multiple_files=True
    )

    if st.button("Process"):
        if not pdf_docs:
            st.warning("Please upload PDFs")
        else:
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                chunks = get_text_chunks(raw_text)
                vector_store = get_vector_store(chunks)

                st.session_state.conversation = get_conversation_chain(vector_store)

            st.success("Done!")


# -------------------------
# Chat UI
# -------------------------
st.header("🤖 Chat with your documents (Gemini API)")

# Show history
for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(msg)


# Input
user_question = st.chat_input("Ask anything about your PDF")

if user_question:
    if not st.session_state.conversation:
        st.warning("Upload and process PDFs first")
        st.stop()

    # Show user message
    st.session_state.chat_history.append(("user", user_question))
    with st.chat_message("user"):
        st.markdown(user_question)

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            response = st.session_state.conversation(
                {"question": user_question}
            )

            answer = response["answer"]
 
            # Streaming effect
            placeholder = st.empty()
            full_text = ""
            for word in answer.split():
                full_text += word + " "
                placeholder.markdown(full_text + "▌")

            placeholder.markdown(full_text)

    # Save assistant message
    st.session_state.chat_history.append(("assistant", answer))