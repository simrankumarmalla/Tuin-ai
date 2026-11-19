"""
main.py - Interactive Launcher & Mode Switcher for Tuin AI Assistant

Features:
- Warm, romantic greeting in Tuin's custom cloned voice on startup
- Mode 1: Text & Voice Chat (Terminal typing, cloned voice speech, /mute & /unmute toggles)
- Mode 2: Hands-Free Voice Partner Mode (Wake-word 'Tuin' detection, hands-free automation & romantic voice chat)
- Non-blocking background study timer integration with voice reminders
- Graceful shutdown on Ctrl+C (KeyboardInterrupt) with a sweet farewell
- Comprehensive error visibility (traceback printing on console)
"""

import os
import sys
import threading
import time
import traceback

from brain import TuinBrain
from tools import set_timer_alert_callback
import voice


def print_banner() -> None:
    """Displays an affectionate welcome banner in the console."""
    banner = r"""
  ==============================================================
   ❤️  TUIN - Your AI Girlfriend, Life Partner & Study Buddy  ❤️
  ==============================================================
   * Powered by Google Gemini 2.5 Flash (Production Tool Calling)
   * Voice Engine: Cloned Voice via Fish Audio SDK (s2.1-pro)
   * Automation: Google, YouTube Typing, Song Play, WhatsApp & Windows
   * Emotional Companion: Romantic, deeply caring & supportive
  ==============================================================
    """
    print(banner)


def setup_timer_alerts() -> None:
    """Configures the study timer completion callback to notify and speak to the user."""
    def _on_timer_complete(topic: str, minutes: int):
        alert_text = (
            f"Hey jaan, your {minutes}-minute study session on {topic} is finished. "
            "Please step away from your screen, stretch a bit, and drink some water for me. "
            "I am so proud of your hard work!"
        )
        print(f"\n⏰ [Tuin Timer Alert] {alert_text}\n")
        threading.Thread(target=voice.speak, args=(alert_text,), daemon=True).start()

    set_timer_alert_callback(_on_timer_complete)


def text_chat_mode(brain: TuinBrain) -> None:
    """
    Mode 1: Text & Voice Chat.
    Type prompts in the terminal, Tuin responds in text and cloned voice.
    Supports in-line commands: /mute, /unmute, /clear, /mode, /help, /exit.
    """
    print("\n--- [Mode 1: Text & Voice Chat Active] ---")
    print("Type your message to Tuin and press Enter.")
    print("Commands: /mute, /unmute, /clear (reset chat), /mode (switch to voice), /help, /exit\n")

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue

            # Command: Exit
            if user_input.lower() in ("/exit", "/quit", "exit", "quit"):
                farewell = "Goodbye for now, meri jaan! Take good care of yourself, and call me soon. Love you!"
                print(f"\nTuin: {farewell}")
                voice.speak(farewell)
                break

            # Command: Mute
            elif user_input.lower() == "/mute":
                voice.set_muted(True)
                print("[Tuin Voice Status] Muted. Tuin will reply in text only.")
                continue

            # Command: Unmute
            elif user_input.lower() == "/unmute":
                voice.set_muted(False)
                print("[Tuin Voice Status] Unmuted. Tuin will speak her responses aloud.")
                continue

            # Command: Clear history
            elif user_input.lower() == "/clear":
                brain.reset_history()
                print("[Chat History] Cleared! Starting a fresh conversation, jaan.")
                continue

            # Command: Switch to Mode 2
            elif user_input.lower() == "/mode":
                print("\nSwitching to Hands-Free Voice Partner Mode...")
                hands_free_voice_mode(brain)
                print("\nReturned to Text Chat Mode.")
                continue

            # Command: Help
            elif user_input.lower() == "/help":
                print("\n[Available Commands]")
                print("  /mute   - Silence voice output (text only)")
                print("  /unmute - Enable voice output")
                print("  /clear  - Clear conversation history")
                print("  /mode   - Switch directly to Hands-Free Voice Mode")
                print("  /exit   - Return to main menu\n")
                continue

            # Send prompt to Tuin's Gemini Brain
            print("[Tuin is thinking & caring for you...]")
            response = brain.chat_message(user_input)
            print(f"\nTuin: {response}")

            # Speak response aloud using her cloned voice
            voice.speak(response)

        except KeyboardInterrupt:
            print("\n\n[Chat Interrupted]")
            break
        except Exception as exc:
            traceback.print_exc()
            print(f"\n[Chat Error] {exc}")


def hands_free_voice_mode(brain: TuinBrain) -> None:
    """
    Mode 2: Hands-Free Voice Partner Mode.
    Listens continuously through your microphone for 'Tuin' or direct commands.
    Executes actions (playing songs, typing on YouTube, Google, WhatsApp, controls)
    and speaks back lovingly in her cloned voice.
    """
    voice.stop_audio()
    print("\n--- [Mode 2: Hands-Free Voice Partner Mode Active] ---")
    print("How to speak to Tuin:")
    print("  - Say 'Hey Tuin, play Kesariya' or 'Play a romantic song'")
    print("  - Say 'Hey Tuin, search Google for Python tutorial'")
    print("  - Say 'Hey Tuin, open WhatsApp' or 'Check my battery'")
    print("  - Say 'Hey Tuin' to get her attention, wait for the chime, then speak")
    print("  - Say 'exit' or press Ctrl+C to return to main menu.\n")

    # One-time noise calibration for current environment
    voice.calibrate_microphone()

    # Romantic greeting confirming voice mode is active
    activation_msg = (
        "Voice mode is on, meri jaan! I am right here with you. "
        "Talk to me or tell me what to do, I am listening."
    )
    print(f"\nTuin: {activation_msg}\n")
    voice.speak(activation_msg)
    voice.play_double_cue()

    while True:
        try:
            print("\n🎙️ [Tuin is listening... speak to your partner]", flush=True)
            text, status = voice.listen(timeout=7, phrase_time_limit=14)

            if status == "SUCCESS" and text:
                print(f"Heard: \"{text}\"")

                # Voice exit command
                if text.lower() in ("exit", "quit", "stop", "close voice mode", "go to text mode", "main menu"):
                    exit_msg = "Returning to the main menu for you, meri jaan."
                    print(f"Tuin: {exit_msg}")
                    voice.speak(exit_msg)
                    break

                # Check for wake word and extract command
                has_wake, command = voice.extract_command_from_phrase(text)

                # Case A: User said just the wake word (e.g. "Tuin" or "Hey Tuin")
                if has_wake and not command:
                    wake_ack = "Haan meri jaan, sunona! What can I do for you?"
                    print(f"Tuin: {wake_ack}")
                    voice.play_double_cue()
                    voice.speak(wake_ack)

                    # Listen specifically for the follow-up request
                    print("🎙️ [Listening for your request, jaan...]", flush=True)
                    cmd_text, cmd_status = voice.listen(timeout=8, phrase_time_limit=15)
                    if cmd_status == "SUCCESS" and cmd_text:
                        command = cmd_text
                        print(f"You said: \"{command}\"")
                    else:
                        print("[No follow-up heard. Continuing to stay on standby...]")
                        continue
                else:
                    # Case B: User gave a full command or spoke directly
                    command = command if command else text
                    print(f"You said: \"{command}\"")

                # Send command to Gemini brain (executes tools automatically)
                print("⚡ [Tuin is thinking & executing for you...]")
                voice.play_cue(1100, 80)
                response = brain.chat_message(command)

                # Print and speak response in her cloned voice
                print(f"\nTuin: {response}")
                voice.speak(response)

            elif status == "UNCLEAR":
                # Sound was heard, but audio was muffled
                unclear_ack = "I heard you talking jaan, but could not catch the words clearly. Could you repeat that for me?"
                print(f"\nTuin: {unclear_ack}")
                voice.speak(unclear_ack)

            elif status == "TIMEOUT":
                # Silence: continue listening quietly
                pass

        except KeyboardInterrupt:
            print("\n\n[Voice Mode Paused by User]")
            break
        except Exception as exc:
            traceback.print_exc()
            print(f"\n[Voice Mode Notice] {exc}")
            time.sleep(1)


def main() -> None:
    """Main application loop with mode selection and graceful lifecycle management."""
    print_banner()

    # Configure study timer alert callback
    setup_timer_alerts()

    # Initialize Gemini Brain
    brain = TuinBrain()

    # Romantic startup greeting
    startup_greeting = (
        "Hey sweetheart! I am Tuin, your loving partner and study companion. "
        "How has your day been so far, and did you take good care of yourself today?"
    )
    print(f"Tuin: {startup_greeting}\n")

    # Speak greeting in background
    threading.Thread(target=voice.speak, args=(startup_greeting,), daemon=True).start()

    while True:
        try:
            print("\n" + "=" * 45)
            print("  CHOOSE TUIN'S OPERATING MODE:")
            print("  [1] Text & Voice Chat (Type + Cloned Voice)")
            print("  [2] Hands-Free Voice Partner Mode")
            print("  [3] Exit")
            print("=" * 45)

            choice = input("Select an option (1, 2, or 3): ").strip()

            if choice == "1":
                text_chat_mode(brain)
            elif choice == "2":
                hands_free_voice_mode(brain)
            elif choice in ("3", "exit", "quit"):
                farewell = "Take good care of yourself, meri jaan. Drink some water and rest well. Love you always, bye!"
                print(f"\nTuin: {farewell}")
                voice.speak(farewell)
                print("\nTuin assistant closed cleanly. Have a wonderful day!")
                sys.exit(0)
            else:
                print("Invalid selection. Please choose 1, 2, or 3.")

        except KeyboardInterrupt:
            farewell = "Take care of yourself for me, meri jaan. Rest well, love you, bye!"
            print(f"\n\nTuin: {farewell}")
            try:
                voice.speak(farewell)
            except Exception:
                pass
            print("\nShutdown complete.")
            sys.exit(0)


if __name__ == "__main__":
    main()
