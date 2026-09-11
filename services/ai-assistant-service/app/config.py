import os
from pathlib import Path
from dotenv import load_dotenv

# Search locations for .env.openai
_current_file = Path(__file__).resolve()
_search_dirs = [
    Path.cwd(),  # Where command is launched from
    _current_file.parent.parent,  # services/ai-assistant-service
    _current_file.parent.parent.parent.parent,  # workspace root
]

env_loaded = False
loaded_from_path = None

for d in _search_dirs:
    env_file = d / ".env.openai"
    if env_file.exists() and env_file.is_file():
        load_dotenv(dotenv_path=env_file, override=True)
        env_loaded = True
        loaded_from_path = str(env_file)
        break

# Also fallback to standard .env if .env.openai not found
if not env_loaded:
    for d in _search_dirs:
        standard_env = d / ".env"
        if standard_env.exists() and standard_env.is_file():
            load_dotenv(dotenv_path=standard_env)
            loaded_from_path = str(standard_env)
            break

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    CATALOG_URL: str = os.getenv("CATALOG_URL", "http://localhost:8082").rstrip("/")
    INVENTORY_URL: str = os.getenv("INVENTORY_URL", "http://localhost:8083").rstrip("/")
    PORT: int = int(os.getenv("PORT", "8088"))
    ENV_SOURCE: str = loaded_from_path or "system environment"

    # Chroma DB Vector Database
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost").strip()
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))
    CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "polyglot_store_knowledge").strip()
    CHROMA_DATA_DIR: str = os.getenv("CHROMA_DATA_DIR", "./chroma_data")

    @classmethod
    def is_openai_configured(cls) -> bool:
        key = cls.OPENAI_API_KEY
        if not key:
            return False
        if key in ("your_openai_api_key_here", "sk-...", "TODO", "your-key-here"):
            return False
        return len(key) > 10

settings = Settings()
