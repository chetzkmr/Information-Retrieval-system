import os
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

# -------------------------
# Load API key
# -------------------------
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


# -------------------------
# Extract PDF text
# -------------------------
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
    return text


# -------------------------
# Chunking
# -------------------------
def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return splitter.split_text(text)


# -------------------------
# Embeddings + Vector DB
# -------------------------
def get_vector_store(text_chunks, save_path="faiss_index"):

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Always rebuild when new PDFs uploaded
    if os.path.exists(save_path):
        import shutil
        shutil.rmtree(save_path)

    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local(save_path)

    return vector_store


# -------------------------
# Conversational RAG chain
# -------------------------
def get_conversation_chain(vector_store):

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        streaming=True,
        convert_system_message_to_human=True
    )

    memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
    )

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        memory=memory,
        return_source_documents=True
    )