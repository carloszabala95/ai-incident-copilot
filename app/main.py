import time
import streamlit as st
from dotenv import load_dotenv

# Importar servicios para sustituir Sqlite por PostgreSQL
from app.postgres_service import test_connection, save_interaction_pg, update_feedback_pg, get_recent_interactions_pg, get_category_metrics_pg, get_metrics_pg

from app.file_service import read_uploaded_file, get_file_preview
from app.rag_service import create_vectorstore_from_text, answer_question
from app.error_classifier import classify_incident
from app.metrics_service import build_category_chart_data
from app.postgres_service import test_connection

load_dotenv()
# Inicializar la base de datos
##init_db() solo para el Sqlite . Inhabilitado porque ahora usamos PostgreSQL ahora
# Configuración de la página
st.set_page_config(
    page_title="SoftIA - AI Incident Support Copilot",
    page_icon="🛠️",
    layout="wide"
)
# Título principal
st.title("🛠️ SoftIA - AI Incident Support Copilot")
st.write("Asistente RAG para analizar logs, incidentes y errores técnicos.")
# Probar conexión a la base de datos
postgres_version = test_connection()

st.sidebar.divider()
st.sidebar.subheader("PostgreSQL")

st.sidebar.success("Conexión OK")

st.sidebar.caption(postgres_version)
# Inicializar variables de sesión
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "incident_category" not in st.session_state:
    st.session_state.incident_category = None

if "source_name" not in st.session_state:
    st.session_state.source_name = None

# Barra lateral con métricas y categorías
st.sidebar.title("📊 AI Observability")

metrics = get_metrics_pg()

st.sidebar.metric("Total consultas", metrics["total_interactions"])
st.sidebar.metric("Latencia promedio", f'{metrics["avg_latency"]} s')
st.sidebar.metric("Feedback positivo", metrics["positive_feedback"])
st.sidebar.metric("Feedback negativo", metrics["negative_feedback"])
st.sidebar.metric("Sin feedback", metrics["without_feedback"])
# Categorías de incidentes y patrones asociados
st.sidebar.divider()
st.sidebar.subheader("Incidentes por categoría")

category_metrics = get_category_metrics_pg()

if category_metrics:
    for category, total in category_metrics:
        st.sidebar.write(f"**{category}:** {total}")
else:
    st.sidebar.write("Sin categorías registradas")

uploaded_file = st.file_uploader(
    "Sube un archivo .txt o .log",
    type=["txt", "log"]
)

if uploaded_file:
    content = read_uploaded_file(uploaded_file)
    source_name = uploaded_file.name

    st.session_state.source_name = source_name

    st.subheader("Vista previa del archivo")
    st.text(get_file_preview(content))

    incident_category = classify_incident(content)
    st.session_state.incident_category = incident_category

    st.subheader("Clasificación automática")
    st.info(f"📌 Categoría detectada: {incident_category}")

    if st.button("Procesar archivo"):
        vectorstore, chunks_count = create_vectorstore_from_text(
            content=content,
            source_name=source_name
        )

        st.session_state.vectorstore = vectorstore

        st.success(f"Archivo procesado correctamente. Chunks generados: {chunks_count}")

st.divider()

question = st.text_input("Haz una pregunta sobre el incidente o log:")

if question and st.session_state.vectorstore:
    start_time = time.time()

    answer, relevant_docs = answer_question(
        vectorstore=st.session_state.vectorstore,
        question=question
    )

    latency_seconds = round(time.time() - start_time, 2)

    interaction_id = save_interaction_pg(
        question=question,
        answer=answer,
        source=st.session_state.source_name or "unknown",
        category=st.session_state.incident_category or "Unknown",
        latency_seconds=latency_seconds
    )

    st.session_state.last_interaction_id = interaction_id

    st.subheader("Respuesta")
    st.write(answer)

    st.write(f"⏱️ Latencia: {latency_seconds} segundos")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("👍 Respuesta útil"):
            update_feedback_pg(st.session_state.last_interaction_id, "positive")
            st.success("Feedback positivo registrado.")

    with col2:
        if st.button("👎 Respuesta no útil"):
            update_feedback_pg(st.session_state.last_interaction_id, "negative")
            st.warning("Feedback negativo registrado.")

    with st.expander("Ver contexto recuperado"): # Mostrar los chunks relevantes recuperados
        for i, doc in enumerate(relevant_docs, start=1):
            st.markdown(f"### Chunk {i}")
            st.text(doc.page_content)

elif question and not st.session_state.vectorstore:
    st.warning("Primero debes subir y procesar un archivo.")

st.divider()
st.subheader("📌 Distribución de incidentes por categoría")

category_metrics = get_category_metrics_pg()

if category_metrics:
    category_data = build_category_chart_data(category_metrics)

    st.bar_chart(
        data=category_data,
        x="Categoría",
        y="Total"
    )
else:
    st.info("Aún no hay suficientes datos para mostrar categorías.")

st.divider()
st.subheader("Historial reciente")

rows = get_recent_interactions_pg(limit=5)

for row in rows:
    interaction_id, question, answer, source, category, latency, feedback, created_at = row

    with st.expander(f"{created_at} - {question[:80]}"):
        st.write("**Pregunta:**")
        st.write(question)

        st.write("**Respuesta:**")
        st.write(answer)

        st.write("**Fuente:**", source)
        st.write("**Categoría:**", category)
        st.write("**Latencia:**", latency)
        st.write("**Feedback:**", feedback or "Sin feedback")