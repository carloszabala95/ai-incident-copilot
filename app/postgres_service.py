import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import text
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

engine = create_engine(DATABASE_URL)

## Este apartado lo hago para quitar SQLite  y asegurarme de que la conexión a PostgreSQL funciona correctamente.

def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))

        for row in result:
            return row[0]

# Guardar la interacción en PostgreSQL
def save_interaction_pg(question, answer, source, category, latency_seconds):
    with engine.begin() as connection:
        result = connection.execute(
            text("""
                INSERT INTO interactions (
                    question, answer, source, category, latency_seconds, feedback, created_at
                )
                VALUES (
                    :question, :answer, :source, :category, :latency_seconds, :feedback, :created_at
                )
                RETURNING id
            """),
            {
                "question": question,
                "answer": answer,
                "source": source,
                "category": category,
                "latency_seconds": latency_seconds,
                "feedback": None,
                "created_at": datetime.now()
            }
        )

        return result.scalar_one()
    
# Actualizar el feedback de una interacción
def update_feedback_pg(interaction_id, feedback):
    with engine.begin() as connection:
        connection.execute(
            text("""
                UPDATE interactions
                SET feedback = :feedback
                WHERE id = :interaction_id
            """),
            {
                "feedback": feedback,
                "interaction_id": interaction_id
            }
        )

# Obtener las interacciones recientes
def get_recent_interactions_pg(limit=10):
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT id, question, answer, source, category, latency_seconds, feedback, created_at
                FROM interactions
                ORDER BY id DESC
                LIMIT :limit
            """),
            {"limit": limit}
        )

        return result.fetchall()
    
def get_category_metrics_pg():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT category, COUNT(*) as total
                FROM interactions
                WHERE category IS NOT NULL
                GROUP BY category
                ORDER BY total DESC
            """)
        )

        return result.fetchall()
    
def get_metrics_pg():
    with engine.connect() as connection:

        total_interactions = connection.execute(
            text("SELECT COUNT(*) FROM interactions")
        ).scalar()

        avg_latency = connection.execute(
            text("SELECT AVG(latency_seconds) FROM interactions")
        ).scalar() or 0

        positive_feedback = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM interactions
                WHERE feedback = 'positive'
            """)
        ).scalar()

        negative_feedback = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM interactions
                WHERE feedback = 'negative'
            """)
        ).scalar()

        without_feedback = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM interactions
                WHERE feedback IS NULL
            """)
        ).scalar()

        return {
            "total_interactions": total_interactions,
            "avg_latency": round(avg_latency, 2),
            "positive_feedback": positive_feedback,
            "negative_feedback": negative_feedback,
            "without_feedback": without_feedback
        }