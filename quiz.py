"""Definición del test y de los estados de ánimo.

Cada opción de respuesta lleva un vector de 'afinidad' con los 6 moods
(en el orden de MOODS). Esos pesos se usan para generar datos de
entrenamiento sintéticos; el modelo de ML aprende a partir de ellos
(y luego de las respuestas reales que dejen los usuarios).
"""

MOODS = ["feliz", "energico", "tranquilo", "melancolico", "estresado", "romantico"]

MOOD_INFO = {
    "feliz":        ("😄", "Feliz",        "Te sientes con buena vibra y ganas de disfrutar."),
    "energico":     ("⚡", "Enérgico",     "Traes energía de sobra: toca moverse."),
    "tranquilo":    ("😌", "Tranquilo",    "Estás en calma y con la mente despejada."),
    "melancolico":  ("🌧️", "Melancólico",  "Hay nostalgia o tristeza, y está bien sentirla."),
    "estresado":    ("😮‍💨", "Estresado",    "Hay tensión y mucho en la cabeza: música para bajar revoluciones."),
    "romantico":    ("💘", "Romántico",    "Tu corazón anda sensible y con alguien en mente."),
}

#                feliz energ tranq melan estre roman
QUESTIONS = [
    {
        "text": "¿Cómo está tu nivel de energía ahora mismo?",
        "options": [
            ("🪫 Por el piso",        [-1.0, -2.0,  1.0,  1.5,  0.5,  0.0]),
            ("🐢 Bajito, pero ahí voy", [ 0.0, -1.0,  1.0,  1.0,  0.5,  0.5]),
            ("🙂 Normal",             [ 0.5,  0.0,  1.0,  0.0,  0.0,  0.5]),
            ("⚡ A tope",             [ 1.0,  2.0, -1.0, -1.0,  0.5,  0.5]),
        ],
    },
    {
        "text": "¿Cómo ha sido tu día hasta ahora?",
        "options": [
            ("🌫️ Pesado y gris",      [-2.0, -1.0,  0.0,  2.0,  2.0,  0.0]),
            ("🍃 Tranquilo",          [ 0.0, -1.0,  2.0,  0.0,  0.0,  1.0]),
            ("👍 Bastante bueno",     [ 1.5,  1.0,  1.0, -1.0, -1.0,  1.0]),
            ("🌟 Increíble",          [ 2.0,  1.5,  0.0, -2.0, -2.0,  1.0]),
        ],
    },
    {
        "text": "¿Con quién te gustaría estar ahora?",
        "options": [
            ("🧍 Solo/a",             [-1.0, -1.0,  1.5,  1.5,  1.0,  0.0]),
            ("👤 Con una persona especial", [ 0.0, -1.0,  1.0,  0.5,  0.0,  2.0]),
            ("👯 Con mis amigos",     [ 1.5,  1.0,  0.0, -0.5, -0.5,  0.5]),
            ("🎉 En una fiesta",      [ 1.5,  2.5, -1.0, -1.5, -1.0,  0.0]),
        ],
    },
    {
        "text": "¿Qué tienes más en la cabeza?",
        "options": [
            ("📋 Pendientes y preocupaciones", [-1.0,  0.0, -1.0,  0.5,  3.0, -1.0]),
            ("🕰️ Nostalgia / alguien que extraño", [-1.0, -1.0,  0.0,  3.0,  0.0,  1.5]),
            ("☁️ Nada, mente en blanco", [ 0.0,  0.0,  3.0,  0.0, -1.0,  0.0]),
            ("🚀 Planes y metas",     [ 1.5,  2.0,  0.0, -1.0,  0.0,  0.0]),
            ("💭 Alguien que me gusta", [ 1.0,  0.0,  0.0,  0.0,  0.0,  3.0]),
        ],
    },
    {
        "text": "¿Cómo se siente tu cuerpo?",
        "options": [
            ("😖 Tenso",              [-1.0,  0.0, -1.0,  0.0,  3.0,  0.0]),
            ("😴 Cansado",            [-1.0, -2.0,  1.5,  2.0,  0.5,  0.0]),
            ("🧘 Relajado",           [ 1.0, -1.0,  3.0,  0.0, -2.0,  1.0]),
            ("🏃 Con ganas de moverme", [ 1.0,  3.0, -2.0, -1.0,  0.0,  0.0]),
        ],
    },
    {
        "text": "¿Qué quieres que haga la música por ti?",
        "options": [
            ("🫂 Que me acompañe en lo que siento", [-1.0, -1.0,  0.0,  3.0,  0.0,  1.0]),
            ("🌊 Que me calme",       [ 0.0, -2.0,  3.0,  0.0,  2.0,  1.0]),
            ("☀️ Que me suba el ánimo", [ 2.0,  1.0,  0.0, -1.0,  1.0,  1.0]),
            ("💃 Que me haga bailar", [ 1.0,  3.0, -1.0, -2.0,  0.0,  0.5]),
        ],
    },
]


ACTIVITIES = [
    ("Solo escuchar música", None),
    ("Estudiar o trabajar", [0.55, 0.28, 0.40, 0.75]),
    ("Hacer ejercicio", [0.65, 0.95, 0.78, 0.08]),
    ("Bailar", [0.75, 0.85, 0.94, 0.12]),
    ("Viajar o desplazarme", [0.65, 0.62, 0.62, 0.30]),
    ("Relajarme o descansar", [0.50, 0.18, 0.32, 0.85]),
]

GENRES = [
    ("Ninguno en particular", None),
    ("Reguetón", "reggaeton"),
    ("Trap", "trap"),
    ("Pop", "pop"),
    ("Hip hop", "hip_hop"),
    ("Rock", "rock"),
    ("Salsa", "salsa"),
    ("Baladas", "balada"),
    ("Bachata", "bachata"),
    ("Cumbia", "cumbia"),
    ("R&B", "rnb"),
]

RECOMMENDATION_QUESTIONS = [
    {"text": "¿Qué vas a hacer mientras escuchas música?", "options": ACTIVITIES},
    {"text": "¿Qué género musical no te gusta?", "options": GENRES},
]
