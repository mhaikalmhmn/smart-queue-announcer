import os
import subprocess
import tempfile
from pathlib import Path

from pydub import AudioSegment


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

BELL_FILE = BASE_DIR / "sounds" / "bell.wav"

VOICE_MODEL = (
    BASE_DIR
    / "voice"
    / "models"
    / "en_US-lessac-high.onnx"
)

OUTPUT_FILE = BASE_DIR / "voice_test_output.wav"


# ============================================================
# SETTINGS
# ============================================================

CHARACTER_DELAY = 0.30
PHRASE_DELAY = 0.80

QUEUE = "A202"

FINAL_PHRASE = "Please pick up your order."


# ============================================================
# PRONUNCIATION
# ============================================================

LETTER_NAMES = {
    "A": "ay",
    "B": "bee",
    "C": "see",
    "D": "dee",
    "E": "ee",
    "F": "eff",
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
    "Z": "zee",
}

NUMBER_NAMES = {
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


def pronounce_character(character):
    character = character.upper()

    if character in LETTER_NAMES:
        return LETTER_NAMES[character]

    if character in NUMBER_NAMES:
        return NUMBER_NAMES[character]

    return character


# ============================================================
# CREATE SPEECH
# ============================================================

def create_speech(text, output_file):

    command = [
        "python",
        "-m",
        "piper",
        "--model",
        str(VOICE_MODEL),
        "--output_file",
        str(output_file),
    ]

    subprocess.run(
        command,
        input=text,
        text=True,
        check=True,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("Smart Queue Announcer - Voice Test")
    print("-----------------------------------")

    if not BELL_FILE.exists():
        raise FileNotFoundError(
            f"Bell not found:\n{BELL_FILE}"
        )

    if not VOICE_MODEL.exists():
        raise FileNotFoundError(
            f"Voice model not found:\n{VOICE_MODEL}"
        )

    print(f"Queue: {QUEUE}")
    print("Creating queue announcement...")

    parts = []

    # --------------------------------------------------------
    # Bell
    # --------------------------------------------------------

    bell = AudioSegment.from_wav(
        BELL_FILE
    )

    parts.append(
        bell
    )

    # Short pause after bell
    parts.append(
        AudioSegment.silent(
            duration=500
        )
    )

    # --------------------------------------------------------
    # Queue characters
    # --------------------------------------------------------

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_dir = Path(temp_dir)

        for index, character in enumerate(QUEUE):

            spoken = pronounce_character(
                character
            )

            print(
                f"Character {index + 1}: "
                f"{character} -> {spoken}"
            )

            character_file = (
                temp_dir
                / f"character_{index}.wav"
            )

            create_speech(
                spoken,
                character_file
            )

            character_audio = (
                AudioSegment.from_wav(
                    character_file
                )
            )

            parts.append(
                character_audio
            )

            # Pause between characters
            if index < len(QUEUE) - 1:

                parts.append(
                    AudioSegment.silent(
                        duration=int(
                            CHARACTER_DELAY * 1000
                        )
                    )
                )

        # ----------------------------------------------------
        # Pause before final phrase
        # ----------------------------------------------------

        parts.append(
            AudioSegment.silent(
                duration=int(
                    PHRASE_DELAY * 1000
                )
            )
        )

        # ----------------------------------------------------
        # Final phrase
        # ----------------------------------------------------

        phrase_file = (
            temp_dir
            / "final_phrase.wav"
        )

        create_speech(
            FINAL_PHRASE,
            phrase_file
        )

        phrase_audio = (
            AudioSegment.from_wav(
                phrase_file
            )
        )

        parts.append(
            phrase_audio
        )

    # --------------------------------------------------------
    # Combine everything
    # --------------------------------------------------------

    announcement = parts[0]

    for part in parts[1:]:

        announcement += part

    announcement.export(
        OUTPUT_FILE,
        format="wav"
    )

    print()
    print("===================================")
    print("Voice test created successfully!")
    print()
    print(f"Output:")
    print(OUTPUT_FILE)
    print("===================================")


if __name__ == "__main__":
    main()
