import os
import argparse
import subprocess
import time

from pydub import AudioSegment
from pydub.utils import make_chunks
from google.cloud import speech
from tqdm import tqdm


CHUNK_LENGTH_SEC = 60


def convert_to_flac(source_path: str) -> str:
    """Convert MP3 file to FLAC using ffmpeg if needed."""
    if source_path.lower().endswith('.flac'):
        return source_path

    flac_path = os.path.splitext(source_path)[0] + '.flac'
    command = [
        'ffmpeg', '-y', '-i', source_path,
        '-ac', '1', '-ar', '16000', flac_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return flac_path


def transcribe_chunk(client: speech.SpeechClient, chunk_path: str, sample_rate: int, language: str) -> str:
    """Send a single audio chunk to Google Speech-to-Text."""
    with open(chunk_path, 'rb') as f:
        audio_content = f.read()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=sample_rate,
        language_code=language,
    )

    for attempt in range(3):
        try:
            response = client.recognize(config=config, audio=audio)
            break
        except Exception as exc:  # pylint: disable=broad-except
            if attempt == 2:
                raise
            print(f'Retrying due to error: {exc}')
            time.sleep(2)
    else:
        return ''

    texts = [result.alternatives[0].transcript for result in response.results]
    return ' '.join(texts)


def transcribe_long_audio(path: str, output_path: str, language: str) -> None:
    client = speech.SpeechClient()

    processed_path = convert_to_flac(path)
    audio = AudioSegment.from_file(processed_path, format='flac')
    audio = audio.set_frame_rate(16000).set_channels(1)
    chunks = make_chunks(audio, CHUNK_LENGTH_SEC * 1000)

    with open(output_path, 'w', encoding='utf-8') as out_file:
        total = len(chunks)
        for idx, chunk in enumerate(tqdm(chunks, desc='Chunks'), start=1):
            chunk_path = f'temp_{idx}.flac'
            chunk.export(chunk_path, format='flac')

            try:
                text = transcribe_chunk(client, chunk_path, 16000, language)
                out_file.write(text + '\n')
            except Exception as err:  # pylint: disable=broad-except
                print(f'Error processing chunk {idx}: {err}')
                out_file.write('\n')
            finally:
                os.remove(chunk_path)

            print(f'Processed {idx} of {total} fragments')

    if processed_path != path:
        os.remove(processed_path)


def main() -> None:
    parser = argparse.ArgumentParser(description='Transcribe audio with Google Speech-to-Text')
    parser.add_argument('input', help='Path to input MP3 or FLAC file')
    parser.add_argument('-o', '--output', default='transcript.txt', help='Output text file')
    parser.add_argument('-l', '--language', default='ru-RU', help='Language code (default ru-RU)')

    args = parser.parse_args()
    transcribe_long_audio(args.input, args.output, args.language)


if __name__ == '__main__':
    main()
