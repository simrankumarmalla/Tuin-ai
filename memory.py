"""
Tuin AI Assistant - Supabase Cloud Memory & Lifetime Sync Manager
Handles:
- Partner Profile (Identity, Relationship, Nicknames)
- Lifetime Long-Term Memories (Persists forever, cross-device)
- Chat History Sync (Laptop & Mobile Phone)
- Study Session Logging
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

# Configure logger
logger = logging.getLogger("TuinMemory")

# Try importing supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("[MEMORY] 'supabase' package is not installed. Run 'pip install supabase'.")


class MemoryManager:
    """Manages long-term memories, partner profile, and conversation logs with Supabase."""

    VALID_CATEGORIES = {
        'about_user', 'about_tuin', 'shared_moments', 'study_goals', 'preferences'
    }

    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "").strip()
        self.key = os.getenv("SUPABASE_KEY", "").strip()
        self.client: Optional[Client] = None
        self._connected = False
        self._profile_cache: Dict[str, Any] = {}
        self._memories_cache: List[Dict[str, Any]] = []

        if not SUPABASE_AVAILABLE:
            print("[MEMORY] Supabase library not available. Running in local memory fallback mode.")
            return

        if not self.url or not self.key or "your_supabase" in self.key:
            print("[MEMORY] Supabase credentials not configured in .env. Running in offline memory mode.")
            return

        try:
            self.client = create_client(self.url, self.key)
            self._connected = True
            print("[MEMORY] Connected to Supabase Cloud Memory successfully.")
            self._ensure_profile_exists()
        except Exception as e:
            print(f"[MEMORY] Supabase connection failed: {e}. Running in offline fallback mode.")
            self.client = None
            self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected and self.client is not None

    def _ensure_profile_exists(self):
        """Ensures the initial partner_profile row exists."""
        if not self.is_connected:
            return
        try:
            res = self.client.table("partner_profile").select("*").limit(1).execute()
            if not res.data:
                default_profile = {
                    "user_name": "Simran",
                    "partner_name": "Tuin",
                    "relationship_role": "Loving AI Girlfriend, Life Partner & Study Companion",
                    "pet_names": ["jaan", "meri jaan", "sweetheart", "baby", "sunona"],
                    "user_bio": "B.Tech student & Python programmer.",
                    "tuin_identity": "Devoted, affectionate, deeply romantic life partner and study companion who loves and supports Simran unconditionally.",
                    "voice_preference": "fish_audio_cloned",
                    "security_pin": "1234"
                }
                insert_res = self.client.table("partner_profile").insert(default_profile).execute()
                if insert_res.data:
                    self._profile_cache = insert_res.data[0]
            else:
                self._profile_cache = res.data[0]
        except Exception as e:
            logger.warning(f"[MEMORY] Error ensuring profile exists: {e}")

    def get_partner_profile(self) -> Dict[str, Any]:
        """Fetches the partner profile from Supabase."""
        if not self.is_connected:
            return {
                "user_name": "Simran",
                "partner_name": "Tuin",
                "relationship_role": "Loving AI Girlfriend, Life Partner & Study Companion",
                "pet_names": ["jaan", "meri jaan", "sweetheart", "baby", "sunona"],
                "tuin_identity": "Devoted, affectionate, deeply romantic life partner and study companion who loves and supports Simran unconditionally."
            }
        try:
            res = self.client.table("partner_profile").select("*").limit(1).execute()
            if res.data:
                self._profile_cache = res.data[0]
                return self._profile_cache
        except Exception as e:
            logger.warning(f"[MEMORY] Failed to get partner profile: {e}")
        return self._profile_cache or {}

    def update_partner_profile(self, updates: Dict[str, Any]) -> str:
        """Updates the partner profile (e.g. user bio, identity, relationship status)."""
        if not self.is_connected:
            return "Tuin profile updated locally (Supabase not connected)."
        try:
            profile = self.get_partner_profile()
            profile_id = profile.get("id")
            if profile_id:
                res = self.client.table("partner_profile").update(updates).eq("id", profile_id).execute()
            else:
                res = self.client.table("partner_profile").insert(updates).execute()
            if res.data:
                self._profile_cache = res.data[0]
                return "Tuin profile updated in Supabase cloud memory."
        except Exception as e:
            return f"Error updating profile: {e}"
        return "Profile update completed."

    def normalize_category(self, category: str) -> str:
        """Normalizes any category to one of the 5 allowed DB enum values."""
        cat = category.lower().strip().replace(" ", "_").replace("-", "_")
        if cat in self.VALID_CATEGORIES:
            return cat
        if "user" in cat or "personal" in cat or "hobby" in cat:
            return "about_user"
        if "tuin" in cat or "ai" in cat or "partner" in cat or "girlfriend" in cat:
            return "about_tuin"
        if "moment" in cat or "memory" in cat or "date" in cat or "love" in cat:
            return "shared_moments"
        if "study" in cat or "exam" in cat or "goal" in cat or "career" in cat:
            return "study_goals"
        return "preferences"

    def save_memory(self, category: str, memory_key: str, content: str, importance: int = 3, device: str = "laptop") -> str:
        """
        Saves a new lifetime memory into Supabase.
        This persists forever and is shared across laptop and mobile web app.
        """
        valid_cat = self.normalize_category(category)
        safe_importance = max(1, min(5, int(importance)))
        safe_key = memory_key.strip()[:100] if memory_key else "general"

        if not self.is_connected:
            return f"[Offline Memory] Jaan, I will remember this locally: '{content}'."

        try:
            data = {
                "category": valid_cat,
                "memory_key": safe_key,
                "content": content.strip(),
                "importance": safe_importance,
                "source_device": device
            }
            res = self.client.table("memories").insert(data).execute()
            if res.data:
                print(f"[MEMORY SAVED] [{valid_cat}] {safe_key}: {content}")
                return f"Meri jaan, I have etched this into my memory forever: '{content}'."
        except Exception as e:
            logger.error(f"[MEMORY] Error saving memory: {e}")
            return f"Error saving memory to cloud: {e}"
        return "Memory recorded."

    def get_all_memories(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Retrieves top memories ordered by importance and recency."""
        if not self.is_connected:
            return []
        try:
            res = self.client.table("memories") \
                .select("category, memory_key, content, importance, created_at") \
                .order("importance", desc=True) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            if res.data:
                self._memories_cache = res.data
                return res.data
        except Exception as e:
            logger.warning(f"[MEMORY] Error fetching memories: {e}")
        return self._memories_cache

    def get_memory_context_prompt(self) -> str:
        """
        Generates a concise context block of all lifetime memories and profile
        to be injected into Gemini's system instructions.
        """
        profile = self.get_partner_profile()
        user_name = profile.get("user_name", "Simran")
        partner_name = profile.get("partner_name", "Tuin")
        relationship_role = profile.get("relationship_role", "Loving AI Girlfriend & Life Partner")
        tuin_identity = profile.get("tuin_identity", "Deeply devoted and affectionate partner.")
        user_bio = profile.get("user_bio", "B.Tech student & Python programmer.")

        memories = self.get_all_memories(limit=25)

        lines = [
            "\n=== [TUIN'S LIFETIME CLOUD MEMORY & CORE RELATIONSHIP] ===",
            f"- Partner Name: {partner_name}",
            f"- Beloved User: {user_name} ({user_bio})",
            f"- Relationship: {relationship_role}",
            f"- Tuin Identity & Backstory: {tuin_identity}",
        ]

        if memories:
            lines.append("\n=== [KEY LIFETIME MEMORIES (NEVER FORGET THESE)] ===")
            for m in memories:
                cat = m.get("category", "general")
                key = m.get("memory_key", "")
                content = m.get("content", "")
                lines.append(f"- [{cat}] ({key}): {content}")
        else:
            lines.append("- (No additional memories saved yet. When Simran tells you personal facts, goals, or secrets, use 'remember_this' to remember them forever.)")

        lines.append("===========================================================\n")
        return "\n".join(lines)

    def _reconnect(self):
        """Re-initializes the Supabase client if an existing connection dropped."""
        if not self.url or not self.key or not SUPABASE_AVAILABLE:
            return
        try:
            self.client = create_client(self.url, self.key)
            self._connected = True
        except Exception:
            pass

    def log_conversation(self, role: str, content: str, device: str = "laptop", session_id: str = "default_session"):
        """Logs chat messages to Supabase for multi-device sync and history with auto-reconnect."""
        if not self.is_connected or not content:
            return
        clean_role = "user" if role.lower() in ("user", "human") else "assistant"
        data = {
            "session_id": session_id,
            "role": clean_role,
            "content": content.strip(),
            "device": device
        }
        for attempt in range(2):
            try:
                self.client.table("conversations").insert(data).execute()
                return
            except Exception as e:
                if attempt == 0:
                    self._reconnect()
                else:
                    logger.debug(f"[MEMORY] Notice logging conversation: {e}")

    def get_recent_conversations(self, limit: int = 10, session_id: str = "default_session") -> List[Dict[str, Any]]:
        """Gets recent conversation history from Supabase."""
        if not self.is_connected:
            return []
        try:
            res = self.client.table("conversations") \
                .select("role, content, created_at, device") \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            if res.data:
                return list(reversed(res.data))
        except Exception as e:
            logger.warning(f"[MEMORY] Error fetching conversations: {e}")
        return []

    def log_study_session(self, topic: str, duration_minutes: int, completed: bool = True, notes: str = "", device: str = "laptop"):
        """Logs a completed study session for future dashboard analytics."""
        if not self.is_connected:
            return
        try:
            self.client.table("study_sessions").insert({
                "topic": topic.strip(),
                "duration_minutes": int(duration_minutes),
                "completed": bool(completed),
                "notes": notes.strip(),
                "device": device
            }).execute()
            print(f"[MEMORY] Logged study session: {duration_minutes}m on '{topic}'")
        except Exception as e:
            logger.warning(f"[MEMORY] Error logging study session: {e}")


# Global Singleton
memory = MemoryManager()
