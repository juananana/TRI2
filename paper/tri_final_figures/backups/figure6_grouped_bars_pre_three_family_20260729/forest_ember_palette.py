"""Shared Forest Ember palette for TRI paper figures."""

INK = "#264A56"
MUTED = "#5F6B70"
GRID = "#D6E0DE"
TEAL = "#407A7F"
TEAL_LIGHT = "#D9E7E7"
EMBER = "#E56D4E"
EMBER_LIGHT = "#F8DDD5"
LEAF = "#60AA84"
LEAF_LIGHT = "#DDECE4"
PLUM = "#8B6F8E"
PLUM_LIGHT = "#E8DEE9"
NEUTRAL = "#D8D4CF"
NEUTRAL_EDGE = "#A7A099"
PAPER = "#FFFFFF"

# Stable model identity across all result figures. Semantic diagrams may use
# the same palette by meaning, but model-facing result plots must keep this map.
MODEL_COLORS = {
    "Qwen": PLUM,
    "Qwen3.5": PLUM,
    "GLM": EMBER,
    "GLM-5.1": EMBER,
    "DeepSeek": TEAL,
    "MiniMax": LEAF,
}
