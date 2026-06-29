EXERCISE_CATALOG = [
    {
        "key": "finger_tap",
        "title_en": "Finger Tapping Exercise",
        "title_si": "ඇඟිලි තට්ටු ව්‍යායාම",
        "instructions_en": (
            "Place your hand flat on a table. Tap each finger to your thumb one at a time, "
            "starting with the index finger. Repeat 10 times per hand, twice daily."
        ),
        "instructions_si": (
            "ඔබේ අත මේසය මත තබාගන්න. දකුණු ඇඟිලි සිට එක් එක් ඇඟිල්ල "
            "බෙරය වෙත තට්ටු කරන්න. එක් අතකට 10 වතාවක්, දිනකට දෙවරක්."
        ),
    },
    {
        "key": "squeeze_ball",
        "title_en": "Squeeze Ball Exercise",
        "title_si": "බෝලය තද කිරීමේ ව්‍යායාම",
        "instructions_en": (
            "Hold a soft ball in your hand. Squeeze firmly for 3 seconds, then release. "
            "Repeat 15 times per hand, once daily."
        ),
        "instructions_si": (
            "ඔබේ අතේ මෘදු බෝලයක් අල්ලාගන්න. තත්පර 3ක් තද කර නිදහස් කරන්න. "
            "එක් අතකට 15 වතාවක්, දිනකට එක් වරක්."
        ),
    },
    {
        "key": "target_touch",
        "title_en": "Target Touch Exercise",
        "title_si": "ඉලක්ක තට්ටු ව්‍යායාම",
        "instructions_en": (
            "Place 5 small objects on a table. Touch each object with your index finger "
            "alternating between left and right hands. Complete 3 rounds daily."
        ),
        "instructions_si": (
            "මේසය මත කුඩා වස්තු 5ක් තබන්න. යටි ඇඟිල්ලෙන් "
            "වම් සහ දකුණු අත් අතර තට්ටු කරන්න. දිනකට 3 වට."
        ),
    },
]


def get_recommended_exercises(risk_profile, asymmetry_side=None):
    if risk_profile in ("baseline",):
        return EXERCISE_CATALOG[:1]

    if risk_profile == "monitor":
        return EXERCISE_CATALOG[:2]

    return EXERCISE_CATALOG
