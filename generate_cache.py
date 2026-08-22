import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

PIPER_PYTHON = Path(
    r"C:\Users\User\piper-test\Scripts\python.exe"
)

PIPER_MODEL = Path(
    r"C:\Users\User\OneDrive - Foodle Sdn Bhd\Backup\piper-voice\en_US-lessac-high.onnx"
)

CACHE_DIR = BASE_DIR / "voice_cache"

CACHE_DIR.mkdir(
    exist_ok=True
)

PRONUNCIATION = {
    "A": "a",
    "B": "bee",
    "C": "sea",
    "D": "dee",
    "E": "ee",
    "F": "F",
    "G": "gee",
    "H": "aitch",
    "I": "eye",
    "J": "jay",
    "K": "kay",
    "L": "el",
    "M": "em",
    "N": "en",
    "O": "oh",
    "P": "pee",
    "Q": "cue",
    "R": "ar",
    "S": "ess",
    "T": "tee",
    "U": "you",
    "V": "vee",
    "W": "double you",
    "X": "ex",
    "Y": "why",
    "Z": "zed",

    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
}

FINAL_PHRASE = "Please pick up your order."


def generate(text, filename):

    output_file = CACHE_DIR / filename

    print(f"Generating {filename}: {text}")

    command = [
        str(PIPER_PYTHON),
        "-m",
        "piper",
        "--model",
        str(PIPER_MODEL),
        "--output_file",
        str(output_file),
    ]

    subprocess.run(
        command,
        input=text,
        text=True,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


for character, pronunciation in PRONUNCIATION.items():

    filename = f"{character}.wav"

    generate(
        pronunciation,
        filename
    )


generate(
    FINAL_PHRASE,
    "final_phrase.wav"
)

print()
print("======================================")
print("VOICE CACHE COMPLETE")
print("======================================")
print()
print(f"Files saved to:")
print(CACHE_DIR)
