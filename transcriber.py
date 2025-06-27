import argparse
import json
import os
import wave

from vosk import Model, KaldiRecognizer


def transcribe(audio_path: str, model_path: str) -> str:
    """Transcribe a WAV file using a Vosk model."""
    if not os.path.isdir(model_path):
        raise FileNotFoundError(f"Vosk model not found: {model_path}")

    with wave.open(audio_path, "rb") as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            raise ValueError("Audio must be WAV format mono PCM")

        sample_rate = wf.getframerate()
        model = Model(model_path)
        recognizer = KaldiRecognizer(model, sample_rate)
        recognizer.SetWords(True)

        results = []
        while True:
            data = wf.readframes(8000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                results.append(result.get("text", ""))

        final_result = json.loads(recognizer.FinalResult())
        results.append(final_result.get("text", ""))

    return " ".join(results)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transcribe Russian speech from a WAV file using an offline Vosk model."
    )
    parser.add_argument(
        "audio", help="Path to WAV file (mono PCM, 16 kHz recommended)."
    )
    parser.add_argument(
        "model",
        nargs="?",
        default="model",
        help="Path to Vosk model directory (default: ./model)"
    )
    parser.add_argument(
        "-o", "--output", help="Optional output text file to save transcription."
    )
    args = parser.parse_args()

    text = transcribe(args.audio, args.model)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
