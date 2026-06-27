import os
import oracledb
import anyio
import threading
from dotenv import load_dotenv

# Monkey patch for compatibility between newer anyio and LiteLLM/OracleAgentMemory
if not hasattr(anyio, 'from_thread'):
    class DummyFromThread:
        pass
    anyio.from_thread = DummyFromThread()
if not hasattr(anyio.from_thread, 'current_thread'):
    anyio.from_thread.current_thread = threading.current_thread

from oracleagentmemory.apis.searchscope import SearchScope
from oracleagentmemory.core import OracleAgentMemory
from oracleagentmemory.core.embedders.embedder import Embedder
from oracleagentmemory.core.llms.llm import Llm

load_dotenv()

# Initialize oracledb connection pool using Thin mode
pool = oracledb.create_pool(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    dsn=os.getenv('DB_DSN'),
    config_dir=os.getenv('WALLET_LOCATION', 'wallet'),
    wallet_location=os.getenv('WALLET_LOCATION', 'wallet'),
    wallet_password=os.getenv('DB_PASSWORD'), # The UI prompts for a wallet password; usually kept same as DB password
    min=1,
    max=4,
    increment=1
)

# Use the locally extracted PEM if running in Render, otherwise fall back to the env var path
key_file_path = 'khuzaima.pem' if os.path.exists('khuzaima.pem') else os.getenv('OCI_KEY_FILE')

oci_kwargs = dict(
    oci_user=os.getenv('OCI_USER'), 
    oci_tenancy=os.getenv('OCI_TENANCY'), 
    oci_fingerprint=os.getenv('OCI_FINGERPRINT'),
    oci_key_file=key_file_path, 
    oci_compartment_id=os.getenv('OCI_COMPARTMENT_ID'),
    oci_region=os.getenv('OCI_REGION'),
)

embedder = Embedder(model="oci/cohere.embed-english-v3.0", **oci_kwargs)
llm = Llm(model="oci/cohere.command-r-08-2024", **oci_kwargs)

memory = OracleAgentMemory(
    connection=pool, 
    embedder=embedder, 
    llm=llm,
    schema_policy="create_if_necessary"
)

def setup_memory():
    # Seed the style once (procedural memory)
    thread = memory.create_thread(user_id="casius")
    
    # Check if the memory already exists to avoid duplicates
    results = memory.search(query="STYLE RULE: write my daily briefing", scope=SearchScope(user_id="casius"))
    
    # If no results or very low similarity, seed it
    if not results or results[0].similarity_score < 0.8:
        print("Seeding procedural style memory...")
        thread.add_memory(
          "STYLE RULE: write my daily briefing in my voice. Five top stories. For each: "
          "what happened, why it matters, and one analogy from a different domain. Link "
          "stories to earlier ones when they are follow-ups. British English. No em dashes. "
          "Give a one-line top-line summary of where the day is trending."
        )

# Seed memory when module is loaded
try:
    setup_memory()
except Exception as e:
    print(f"Warning: Failed to seed memory on startup: {e}")
