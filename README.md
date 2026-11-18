# ❤️ Tuin - Romantic AI Life-Partner & Personal Study Companion

**Tuin** (pronounced *"Tu-in"*) is a complete, voice-enabled Windows 11 desktop AI assistant, loving romantic life partner, emotional safe space, and personal study companion.

---

## 🌟 Key Features

1. **Romantic Life-Partner & Study Persona (`brain.py`)**:
   - Powered by **Google Gemini 3.8 Flash** (`gemini-3.8-flash`) via the official `google-genai` SDK.
   - Continuous multi-turn conversation memory with automatic function calling.
   - Warm, tender, romantic, and deeply supportive tone blended with affectionate Hindi/Indian endearments (*"jaan"*, *"meri jaan"*, *"sunona"*, *"yaar"*).
   - Checks on your meals, sleep, mood, and stress levels while encouraging your B.Tech CSE / Data Science studies and Python coding.
   - Voice-first formatting (concise 2–4 sentences, strictly no markdown or emojis).

2. **Windows 11 Automation Tools (`tools.py`)**:
   - **`search_google(query)`**: Opens Google search immediately in the default browser.
   - **`play_song(song_name)`**: Plays any song hands-free on YouTube using `pywhatkit.playonyt`.
   - **`youtube_search_and_type(search_text)`**: Opens YouTube and visually types the search query into the search bar for you to watch.
   - **`open_whatsapp(contact_or_message)`**: Opens WhatsApp Desktop (`whatsapp:`) with fallback to WhatsApp Web.
   - **`open_app(app_name)`**: Launches Windows apps (Chrome, VS Code, Spotify, Notepad, Explorer, Calculator, Terminal).
   - **`system_control(action)`**: Controls volume, mute, checks battery percentage, and monitors CPU/RAM health.
   - **`start_study_timer(minutes, topic)`**: Non-blocking background Pomodoro study timer with romantic voice alerts.

3. **Neural Cloned Voice Engine (`voice.py`)**:
   - **Primary Cloned Voice**: Uses `fishaudio` SDK (`FishAudio`, `save`) with model `s2.1-pro` to speak in your custom cloned voice.
   - **Automatic Fallback Voice**: Seamlessly falls back to `edge-tts` (`en-IN-NeerjaNeural` with tuned ~292Hz acoustic profile) if Fish Audio is unavailable.
   - **Speech Recognition**: Ambient noise calibration with PyAudio and SpeechRecognition.
   - **Wake Word**: Continuously listens for `"Tuin"`, `"Hey Tuin"`, `"twin"`, etc., with one-shot command execution.

4. **Interactive Modes (`main.py`)**:
   - **Mode 1: Text & Voice Chat**: Type in terminal; Tuin replies in text and her cloned voice. Supports `/mute`, `/unmute`, `/clear`, `/mode`, `/help`, `/exit`.
   - **Mode 2: Hands-Free Voice Partner Mode**: Speaks and listens hands-free for automation, questions, and romantic conversation.

---

## 🚀 How to Run

1. **Ensure dependencies are installed**:
   ```powershell
   pip install -r requirements.txt
   ```

2. **Check your `.env`**:
   Make sure your credentials are saved in `.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   FISH_API_KEY=your_fish_audio_api_key
   FISH_VOICE_ID=your_cloned_voice_id
   ```

3. **Start Tuin**:
   ```powershell
   python main.py
   ```
