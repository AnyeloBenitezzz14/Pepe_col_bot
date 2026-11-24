"""Entrena (o reentrena) el modelo. Úsalo después de juntar feedback real."""
from mood_model import train

if __name__ == "__main__":
    train()
    print("Modelo guardado en models/mood_model.joblib")
