import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(os.environ.get("VIBRARY_DATA_DIR", "./data/demo")).expanduser()
DATABASE_URL = os.environ["DATABASE_URL"]
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

# BAAI/bge-small-en-v1.5 and all-MiniLM-L6-v2 both produce 384-dim vectors.
# Change this if you swap to a model with a different output size.
EMBEDDING_DIM = 384
