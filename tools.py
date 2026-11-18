"""
tools.py - Windows 11 Laptop Control & Study Tools for Tuin AI Assistant

Provides clean, type-annotated functions designed for Gemini automatic tool/function calling:
- search_google: Searches Google in the default browser
- play_song: Automatically plays any song on YouTube hands-free using pywhatkit
- youtube_search_and_type: Opens YouTube and visually types in the search query for the user
- open_whatsapp: Opens WhatsApp Desktop or WhatsApp Web
- open_app: Launches common Windows 11 desktop applications
- system_control: Controls volume, mute, checks battery and system resource metrics
- start_study_timer: Non-blocking background study timer for Pomodoro sessions with voice alert
"""

import os
import subprocess
import threading
import time
import urllib.parse
import webbrowser
from typing import Callable, Optional

import psutil
import pyautogui

# Global timer alert callback hook (configured by voice / main module)
_timer_alert_callback: Optional[Callable[[str, int], None]] = None


def set_timer_alert_callback(callback: Callable[[str, int], None]) -> None:
    """Sets a global callback to be invoked when a study timer completes."""
    global _timer_alert_callback
    _timer_alert_callback = callback


def search_google(query: str) -> str:
    """
    Opens the default web browser and immediately searches Google for the query.

    Args:
        query: The search term, question, or phrase to search on Google.

    Returns:
        A confirmation message indicating that the Google search has been opened.
    """
    clean_query = query.strip()
    print(f"\n[Tool Executing] search_google: '{clean_query}'")
    encoded_query = urllib.parse.quote_plus(clean_query)
    url = f"https://www.google.com/search?q={encoded_query}"

    try:
        webbrowser.open(url)
        return f"I have opened a Google search for '{clean_query}' in your browser, meri jaan."
    except Exception as exc:
        return f"Sorry jaan, I could not open Google search for '{clean_query}'. Error: {str(exc)}"


def play_song(song_name: str) -> str:
    """
    Automatically plays the requested song or music on YouTube in the default browser
    using pywhatkit so the music starts playing hands-free without clicking anything.

    Args:
        song_name: The name of the song, artist, playlist, or music track to play.

    Returns:
        A confirmation message indicating that the song has started playing.
    """
    clean_song = song_name.strip()
    print(f"\n[Tool Executing] play_song: '{clean_song}'")

    try:
        import pywhatkit
        pywhatkit.playonyt(clean_song)
        return f"Playing '{clean_song}' on YouTube for you, jaan. Enjoy your music!"
    except Exception as exc:
        # Fallback to direct browser search if pywhatkit encounters network/driver issues
        print(f"[play_song fallback] {exc}")
        encoded = urllib.parse.quote_plus(clean_song)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        return f"Opened YouTube for '{clean_song}' so you can listen to your favorite track right now, jaan."


def youtube_search_and_type(search_text: str) -> str:
    """
    Opens YouTube in the default browser, waits for the page to load, activates the
    search bar via keyboard shortcut (/), types the search query smoothly, and presses Enter
    so you can watch Tuin type and search on YouTube for you.

    Args:
        search_text: The video title, tutorial topic, or query to type on YouTube.

    Returns:
        A confirmation message indicating that Tuin has typed and searched on YouTube.
    """
    clean_text = search_text.strip()
    print(f"\n[Tool Executing] youtube_search_and_type: '{clean_text}'")

    try:
        # Open YouTube home
        webbrowser.open("https://www.youtube.com")

        # Non-blocking thread to allow page loading, then type smoothly
        def _type_worker():
            time.sleep(3.0)  # Wait for YouTube page to load
            # YouTube shortcut to focus the search bar is '/'
            pyautogui.press("/")
            time.sleep(0.4)
            # Type search text with a human typing cadence
            pyautogui.write(clean_text, interval=0.06)
            time.sleep(0.3)
            pyautogui.press("enter")

        threading.Thread(target=_type_worker, daemon=True).start()
        return f"I opened YouTube and I am typing '{clean_text}' into the search bar for you right now, sunona!"

    except Exception as exc:
        return f"Could not type search on YouTube. Error: {str(exc)}"


def open_whatsapp(contact_or_message: str = "") -> str:
    """
    Opens WhatsApp Desktop on Windows (whatsapp: protocol). If the desktop app is
    not installed or fails to launch, automatically falls back to opening WhatsApp Web
    (https://web.whatsapp.com) in the browser.

    Args:
        contact_or_message: Optional contact name or note for reference.

    Returns:
        A confirmation message indicating WhatsApp has been opened.
    """
    print(f"\n[Tool Executing] open_whatsapp: '{contact_or_message}'")

    try:
        # Try launching WhatsApp Desktop via URI scheme
        os.startfile("whatsapp:")
        return "Opened WhatsApp Desktop for you, meri jaan. Check your messages!"
    except Exception:
        try:
            # Secondary desktop command attempt
            subprocess.Popen(["cmd", "/c", "start", "whatsapp:"], shell=True)
            return "Launching WhatsApp Desktop for you, jaan."
        except Exception:
            # Fallback to WhatsApp Web
            webbrowser.open("https://web.whatsapp.com")
            return "WhatsApp Desktop was not found, so I opened WhatsApp Web in your browser for you, sweetheart."


def open_app(app_name: str) -> str:
    """
    Opens common Windows applications such as Chrome, VS Code, Spotify, Notepad,
    File Explorer, Calculator, or Windows Terminal on Windows 11.

    Args:
        app_name: The name or alias of the application to open.
                  Supported examples: 'chrome', 'vscode', 'spotify', 'notepad',
                  'explorer', 'calculator', 'terminal'.

    Returns:
        A confirmation message indicating whether the application launched.
    """
    app_key = app_name.strip().lower()
    print(f"\n[Tool Executing] open_app: '{app_name}'")

    app_commands = {
        "chrome": ["cmd", "/c", "start", "chrome"],
        "google chrome": ["cmd", "/c", "start", "chrome"],
        "browser": ["cmd", "/c", "start", "chrome"],
        "vscode": ["cmd", "/c", "code"],
        "code": ["cmd", "/c", "code"],
        "vs code": ["cmd", "/c", "code"],
        "visual studio code": ["cmd", "/c", "code"],
        "spotify": ["cmd", "/c", "start", "spotify:"],
        "music": ["cmd", "/c", "start", "spotify:"],
        "notepad": ["notepad.exe"],
        "notes": ["notepad.exe"],
        "explorer": ["explorer.exe"],
        "file explorer": ["explorer.exe"],
        "files": ["explorer.exe"],
        "calculator": ["calc.exe"],
        "calc": ["calc.exe"],
        "terminal": ["cmd", "/c", "start", "wt"],
        "windows terminal": ["cmd", "/c", "start", "wt"],
        "powershell": ["cmd", "/c", "start", "powershell"],
        "cmd": ["cmd", "/c", "start", "cmd"],
        "command prompt": ["cmd", "/c", "start", "cmd"],
    }

    try:
        if app_key in app_commands:
            subprocess.Popen(app_commands[app_key], shell=True)
            return f"Opened {app_name.title()} for you, meri jaan."

        # Generic launch attempt for any registered Windows app
        subprocess.Popen(["cmd", "/c", "start", app_key], shell=True)
        return f"Attempted to open {app_name}. If it is installed on your laptop, it should be opening now, jaan."

    except Exception as exc:
        return f"Sorry jaan, I could not open {app_name}. Error: {str(exc)}"


def system_control(action: str) -> str:
    """
    Controls Windows 11 system settings and retrieves hardware metrics so Tuin
    can warn you if your laptop battery is low or running hot.

    Args:
        action: The control or diagnostic action to perform:
                - 'volume_up': Increases volume by a few notches
                - 'volume_down': Decreases volume by a few notches
                - 'mute': Toggles system audio mute
                - 'battery_status': Returns battery level and charging state
                - 'system_stats': Returns CPU and RAM utilization

    Returns:
        A natural-language response describing the outcome or system status.
    """
    action_key = action.strip().lower()
    print(f"\n[Tool Executing] system_control: '{action_key}'")

    try:
        if action_key in ("volume_up", "vol_up"):
            for _ in range(5):
                pyautogui.press("volumeup")
            return "Turned the volume up for you, jaan."

        elif action_key in ("volume_down", "vol_down"):
            for _ in range(5):
                pyautogui.press("volumedown")
            return "Turned the volume down for you, sweetheart."

        elif action_key == "mute":
            pyautogui.press("volumemute")
            return "Toggled the system mute status for you, meri jaan."

        elif action_key in ("battery_status", "battery", "battery_check"):
            battery = psutil.sensors_battery()
            if battery is None:
                return "Your laptop is running on direct AC power with no battery detected, jaan."

            percent = round(battery.percent)
            is_plugged = battery.power_plugged
            status_text = "plugged in and charging" if is_plugged else "running on battery"

            warning = ""
            if percent <= 20 and not is_plugged:
                warning = " Sweetheart, your battery is quite low! Please plug in the charger so your work does not get interrupted."
            elif percent >= 95 and is_plugged:
                warning = " Battery is almost full, jaan."

            return f"Your battery is at {percent} percent and currently {status_text}.{warning}"

        elif action_key in ("system_stats", "stats", "cpu", "ram", "health"):
            cpu_usage = psutil.cpu_percent(interval=0.3)
            mem = psutil.virtual_memory()
            ram_usage = round(mem.percent)
            free_gb = round(mem.available / (1024 ** 3), 1)

            advice = ""
            if cpu_usage > 85:
                advice = " The CPU is running quite hot and heavy right now, jaan. Maybe close some background heavy tasks?"
            else:
                advice = " Everything is running cool and smooth, meri jaan."

            return (
                f"Laptop check: CPU usage is {cpu_usage} percent, and RAM usage is "
                f"{ram_usage} percent with {free_gb} GB free.{advice}"
            )

        else:
            return (
                f"Unknown system control action '{action}'. "
                "Supported actions: volume_up, volume_down, mute, battery_status, and system_stats."
            )

    except Exception as exc:
        return f"Could not perform system action '{action}'. Error: {str(exc)}"


def start_study_timer(minutes: int, topic: str = "Focus Session") -> str:
    """
    Starts a non-blocking background study timer for the specified topic and duration.
    When the timer completes, Tuin will notify and speak an affectionate reminder to take a break.

    Args:
        minutes: The duration of the study session in minutes (e.g. 25 for Pomodoro).
        topic: The topic, subject, or task being studied (e.g. 'Operating Systems', 'Python coding').

    Returns:
        A confirmation message that the timer has started.
    """
    clean_topic = topic.strip() if topic else "your focus session"
    duration_minutes = max(1, int(minutes))
    duration_seconds = duration_minutes * 60

    print(f"\n[Tool Executing] start_study_timer: {duration_minutes} min on '{clean_topic}'")

    def _timer_worker():
        time.sleep(duration_seconds)
        alert_msg = f"\n\n⏰ [Timer Finished] Great job jaan! You completed your {duration_minutes}-minute study on '{clean_topic}'!\n"
        print(alert_msg)

        if _timer_alert_callback is not None:
            try:
                _timer_alert_callback(clean_topic, duration_minutes)
            except Exception as e:
                print(f"[Timer Alert Error] {e}")

    thread = threading.Thread(target=_timer_worker, daemon=True)
    thread.start()

    return (
        f"Timer set for {duration_minutes} minutes for '{clean_topic}', meri jaan. "
        "Put distractions away, focus with all your heart, and I will remind you when it is time to rest. Chalo, you can do this!"
    )
