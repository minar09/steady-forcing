import random

# Static anchors: immovable background elements
static_elements = [
    "heavy stone bridge", "solid concrete canal walls", "motionless riverbank",
    "immovable rocky hillside", "still forest floor", "solid gray rocks",
    "unchanging sandy shoreline", "motionless driftwood", "concrete embankment",
    "static wooden pier", "solid brick wall", "motionless grassy bank",
    "immovable cliffs", "still tree trunks", "solid paved street"
]

# Dynamic flows: continuous natural motion
dynamic_elements = [
    "crystal-clear water flowing gently", "rippling surface shimmering with light",
    "floodwater rising slowly and smoothly", "waves crashing rhythmically against rocks",
    "smoke rising steadily into the sky", "flames flickering naturally without distortion",
    "branches thrashing violently in the storm", "petals drifting softly with the wind",
    "tides rolling in seamless rhythm", "stream currents weaving around pebbles",
    "snow falling continuously in soft cascades", "mist drifting upward in steady motion",
    "rain falling endlessly, forming puddles", "marine foam swirling naturally",
    "wind pushing grass in rhythmic waves"
]

# Atmosphere descriptors
atmospheres = [
    "overcast daylight with muted tones", "bright sunny spring day with golden light",
    "stormy gray skies with heavy clouds", "nighttime illuminated by faint moonlight",
    "sunset casting warm orange reflections", "autumn afternoon with soft golden hues",
    "misty dawn with pale blue tones", "clear summer day with vivid colors",
    "winter twilight with silver reflections", "humid monsoon evening with dim light"
]

# Locations / contexts
locations = [
    "rural South Korean hillside", "urban neighborhood park", "coastal fishing village",
    "mountain stream in a forest", "empty sea beach", "city canal under a bridge",
    "remote valley river", "stormy coastal cliffs", "quiet rural street food stall",
    "urban underpass flooded with water"
]

# Camera constraint (always static)
camera_constraint = (
    "recorded by a completely fixed, static, tripod mounted camera. "
    "The camera is not seen, it does not move, tilt, pan, or zoom at any point."
)

def generate_prompt():
    static = random.choice(static_elements)
    dynamic = random.choice(dynamic_elements)
    atmosphere = random.choice(atmospheres)
    location = random.choice(locations)
    
    prompt = (
        f"A {location} scene {camera_constraint} "
        f"The {static} remains perfectly still, while {dynamic}. "
        f"The atmosphere is {atmosphere}. "
        f"The scene unfolds in real time, emphasizing the physical dynamics of nature flow. "
        f"The video maintains temporal continuity across all frames, showing uninterrupted progression without cinematic exaggeration."
    )
    return prompt

# Generate a batch of prompts
num_prompts = 10000   # adjust to 10,000–40,000 for full dataset
prompts = [generate_prompt() for _ in range(num_prompts)]

# Save to file
with open("static_nature_prompts_train.txt", "w", encoding="utf-8") as f:
    for p in prompts:
        f.write(p + "\n")

print(f"Generated {num_prompts} prompts and saved to static_nature_prompts_train.txt")
