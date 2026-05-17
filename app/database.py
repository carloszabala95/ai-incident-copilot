import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/interactions.db")

# Función para inicializar la base de datos
def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            source TEXT,
            latency_seconds REAL,
            feedback TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# Función para guardar una nueva interacción
def save_interaction(question, answer, source, latency_seconds):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO interactions (
            question,
            answer,
            source,
            latency_seconds,
            feedback,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        question,
        answer,
        source,
        latency_seconds,
        None,
        datetime.now().isoformat(timespec="seconds")
    ))

    interaction_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return interaction_id

# Función para actualizar el feedback de una interacción
def update_feedback(interaction_id, feedback):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE interactions
        SET feedback = ?
        WHERE id = ?
    """, (feedback, interaction_id))

    conn.commit()
    conn.close()

#   Función para obtener las interacciones más recientes
def get_recent_interactions(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, question, answer, source, latency_seconds, feedback, created_at
        FROM interactions
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return rows
#   Función para obtener métricas clave de la base de datos
def get_metrics():
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Obtener el total de interacciones
    cursor.execute("SELECT COUNT(*) FROM interactions")
    total_interactions = cursor.fetchone()[0]
    # Obtener la latencia promedio
    cursor.execute("SELECT AVG(latency_seconds) FROM interactions")
    avg_latency = cursor.fetchone()[0] or 0
    # Obtener el conteo de feedback positivo, negativo y sin feedback
    cursor.execute("SELECT COUNT(*) FROM interactions WHERE feedback = 'positive'")
    positive_feedback = cursor.fetchone()[0]
    # Obtener el conteo de feedback negativo
    cursor.execute("SELECT COUNT(*) FROM interactions WHERE feedback = 'negative'")
    negative_feedback = cursor.fetchone()[0]
    # Obtener el conteo de interacciones sin feedback
    cursor.execute("SELECT COUNT(*) FROM interactions WHERE feedback IS NULL")
    without_feedback = cursor.fetchone()[0]
    # Cerrar la conexión a la base de datos
    conn.close()

    return {
        "total_interactions": total_interactions,
        "avg_latency": round(avg_latency, 2),
        "positive_feedback": positive_feedback,
        "negative_feedback": negative_feedback,
        "without_feedback": without_feedback
    }