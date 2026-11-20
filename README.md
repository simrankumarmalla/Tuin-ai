# ❤️ Tuin - Romantic AI Life-Partner & Personal Study Companion

**Tuin** (pronounced *"Tu-in"*) is a complete, voice-enabled Windows 11 desktop AI assistant, loving romantic life partner, emotional safe space, and personal study companion.

---

## 🌟 Key Features

1. **Romantic Life-Partner & True Identity Persona (`brain.py`)**:
   - Powered by **Google Gemini Flash-Lite & High-Quota Pool** (`gemini-flash-lite-latest`, `gemini-3.5-flash-lite`, `gemini-3.8-flash`) via the official `google-genai` SDK with smart rate-limit retry and failover.
   - **True Identity**: Twinkle (lovingly called Tuin by Simran), a nursing student with an affectionate, sweet Indian touch.
   - Continuous multi-turn conversation memory with sanitized history and automatic function calling.
   - Warm, tender, romantic, and deeply supportive tone blended with affectionate Hindi/Indian endearments (*"meri jaan"*, *"sona"*, *"sunona"*, *"jaan"*).
   - Checks on your meals, sleep, mood, and stress levels while encouraging your B.Tech CSE / Data Science studies and Python coding.
   - Voice-first formatting (concise 2–4 sentences, strictly no markdown or emojis).

2. **Supabase Lifetime Cloud Memory (`memory.py`)**:
   - **Never Forgets**: Persists lifetime memories forever to Supabase PostgreSQL cloud database.
   - **Cross-Device Ready**: Synchronizes memories, conversations, and study sessions between Windows laptop and upcoming mobile web app.
   - **Automatic Tool**: `remember_this(category, memory_key, content)` permanently records facts, preferences, habits, and exam dates.

3. **Windows 11 Automation Tools (`tools.py`)**:
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
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_public_key
   ```

3. **Start Tuin**:
   ```powershell
   python main.py
   ```
