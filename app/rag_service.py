from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from app.prompts import INCIDENT_ANALYSIS_PROMPT


def create_vectorstore_from_text(content, source_name, persist_directory="./data/chroma"):
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

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    return vectorstore, len(chunks)


def answer_question(vectorstore, question, k=4):
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    relevant_docs = retriever.invoke(question)

    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    chain = INCIDENT_ANALYSIS_PROMPT | llm

    response = chain.invoke({
        "context": context,
        "question": question
    })

    return response.content, relevant_docs