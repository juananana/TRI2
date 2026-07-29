"""Shared three-family visual system for all TRI paper figures."""

# Neutral structure does not count toward the three chromatic families.
INK = "#264A56"
MUTED = "#5F6B70"
GRID = "#D6E0DE"
NEUTRAL = "#D8D4CF"
NEUTRAL_EDGE = "#A7A099"
PAPER = "#FFFFFF"

# The only three chromatic families used in the paper.
LAVENDER = "#9A82BA"
LAVENDER_DARK = "#73558F"
LAVENDER_LIGHT = "#E9E1EF"
LAVENDER_WASH = "#F7F4F9"

CORAL = "#E96F75"
CORAL_DARK = "#C74D59"
CORAL_LIGHT = "#FBE0DF"
CORAL_WASH = "#FFF7F6"

TEAL = "#407A7F"
TEAL_DARK = "#2F6468"
TEAL_LIGHT = "#D9E7E7"
TEAL_WASH = "#F2F8F8"
TEAL_ALT = "#72A9AC"  # Same family; MiniMax only.

# Backward-compatible names. They deliberately resolve to the three families.
PLUM = LAVENDER
PLUM_LIGHT = LAVENDER_LIGHT
EMBER = CORAL
EMBER_LIGHT = CORAL_LIGHT
LEAF = TEAL_ALT
LEAF_LIGHT = TEAL_LIGHT

# Stable identity across model-facing result plots.
MODEL_COLORS = {
    "Qwen": LAVENDER,
    "Qwen3.5": LAVENDER,
    "GLM": CORAL,
    "GLM-5.1": CORAL,
    "DeepSeek": TEAL,
    "MiniMax": TEAL_ALT,
}
MODEL_MARKERS = {
    "Qwen": "o",
    "Qwen3.5": "o",
    "GLM": "s",
    "GLM-5.1": "s",
    "DeepSeek": "D",
    "MiniMax": "^",
}

# Cross-figure state vocabulary.
HATCH_PRESERVE = "/"
HATCH_REEVALUATE = "\\"
HATCH_NONE = ""
