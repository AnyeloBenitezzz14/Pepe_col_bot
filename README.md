# 🎧 Bot de Telegram: música según tu estado de ánimo

Hace un test de 6 preguntas con botones, un modelo de **machine learning** detecta
tu mood y un **recomendador KNN** te sugiere canciones para ese momento.

## Cómo funciona

```
Test (6 preguntas) ──► LogisticRegression ──► mood + probabilidades
                                                   │
                                                   ▼
                       perfil de audio del mood ──► KNN sobre data/songs.csv ──► 5 canciones
                       (valence, energy, danceability, acousticness)
```

- **Moods:** feliz, enérgico, tranquilo, melancólico, estresado, romántico.
- **Clasificador (`mood_model.py`):** regresión logística de scikit-learn sobre las respuestas (one-hot).
- **Recomendador (`recommender.py`):** K-Nearest Neighbors entre el perfil del mood y las características de cada canción. Se muestrea entre los vecinos más cercanos para que "Más canciones" no repita.
- **Estresado** recibe música calmante para bajar revoluciones. **Melancólico** recibe música que lo acompaña y puede pulsar "Quiero animarme".
- **Feedback:** al final el bot pregunta si acertó. Esas respuestas se guardan en `data/feedback.csv` (sin ID de usuario) y sirven para reentrenar.

## Instalación

```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
```

1. Crea el bot con [@BotFather](https://t.me/BotFather) (`/newbot`) y copia el token.
2. Copia `.env.example` a `.env` y pega tu token (el archivo `.env` está en `.gitignore`).
3. Ejecuta:

```bash
python train_model.py   # opcional: el bot lo entrena solo si no existe el modelo
python bot.py
```

Comandos: `/start`, `/test`.

## Reentrenar con datos reales

Cuando tengas respuestas en `data/feedback.csv`, ejecuta de nuevo `python train_model.py`.
Las respuestas reales pesan 5× más que las sintéticas.

## ⚠️ Limitaciones honestas

- El modelo se entrenó con **datos sintéticos** generados a partir de las afinidades definidas en `quiz.py`. El ~79 % de accuracy mide qué tan bien aprende esas reglas, no qué tan bien acierta con personas reales. Mejorará con el feedback.
- Las características de audio de `data/songs.csv` son **estimaciones aproximadas**. Para algo más serio usa un dataset real (por ejemplo, datasets de Spotify en Kaggle). La API de audio-features de Spotify tiene acceso restringido para apps nuevas.
- Los enlaces son búsquedas en YouTube/Spotify: el bot no necesita API de música.

## Ideas para mejorar

- Preguntar género o idioma favorito y filtrar el catálogo.
- Guardar el historial por usuario para personalizar (con consentimiento).
- Ampliar `songs.csv` a miles de canciones.
- Detectar el mood también por texto libre (puedes reutilizar `pysentimiento` de tu proyecto anterior).
- Desplegar en Railway/Render/Fly.io con un `Dockerfile`.

## 🔐 Seguridad

Nunca subas el token a GitHub. Si se filtra: @BotFather → `/revoke`.
