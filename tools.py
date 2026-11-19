"""
tools.py - Bulletproof Windows 11 Laptop Control & Study Tools for Tuin AI Assistant

Provides clean, type-annotated functions designed for Gemini automatic tool/function calling:
- open_app: Opens Windows 11 desktop and UWP store apps (Spotify, WhatsApp, VS Code, Chrome, etc.)
- search_google: Opens Google search in the default web browser
- play_song: Plays any song on YouTube hands-free using pywhatkit with browser fallback
- open_youtube_and_search: Opens YouTube home or directly searches for a video in the browser
- youtube_search_and_type: Smooth YouTube search and typing automation
- open_whatsapp: Opens WhatsApp Desktop or WhatsApp Web
- system_control: Controls volume, mute, checks battery and system resource metrics
- start_study_timer: Non-blocking background Pomodoro study timer with voice reminder
"""

import os
import subprocess
import threading
import time
import traceback
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


def open_app(app_name: str) -> str:
    """
    Opens common Windows applications and UWP store apps (Spotify, WhatsApp, VS Code,
    Chrome, Notepad, Calculator, File Explorer, Terminal) reliably on Windows 11.

    Args:
        app_name: The name or alias of the application to open.
                  Examples: 'spotify', 'whatsapp', 'youtube', 'chrome', 'google',
                  'vscode', 'vs code', 'notepad', 'calculator', 'explorer', 'files', 'terminal'.

    Returns:
        A confirmation message indicating whether the application launched.
    """
    clean_name = app_name.lower().strip()

    try:
        if "spotify" in clean_name:
            try:
                os.startfile("spotify:")
                result = "Opened Spotify app for you, meri jaan."
            except OSError:
                webbrowser.open("https://open.spotify.com")
                result = "Spotify desktop app was not found, so I opened Spotify Web in your browser for you, jaan."

        elif "whatsapp" in clean_name:
            try:
                os.startfile("whatsapp:")
                result = "Opened WhatsApp Desktop for you, meri jaan."
            except OSError:
                webbrowser.open("https://web.whatsapp.com")
                result = "WhatsApp Desktop was not found, so I opened WhatsApp Web in your browser, sweetheart."

        elif "youtube" in clean_name:
            webbrowser.open("https://www.youtube.com")
            result = "Opened YouTube in your browser for you, jaan."

        elif clean_name in ("google", "chrome", "google chrome", "browser"):
            try:
                subprocess.Popen("start chrome", shell=True)
                result = "Opened Google Chrome for you, meri jaan."
            except Exception:
                webbrowser.open("https://www.google.com")
                result = "Opened Google in your default browser for you, jaan."

        elif clean_name in ("vscode", "vs code", "code", "visual studio code"):
            subprocess.Popen("code", shell=True)
            result = "Launched VS Code for your coding session, jaan. Let's build something amazing!"

        elif clean_name in ("notepad", "notes"):
            subprocess.Popen("notepad.exe")
            result = "Opened Notepad for you, sweetheart."

        elif clean_name in ("calculator", "calc"):
            subprocess.Popen("calc.exe")
            result = "Opened Calculator for you, jaan."

        elif clean_name in ("explorer", "files", "file explorer", "my computer"):
            subprocess.Popen("explorer.exe")
            result = "Opened File Explorer for you, meri jaan."

        elif clean_name in ("terminal", "cmd", "command prompt", "powershell"):
            try:
                subprocess.Popen("wt.exe")
                result = "Opened Windows Terminal for you, jaan."
            except Exception:
                subprocess.Popen("cmd.exe")
                result = "Opened Command Prompt for you, jaan."

        else:
            # Fallback for any other installed Windows application
            subprocess.Popen(f'start "" "{clean_name}"', shell=True)
            result = f"Attempted to open {app_name}. If it is installed on Windows, it should be opening now, jaan."

        print(f"[TOOL EXECUTED] open_app(app_name='{app_name}') -> {result}")
        return result

    except Exception as exc:
        traceback.print_exc()
        err_msg = f"Sorry jaan, I could not open {app_name}. Error: {str(exc)}"
        print(f"[TOOL ERROR] open_app(app_name='{app_name}') -> {err_msg}")
        return err_msg


def open_youtube_and_search(query: str = "") -> str:
    """
    Opens YouTube directly in the default browser. If a search query is provided,
    it immediately navigates to the search results page so it never fails due to
    window focus issues.

    Args:
        query: Optional search query (e.g. 'lofi hip hop', 'machine learning tutorial').
               If empty, opens the YouTube homepage.

    Returns:
        A confirmation message indicating that YouTube has been opened.
    """
    clean_query = query.strip()
    try:
        if not clean_query:
            webbrowser.open("https://www.youtube.com")
            result = "Opened YouTube homepage for you, meri jaan."
        else:
            encoded = urllib.parse.quote_plus(clean_query)
            url = f"https://www.youtube.com/results?search_query={encoded}"
            webbrowser.open(url)
            result = f"Opened YouTube search results for '{clean_query}', jaan."

        print(f"[TOOL EXECUTED] open_youtube_and_search(query='{clean_query}') -> {result}")
        return result
    except Exception as exc:
        traceback.print_exc()
        err_msg = f"Could not open YouTube search. Error: {str(exc)}"
        print(f"[TOOL ERROR] open_youtube_and_search -> {err_msg}")
        return err_msg


def play_song(song_name: str) -> str:
    """
    Automatically plays the requested song or music on YouTube hands-free using pywhatkit.
    If pywhatkit encounters network or timeout issues, automatically falls back to opening
    the search results in the browser so the song ALWAYS opens.

    Args:
        song_name: The name of the song, artist, playlist, or music track to play.

    Returns:
        A confirmation message indicating that the song has started playing.
    """
    clean_song = song_name.strip()

    try:
        import pywhatkit
        pywhatkit.playonyt(clean_song)
        result = f"Playing '{clean_song}' on YouTube for you, jaan. Enjoy your music!"
    except Exception as exc:
        traceback.print_exc()
        encoded = urllib.parse.quote_plus(clean_song)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        result = f"Opened YouTube for '{clean_song}' so your music starts right up, meri jaan."

    print(f"[TOOL EXECUTED] play_song(song_name='{clean_song}') -> {result}")
    return result


def youtube_search_and_type(search_text: str) -> str:
    """
    Opens YouTube, waits briefly for the page to load, focuses the search bar via '/',
    and types the query smoothly with pyautogui so you can watch Tuin type for you.
    Also falls back to open_youtube_and_search if typing fails.

    Args:
        search_text: The video title, tutorial topic, or query to type on YouTube.

    Returns:
        A confirmation message indicating that Tuin is typing the search.
    """
    clean_text = search_text.strip()

    try:
        webbrowser.open("https://www.youtube.com")

        def _type_worker():
            time.sleep(2.5)
            try:
                pyautogui.press("/")
                time.sleep(0.3)
                pyautogui.write(clean_text, interval=0.06)
                time.sleep(0.3)
                pyautogui.press("enter")
            except Exception:
                # Fallback to direct search URL if pyautogui fails
                encoded = urllib.parse.quote_plus(clean_text)
                webbrowser.open(f"https://www.youtube.com/results?search_query={encoded}")

        threading.Thread(target=_type_worker, daemon=True).start()
        result = f"Opened YouTube and typing '{clean_text}' into the search bar for you right now, sunona!"
        print(f"[TOOL EXECUTED] youtube_search_and_type(search_text='{clean_text}') -> {result}")
        return result

    except Exception as exc:
        traceback.print_exc()
        # Direct browser fallback
        return open_youtube_and_search(clean_text)


def search_google(query: str) -> str:
    """
    Opens the default web browser and immediately searches Google for the query.

    Args:
        query: The search term, question, or phrase to search on Google.

    Returns:
        A confirmation message indicating that the Google search has been opened.
    """
    clean_query = query.strip()
    encoded = urllib.parse.quote_plus(clean_query)
    url = f"https://www.google.com/search?q={encoded}"

    try:
        webbrowser.open(url)
        result = f"Opened a Google search for '{clean_query}' in your browser, meri jaan."
        print(f"[TOOL EXECUTED] search_google(query='{clean_query}') -> {result}")
        return result
    except Exception as exc:
        traceback.print_exc()
        err_msg = f"Sorry jaan, I could not open Google search for '{clean_query}'. Error: {str(exc)}"
        print(f"[TOOL ERROR] search_google -> {err_msg}")
        return err_msg


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
    try:
        try:
            os.startfile("whatsapp:")
            result = "Opened WhatsApp Desktop for you, meri jaan. Check your messages!"
        except OSError:
            webbrowser.open("https://web.whatsapp.com")
            result = "WhatsApp Desktop was not found, so I opened WhatsApp Web in your browser for you, sweetheart."

        print(f"[TOOL EXECUTED] open_whatsapp(contact_or_message='{contact_or_message}') -> {result}")
        return result

    except Exception as exc:
        traceback.print_exc()
        err_msg = f"Could not open WhatsApp. Error: {str(exc)}"
        print(f"[TOOL ERROR] open_whatsapp -> {err_msg}")
        return err_msg


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

    try:
        if action_key in ("volume_up", "vol_up"):
            for _ in range(5):
                pyautogui.press("volumeup")
            result = "Turned the volume up for you, jaan."

        elif action_key in ("volume_down", "vol_down"):
            for _ in range(5):
                pyautogui.press("volumedown")
            result = "Turned the volume down for you, sweetheart."

        elif action_key == "mute":
            pyautogui.press("volumemute")
            result = "Toggled the system mute status for you, meri jaan."

        elif action_key in ("battery_status", "battery", "battery_check"):
            battery = psutil.sensors_battery()
            if battery is None:
                result = "Your laptop is running on direct AC power with no battery detected, jaan."
            else:
                percent = round(battery.percent)
                is_plugged = battery.power_plugged
                status_text = "plugged in and charging" if is_plugged else "running on battery"
                warning = ""
                if percent <= 20 and not is_plugged:
                    warning = " Sweetheart, your battery is quite low! Please plug in the charger so your work does not get interrupted."
                elif percent >= 95 and is_plugged:
                    warning = " Battery is almost full, jaan."
                result = f"Your battery is at {percent} percent and currently {status_text}.{warning}"

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

            result = (
                f"Laptop check: CPU usage is {cpu_usage} percent, and RAM usage is "
                f"{ram_usage} percent with {free_gb} GB free.{advice}"
            )

        else:
            result = (
                f"Unknown system control action '{action}'. "
                "Supported actions: volume_up, volume_down, mute, battery_status, and system_stats."
            )

        print(f"[TOOL EXECUTED] system_control(action='{action}') -> {result}")
        return result

    except Exception as exc:
        traceback.print_exc()
        err_msg = f"Could not perform system action '{action}'. Error: {str(exc)}"
        print(f"[TOOL ERROR] system_control -> {err_msg}")
        return err_msg


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

    def _timer_worker():
        alert_msg = f"\n\n⏰ [Timer Finished] Great job jaan! You completed your {duration_minutes}-minute study on '{clean_topic}'!\n"
        print(alert_msg)

        if _timer_alert_callback is not None:
            try:
                _timer_alert_callback(clean_topic, duration_minutes)
            except Exception as e:
                traceback.print_exc()
                print(f"[Timer Alert Error] {e}")

    # Use threading.Timer for non-blocking execution
    timer = threading.Timer(duration_seconds, _timer_worker)
    timer.daemon = True
    timer.start()

    result = (
        f"Timer set for {duration_minutes} minutes for '{clean_topic}', meri jaan. "
        "Put distractions away, focus with all your heart, and I will remind you when it is time to rest. Chalo, you can do this!"
    )
    print(f"[TOOL EXECUTED] start_study_timer(minutes={duration_minutes}, topic='{clean_topic}') -> {result}")
    return result
