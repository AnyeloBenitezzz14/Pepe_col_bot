"""Recomendador basado en contenido (KNN sobre características de audio).

El perfil del mood se combina con el de la actividad cuando corresponde.
Se filtran los géneros excluidos y se muestrean las canciones cercanas
con mayor probabilidad para las que mejor encajan.
"""
from pathlib import Path

import numpy as np
import pandas as pd

FEATURES = ["valence", "energy", "danceability", "acousticness"]

PROTOTYPES = {
    "feliz":       [0.85, 0.75, 0.80, 0.20],
    "energico":    [0.65, 0.92, 0.80, 0.08],
    "tranquilo":   [0.60, 0.30, 0.55, 0.70],
    "melancolico": [0.20, 0.30, 0.40, 0.80],
    "estresado":   [0.30, 0.12, 0.25, 0.92],   # música para bajar revoluciones
    "romantico":   [0.55, 0.50, 0.60, 0.45],
}

SONGS = pd.read_csv(Path(__file__).parent / "data" / "songs.csv")
_AUDIO = SONGS[FEATURES].to_numpy()
_GENRES = SONGS["genres"].fillna("").str.split("|", regex=False)
_RNG = np.random.default_rng()


def recommend(mood, n=5, exclude=None, *, activity=None, excluded_genre=None):
    target = np.array(PROTOTYPES[mood])
    if activity is not None:
        target = 0.55 * target + 0.45 * np.asarray(activity)

    distances = np.linalg.norm(_AUDIO - target, axis=1)
    eligible = [
        i for i in np.argsort(distances)
        if excluded_genre not in _GENRES.iat[i]
    ]
    shown = set(exclude or [])
    unseen = [i for i in eligible if i not in shown]
    pool = unseen if len(unseen) >= n else eligible
    ids = np.array(pool[:max(18, n)], dtype=int)
    if not len(ids):
        return []

    closeness = 1.0 / (distances[ids] + 0.05)
    picks = _RNG.choice(ids, size=min(n, len(ids)), replace=False, p=closeness / closeness.sum())
    return [
        {"idx": int(i), "title": SONGS.at[i, "title"], "artist": SONGS.at[i, "artist"]}
        for i in picks
    ]
