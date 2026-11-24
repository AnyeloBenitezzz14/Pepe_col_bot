"""Modelo de ML que clasifica el estado de ánimo a partir del test.

- Codificación one-hot de las respuestas.
- Regresión logística multinomial (scikit-learn) -> devuelve probabilidades.
- Entrenamiento con datos sintéticos + (opcional) feedback real de usuarios
  guardado en data/feedback.csv.
"""
import csv
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

from quiz import MOODS, QUESTIONS

BASE = Path(__file__).parent
MODEL_PATH = BASE / "models" / "mood_model.joblib"
FEEDBACK_PATH = BASE / "data" / "feedback.csv"

N_OPTS = [len(q["options"]) for q in QUESTIONS]
OFFSETS = np.cumsum([0] + N_OPTS)[:-1]
N_FEATURES = int(sum(N_OPTS))


def encode(answers):
    x = np.zeros(N_FEATURES)
    for qi, ai in enumerate(answers):
        x[OFFSETS[qi] + ai] = 1.0
    return x


def generate_synthetic(n_per_mood=600, sharpness=0.9, noise=0.10, seed=42):
    """Simula personas de cada mood: cada una responde según las afinidades."""
    rng = np.random.default_rng(seed)
    X, y = [], []
    for mi, mood in enumerate(MOODS):
        for _ in range(n_per_mood):
            answers = []
            for q in QUESTIONS:
                w = np.array([opt[1][mi] for opt in q["options"]])
                if rng.random() < noise:          # respuesta "rara"
                    a = rng.integers(len(w))
                else:
                    p = np.exp(sharpness * w)
                    p /= p.sum()
                    a = rng.choice(len(w), p=p)
                answers.append(int(a))
            X.append(encode(answers))
            y.append(mood)
    return np.array(X), np.array(y)


def load_feedback():
    """Lee las respuestas reales (con el mood que confirmó el usuario)."""
    if not FEEDBACK_PATH.exists():
        return np.empty((0, N_FEATURES)), np.empty((0,), dtype=str)
    X, y = [], []
    with open(FEEDBACK_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                answers = [int(row[f"q{i+1}"]) for i in range(len(QUESTIONS))]
                if row["true_mood"] in MOODS:
                    X.append(encode(answers))
                    y.append(row["true_mood"])
            except (KeyError, ValueError, IndexError):
                continue
    return np.array(X).reshape(-1, N_FEATURES), np.array(y)


def save_feedback(answers, true_mood):
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    new = not FEEDBACK_PATH.exists()
    with open(FEEDBACK_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp"] + [f"q{i+1}" for i in range(len(QUESTIONS))] + ["true_mood"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), *answers, true_mood])


def train(real_weight=5.0, verbose=True):
    X, y = generate_synthetic()
    w = np.ones(len(y))
    Xr, yr = load_feedback()
    if len(yr):
        X = np.vstack([X, Xr])
        y = np.concatenate([y, yr])
        w = np.concatenate([w, np.full(len(yr), real_weight)])
    model = LogisticRegression(max_iter=2000, C=1.0)
    cv = cross_val_score(model, X, y, cv=5).mean()
    model.fit(X, y, sample_weight=w)
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    if verbose:
        print(f"Muestras sintéticas: {len(y) - len(yr)} | reales: {len(yr)}")
        print(f"Accuracy (validación cruzada 5-fold): {cv:.1%}")
    return model


_model = None


def get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else train(verbose=False)
    return _model


def predict(answers):
    """Devuelve [(mood, prob), ...] ordenado de mayor a menor."""
    m = get_model()
    probs = m.predict_proba(encode(answers).reshape(1, -1))[0]
    return sorted(zip(map(str, m.classes_), map(float, probs)), key=lambda t: -t[1])
