# perceptron999
Проект для транскриптора на Python с VOSK.

## Google Speech-to-Text

В репозиторий добавлен скрипт `google_transcriber.py` для транскрибирования длинных аудиофайлов при помощи Google Cloud Speech-to-Text.

### Требования
- Python 3.8+
- `ffmpeg` должен быть установлен и доступен в `PATH`.
- Установите зависимости:
  ```bash
  pip install google-cloud-speech pydub ffmpeg-python tqdm
  ```

### Настройка Google Cloud
1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/).
2. Включите API **Speech-to-Text**.
3. Создайте *service account* и скачайте JSON‑ключ.
4. Установите переменную окружения `GOOGLE_APPLICATION_CREDENTIALS` с путём до этого файла.
   Пример для Windows:
   ```cmd
   set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\key.json
   ```

### Запуск скрипта
Скрипт разбивает аудио на фрагменты по 60 секунд, отправляет каждый из них в Google Speech-to-Text и сохраняет результат в текстовый файл:
```bash
python google_transcriber.py input.mp3 -o result.txt
```
В консоль выводится прогресс вида `Processed 12 of 100 fragments`.
