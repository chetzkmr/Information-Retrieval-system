import streamlit as st
from src.helper import get_pdf_text, get_text_chunks, get_vector_store, get_conversation_chain


def main():
    st.set_page_config(page_title="PDF Reader", page_icon="📄")
    st.header("📄 PDF Reader with LangChain")

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    # Sidebar
    with st.sidebar:
        st.title("Menu")
        pdf_docs = st.file_uploader(
            "Upload your PDF files here and click on 'Process'",
            accept_multiple_files=True
        )

        if st.button("Process"):
            if pdf_docs:
                with st.spinner("Processing..."):
                    raw_text = get_pdf_text(pdf_docs)
                    text_chunks = get_text_chunks(raw_text)
                    vector_store = get_vector_store(text_chunks)
                    st.session_state.conversation = get_conversation_chain(vector_store)

                st.success("PDF files processed successfully!")
            else:
                st.warning("Please upload at least one PDF.")

    # Chat input
    user_question = st.text_input("Ask a question about your PDF:")

    if user_question and st.session_state.conversation:
        response = st.session_state.conversation({'question': user_question})
        st.write(response['answer'])


if __name__ == "__main__":
    main()