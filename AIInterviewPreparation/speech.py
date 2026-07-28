"""
speech.py
Wraps speech-to-text functionality for the Voice Interview feature.

Uses the `speech_recognition` library. Where possible it prefers an offline
recognizer (Sphinx via `pocketsphinx`) so the app can run without internet
access; if that engine isn't installed it gracefully falls back to the
library's Google Web Speech engine (requires internet), and if no
microphone/recognition backend is available at all, it fails safely with a
clear message instead of crashing the app.
"""

import threading

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False


class SpeechRecognizer:
    """Small helper class that records a short audio clip from the default
    microphone and converts it to text, running the blocking work on a
    background thread so the CustomTkinter UI never freezes."""

    def __init__(self):
        self.available = SR_AVAILABLE
        if self.available:
            self.recognizer = sr.Recognizer()

    def is_microphone_available(self) -> bool:
        if not self.available:
            return False
        try:
            with sr.Microphone() as _:
                return True
        except Exception:
            return False

    def listen_and_transcribe_async(self, on_result, on_error, timeout=8, phrase_time_limit=25):
        """Start listening in a background thread.
        on_result(text) is called with the transcribed text on success.
        on_error(message) is called with a human-readable error otherwise.
        """
        thread = threading.Thread(
            target=self._listen_worker,
            args=(on_result, on_error, timeout, phrase_time_limit),
            daemon=True,
        )
        thread.start()

    def _listen_worker(self, on_result, on_error, timeout, phrase_time_limit):
        if not self.available:
            on_error("Speech recognition library is not installed.\n"
                      "Install it with: pip install SpeechRecognition pocketsphinx pyaudio")
            return
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )
        except Exception as e:
            on_error(f"Could not access microphone: {e}")
            return

        # Try offline recognition first (Sphinx), then fall back to Google.
        text = None
        last_error = None
        try:
            text = self.recognizer.recognize_sphinx(audio)
        except Exception as e:
            last_error = e

        if text is None:
            try:
                text = self.recognizer.recognize_google(audio)
            except Exception as e:
                last_error = e

        if text:
            on_result(text)
        else:
            on_error(f"Could not understand audio. ({last_error})")
