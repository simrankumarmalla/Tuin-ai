"""
voice.py - Ears & Voice Engine for Tuin AI Assistant

Voice Pipeline:
1. Primary Cloned Voice: Uses Fish Audio SDK (`from fishaudio import FishAudio, save`)
   with model='s2.1-pro' and your custom cloned Voice ID.
2. Automatic Fallback Voice: Seamlessly falls back to Edge-TTS (`en-IN-NeerjaNeural`
   with tuned ~292Hz acoustic profile) if Fish Audio credentials are unset or error out.
3. Speech-to-Text (`listen()`): SpeechRecognition with microphone input, ambient noise
   calibration, and crash-proof error handling.
4. Wake Word (`listen_for_wake_word()`): Listens for 'tuin' and phonetic matches ('twin',
   'to in', 'tuwin', 'hey tuin') with one-shot command extraction.
"""

import asyncio
import os
import re
import tempfile
import time
import winsound
from typing import List, Optional, Tuple

from dotenv import load_dotenv
import edge_tts
from fishaudio import FishAudio
from fishaudio.utils import save
import pygame
import speech_recognition as sr

# Load environment variables
load_dotenv()

# Fish Audio Credentials (support both FISH_API_KEY and FISH_AUDIO_API_KEY)
FISH_API_KEY = (os.getenv("FISH_API_KEY") or os.getenv("FISH_AUDIO_API_KEY", "")).strip()
FISH_VOICE_ID = (os.getenv("FISH_VOICE_ID") or os.getenv("FISH_AUDIO_VOICE_ID", "")).strip()

# Fallback Edge-TTS Settings
TTS_FALLBACK_VOICE = "en-IN-NeerjaNeural"
VOICE_PITCH = "+12Hz"  # Calibrated to ~292Hz
VOICE_RATE = "-2%"

# Initialize pygame mixer once
try:
    pygame.mixer.init()
except Exception as _e:
    print(f"[Warning] Could not initialize pygame mixer: {_e}")

# Speech recognizer instance
_recognizer = sr.Recognizer()
_recognizer.dynamic_energy_threshold = True
_recognizer.dynamic_energy_adjustment_damping = 0.15
_recognizer.dynamic_energy_ratio = 1.5
_recognizer.pause_threshold = 0.8
_recognizer.non_speaking_duration = 0.5
_recognizer.energy_threshold = 300

# Wake words & common phonetic variants transcribed by STT
WAKE_WORDS = [
    "hey tuin", "hi tuin", "hello tuin", "ok tuin", "okay tuin",
    "tuin", "twin", "to in", "tu in", "tu-in", "tuwin",
    "doing", "tune", "to win", "the win", "queen", "tewin"
]

# Mute toggle state
_is_muted = False


def set_muted(muted: bool) -> None:
    """Sets whether voice audio output is silenced."""
    global _is_muted
    _is_muted = muted


def is_muted() -> bool:
    """Returns True if voice audio output is currently muted."""
    return _is_muted


def play_cue(frequency: int = 1200, duration_ms: int = 150) -> None:
    """Plays a short audio tone cue using native Windows sound."""
    try:
        winsound.Beep(frequency, duration_ms)
    except Exception:
        pass


def play_double_cue() -> None:
    """Plays a pleasant two-tone chime when Tuin starts listening."""
    try:
        winsound.Beep(900, 100)
        winsound.Beep(1350, 140)
    except Exception:
        pass


def stop_audio() -> None:
    """Stops and unloads any active pygame audio playback cleanly."""
    try:
        if pygame.mixer.get_init():
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.music.unload()
    except Exception:
        pass


def calibrate_microphone() -> None:
    """Calibrates microphone once for background room noise."""
    try:
        stop_audio()
        with sr.Microphone() as source:
            print("[Calibrating microphone for ambient room noise... please wait 1 second]")
            _recognizer.adjust_for_ambient_noise(source, duration=0.8)
            if _recognizer.energy_threshold < 180:
                _recognizer.energy_threshold = 180
            elif _recognizer.energy_threshold > 900:
                _recognizer.energy_threshold = 900
            print(f"[Microphone ready! Energy threshold: {int(_recognizer.energy_threshold)}]")
    except Exception as exc:
        print(f"[Warning] Microphone calibration note: {exc}")


def clean_text_for_speech(text: str) -> str:
    """Cleans markdown formatting, code fences, symbols, and URLs from text."""
    if not text:
        return ""

    cleaned = re.sub(r"```[\s\S]*?```", " [code snippet omitted] ", text)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"https?://\S+|www\.\S+", "link", cleaned)
    cleaned = re.sub(r"[#*_~>]", "", cleaned)
    cleaned = re.sub(r"^\s*[-+•]\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _synthesize_fish_audio(text: str, output_path: str) -> bool:
    """
    Synthesizes speech using the primary Fish Audio SDK with model='s2.1-pro'
    and your cloned voice ID.
    """
    api_key = (os.getenv("FISH_API_KEY") or os.getenv("FISH_AUDIO_API_KEY", "")).strip()
    voice_id = (os.getenv("FISH_VOICE_ID") or os.getenv("FISH_AUDIO_VOICE_ID", "")).strip()

    if not api_key or not voice_id:
        return False

    try:
        # Use official fishaudio SDK
        client = FishAudio(api_key=api_key)
        audio_data = client.tts.convert(
            text=text,
            reference_id=voice_id,
            model="s2.1-pro"
        )
        save(audio_data, output_path)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 500

    except Exception as exc:
        print(f"[Fish Audio Notice] SDK generation failed ({exc}). Trying fallback...")
        # Direct REST API backup attempt
        try:
            import requests
            url = "https://api.fish.audio/v1/tts"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {"text": text, "reference_id": voice_id, "format": "mp3"}
            resp = requests.post(url, json=payload, headers=headers, timeout=12)
            if resp.status_code == 200 and len(resp.content) > 500:
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                return True
        except Exception:
            pass
        return False


async def _generate_edge_tts_audio(text: str, output_path: str) -> None:
    """Generates speech audio using edge-tts as reliable fallback."""
    communicate = edge_tts.Communicate(
        text,
        voice=TTS_FALLBACK_VOICE,
        pitch=VOICE_PITCH,
        rate=VOICE_RATE
    )
    await communicate.save(output_path)


def _run_coroutine_safely(coro):
    """Safely runs an async coroutine across threads or active loops."""
    try:
        return asyncio.run(coro)
    except RuntimeError:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(asyncio.run, coro).result()


def speak(text: str) -> None:
    """
    Speaks the given text aloud using Tuin's cloned voice (Fish Audio) or
    Edge-TTS fallback. Plays via pygame.mixer and immediately deletes temp files.
    """
    if _is_muted:
        return

    cleaned = clean_text_for_speech(text)
    if not cleaned:
        return

    temp_dir = tempfile.gettempdir()
    temp_filename = os.path.join(temp_dir, f"tuin_voice_{int(time.time() * 1000)}.mp3")

    try:
        # 1. Primary: Cloned voice via Fish Audio SDK
        success = _synthesize_fish_audio(cleaned, temp_filename)

        # 2. Fallback: Edge-TTS if Fish Audio is unconfigured or errors out
        if not success or not os.path.exists(temp_filename):
            _run_coroutine_safely(_generate_edge_tts_audio(cleaned, temp_filename))

        if not os.path.exists(temp_filename):
            return

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        stop_audio()

        # Load and play audio
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()

        # Wait until playback is finished
        clock = pygame.time.Clock()
        while pygame.mixer.music.get_busy():
            clock.tick(15)

    except Exception as exc:
        print(f"[TTS Playback Error] {exc}")
    finally:
        stop_audio()
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except Exception:
                pass


def listen(prompt: Optional[str] = None, timeout: Optional[int] = 5, phrase_time_limit: int = 12) -> Tuple[str, str]:
    """
    Listens for speech input from the microphone using SpeechRecognition and PyAudio.
    
    Returns:
        tuple (recognized_text, status):
        - (text, "SUCCESS") when speech was transcribed
        - ("", "TIMEOUT") when no sound was heard (silence)
        - ("", "UNCLEAR") when speech was unintelligible
        - ("", "ERROR") on mic or network failure
    """
    if prompt:
        print(prompt, end="", flush=True)

    time.sleep(0.2)

    try:
        with sr.Microphone() as source:
            audio = _recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        text = _recognizer.recognize_google(audio, language="en-IN").strip()
        return text, "SUCCESS"

    except sr.WaitTimeoutError:
        return "", "TIMEOUT"
    except sr.UnknownValueError:
        return "", "UNCLEAR"
    except sr.RequestError as exc:
        print(f"\n[STT Network Notice] Could not reach speech service: {exc}")
        return "", "ERROR"
    except Exception as exc:
        print(f"\n[Microphone Error] {exc}")
        return "", "ERROR"


def listen_for_wake_word(listen_timeout: int = 3, phrase_time_limit: int = 4) -> Tuple[bool, str]:
    """
    Listens in short phrases for 'tuin' (and common phonetic matches 'twin',
    'to in', 'tuwin', 'hey tuin'). Returns (is_detected, extracted_command).
    """
    text, status = listen(timeout=listen_timeout, phrase_time_limit=phrase_time_limit)
    if status == "SUCCESS" and text:
        has_wake, command = extract_command_from_phrase(text)
        if has_wake:
            return True, command

    return False, ""


def extract_command_from_phrase(phrase: str) -> Tuple[bool, str]:
    """
    Checks if a wake word was said, and extracts the command portion.
    Examples:
      - "Hey Tuin play Kesariya" -> (True, "play Kesariya")
      - "Tuin" -> (True, "")
      - "What is my battery level?" -> (False, "What is my battery level?")
    """
    lower = phrase.lower().strip()
    for w in sorted(WAKE_WORDS, key=len, reverse=True):
        if lower.startswith(w):
            remainder = lower[len(w):].strip(" ,.!?")
            return True, remainder
        elif w in lower:
            idx = lower.find(w)
            remainder = (lower[:idx] + " " + lower[idx + len(w):]).strip(" ,.!?")
            return True, remainder

    return False, phrase
