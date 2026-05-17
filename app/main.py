import streamlit as st
from dotenv import load_dotenv

from app.prompts import INCIDENT_ANALYSIS_PROMPT
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
## Fase 2 persistencia
import time
from app.database import init_db, save_interaction, update_feedback, get_recent_interactions, get_metrics
## Rule-based error classifier
from app.error_classifier import classify_incident


load_dotenv()

st.set_page_config(
    page_title="SoftIA - AI Incident Support Copilot",
    page_icon="🛠️",
    layout="wide"
)
# Inicializar la base de datos
init_db()
# Barra lateral con métricas clave
st.sidebar.title("📊 AI Observability")
# Obtener métricas clave de la base de datos
metrics = get_metrics()
# Mostrar métricas en la barra lateral
st.sidebar.metric("Total consultas", metrics["total_interactions"])
st.sidebar.metric("Latencia promedio", f'{metrics["avg_latency"]} s')
st.sidebar.metric("Feedback positivo", metrics["positive_feedback"])
st.sidebar.metric("Feedback negativo", metrics["negative_feedback"])
st.sidebar.metric("Sin feedback", metrics["without_feedback"])

# Título y descripción
st.title("🛠️ SoftIA - AI Incident Support Copilot")
st.write("Asistente RAG para analizar logs, incidentes y errores técnicos.")

uploaded_file = st.file_uploader(
    "Sube un archivo .txt o .log",
    type=["txt", "log"]
)
# Inicializar vectorstore en el estado de la sesión
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
# Procesar el archivo subido
if uploaded_file:
    # Leer el contenido del archivo
    content = uploaded_file.read().decode("utf-8", errors="ignore")
    # Clasificar el incidente utilizando el clasificador basado en reglas
    incident_category = classify_incident(content)

    st.subheader("Clasificación automática")
    st.info(f"📌 Categoría detectada: {incident_category}")
    # Mostrar una vista previa del contenido
    st.subheader("Vista previa del archivo")
    st.text(content[:2000])
    # Botón para procesar el archivo
    if st.button("Procesar archivo"):
        # Dividir el contenido en chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150
        )

        docs = [Document(page_content=content, metadata={"source": uploaded_file.name})]
        chunks = splitter.split_documents(docs)

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory="./data/chroma"
        )

        st.session_state.vectorstore = vectorstore

        st.success(f"Archivo procesado correctamente. Chunks generados: {len(chunks)}")

st.divider()

question = st.text_input("Haz una pregunta sobre el incidente o log:")

if question and st.session_state.vectorstore:
    retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 4})
    relevant_docs = retriever.invoke(question)

    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    prompt = INCIDENT_ANALYSIS_PROMPT
    # Medir el tiempo de respuesta del LLM
    start_time = time.time()
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    chain = prompt | llm

    response = chain.invoke({
        "context": context,
        "question": question
    })

    st.subheader("Respuesta")
    st.write(response.content)

    # Medir el tiempo de respuesta
    latency_seconds = round(time.time() - start_time, 2)
    # Obtener el nombre del archivo como fuente de la interacción
    source = uploaded_file.name if uploaded_file else "unknown"
    # Guardar la interacción en la base de datosy obtener el ID de la interacción recién guardada
    interaction_id = save_interaction(
        question=question,
        answer=response.content,
        source=source,
        category=incident_category,
        latency_seconds=latency_seconds
    )
    # Guardar el ID de la última interacción en el estado de la sesión para futuras referencias (como feedback)
    st.session_state.last_interaction_id = interaction_id
    # Mostrar el contexto recuperado

    with st.expander("Ver contexto recuperado"):
        for i, doc in enumerate(relevant_docs, start=1):
            st.markdown(f"### Chunk {i}")
            st.text(doc.page_content)

    st.write(f"⏱️ Latencia: {latency_seconds} segundos")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("👍 Respuesta útil"):
            update_feedback(st.session_state.last_interaction_id, "positive")
            st.success("Feedback positivo registrado.")

    with col2:
        if st.button("👎 Respuesta no útil"):
            update_feedback(st.session_state.last_interaction_id, "negative")
            st.warning("Feedback negativo registrado.")

elif question and not st.session_state.vectorstore:
    st.warning("Primero debes subir y procesar un archivo.")

st.divider()
st.subheader("Historial reciente")

rows = get_recent_interactions(limit=5)

for row in rows:
    interaction_id, question, answer, source, category, latency, feedback, created_at = row

    with st.expander(f"{created_at} - {question[:80]}"):
        st.write("**Pregunta:**")
        st.write(question)

        st.write("**Respuesta:**")
        st.write(answer)

        st.write("**Fuente:**", source)
        st.write("**Latencia:**", latency)
        st.write("**Feedback:**", feedback or "Sin feedback")
