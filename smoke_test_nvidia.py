"""
Standalone smoke test for the NVIDIA Build migration.
Run:  python3 smoke_test_nvidia.py
Verifies (1) LLM chat, (2) embeddings + correct dimension, (3) input_type handling.
Makes a few tiny API calls (costs a handful of credits). Prints no secrets.
"""
import os
import sys
from dotenv import load_dotenv
import openai

load_dotenv()

BASE_URL = "https://integrate.api.nvidia.com/v1"
GENERATION_MODEL = "meta/llama-3.3-70b-instruct"
EMBEDDING_MODEL = "nvidia/llama-3.2-nv-embedqa-1b-v2"
EXPECTED_DIM = 2048

key = os.getenv("NVIDIA_API_KEY")
if not key or not key.startswith("nvapi-"):
    print("❌ NVIDIA_API_KEY missing or wrong format."); sys.exit(1)

# Short timeout + no retries so a bad request fails loudly instead of hanging.
client = openai.OpenAI(api_key=key, base_url=BASE_URL, timeout=30.0, max_retries=0)

# --- Test 1: LLM chat -------------------------------------------------------
print("① Testing LLM chat (llama-3.3-70b-instruct)...")
try:
    r = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": "Reply with exactly the word: OK"}],
        temperature=0.0, max_tokens=5,
    )
    print(f"   ✅ LLM reply: {r.choices[0].message.content.strip()!r}")
except Exception as e:
    print(f"   ❌ LLM call failed: {type(e).__name__}: {e}"); sys.exit(1)

# --- Test 2: embeddings with input_type via extra_body ----------------------
print("② Testing embeddings with extra_body input_type=passage...")
extra_body_works = False
try:
    r = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=["This is a test contract clause about termination."],
        extra_body={"input_type": "passage", "truncate": "END"},
    )
    dim = len(r.data[0].embedding)
    print(f"   ✅ Embedding returned. dimension = {dim} (expected {EXPECTED_DIM})")
    if dim != EXPECTED_DIM:
        print(f"   ⚠️  DIMENSION MISMATCH — update EMBEDDING_DIMENSION to {dim} in worker.py")
    extra_body_works = True
except Exception as e:
    print(f"   ❌ extra_body approach failed: {type(e).__name__}: {e}")

# --- Test 3: fallback — suffix in model name (only if test 2 failed) --------
if not extra_body_works:
    print("③ Trying FALLBACK: model-name suffix (…-passage)...")
    try:
        r = client.embeddings.create(
            model=EMBEDDING_MODEL + "-passage",
            input=["This is a test contract clause about termination."],
        )
        dim = len(r.data[0].embedding)
        print(f"   ✅ Fallback works. dimension = {dim}")
        print("   ⚠️  ACTION: switch worker.py to the -passage/-query suffix style.")
    except Exception as e:
        print(f"   ❌ Fallback also failed: {type(e).__name__}: {e}"); sys.exit(1)

print("\n🎉 Smoke test complete.")
