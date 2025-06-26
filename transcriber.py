import argparse
import json
import wave

from vosk import Model, KaldiRecognizer


def transcribe(audio_path: str, model_path: str, sample_rate: int = 16000) -> str:
    """Transcribe a WAV file using a Vosk model."""
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, sample_rate)
    recognizer.SetWords(True)

    results = []

    with wave.open(audio_path, "rb") as wf:
        if (
            wf.getnchannels() != 1
            or wf.getsampwidth() != 2
            or wf.getframerate() != sample_rate
        ):
            raise ValueError(
                "Audio file must be WAV format mono PCM with sample rate %d" % sample_rate
            )

        while True:
            data = wf.readframes(4000)
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
        description="Transcribe a WAV audio file using an offline Vosk model."
    )
    parser.add_argument(
        "audio", help="Path to WAV file (mono PCM, 16 kHz recommended)."
    )
    parser.add_argument("model", help="Path to directory with Vosk model.")
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
