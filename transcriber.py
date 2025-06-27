import argparse
import json
import os
import wave

from vosk import Model, KaldiRecognizer


def transcribe(audio_path: str, model_path: str) -> str:
    """Transcribe a WAV file using a Vosk model and show progress."""
    if not os.path.isdir(model_path):
        raise FileNotFoundError(f"Vosk model not found: {model_path}")

    with wave.open(audio_path, "rb") as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            raise ValueError("Audio must be WAV format mono PCM")

        sample_rate = wf.getframerate()
        total_frames = wf.getnframes()
        model = Model(model_path)
        recognizer = KaldiRecognizer(model, sample_rate)
        recognizer.SetWords(True)

        results = []
        processed_frames = 0
        while True:
            data = wf.readframes(8000)
            if len(data) == 0:
                break
            processed_frames += len(data) // (wf.getsampwidth() * wf.getnchannels())
            percent = processed_frames / total_frames * 100
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text_chunk = result.get("text", "")
                if text_chunk:
                    print(f"[{percent:6.2f}%] {text_chunk}")
                else:
                    print(f"[{percent:6.2f}%]")
                results.append(text_chunk)
            else:
                print(f"[{percent:6.2f}%]", end="\r", flush=True)

        final_result = json.loads(recognizer.FinalResult())
        final_text = final_result.get("text", "")
        print("[100.00%]", final_text)
        results.append(final_text)

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
