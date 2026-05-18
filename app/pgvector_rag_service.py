from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from app.prompts import INCIDENT_ANALYSIS_PROMPT
from app.postgres_service import (
    delete_chunks_by_source,
    save_document_chunk_pg,
    search_similar_chunks_pg
)

# Función para indexar un documento en PostgreSQL utilizando pgvector
def index_document_pgvector(content, source_name):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    docs = [
        Document(
            page_content=content,
            metadata={"source": source_name}
        )
    ]

    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    delete_chunks_by_source(source_name)

    for chunk in chunks:
        embedding = embeddings.embed_query(chunk.page_content)
        save_document_chunk_pg(
            source=source_name,
            chunk_text=chunk.page_content,
            embedding=str(embedding)
        )

    return len(chunks)

# Función para responder preguntas utilizando pgvector para recuperar chunks relevantes
def answer_question_pgvector(question, k=4):
    similar_chunks = search_similar_chunks_pg(question, limit=k)

    context = "\n\n".join([row.chunk_text for row in similar_chunks])

    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    chain = INCIDENT_ANALYSIS_PROMPT | llm

    response = chain.invoke({
        "context": context,
        "question": question
    })

    return response.content, similar_chunks