"""Test a raw httpx POST to chat/completions (bypassing the OpenAI SDK)."""
import time, httpx
from dotenv import dotenv_values

key = dotenv_values(".env")["NVIDIA_API_KEY"]
URL = "https://integrate.api.nvidia.com/v1/chat/completions"
payload = {
    "model": "meta/llama-3.3-70b-instruct",
    "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
    "max_tokens": 5, "temperature": 0.0,
}
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

print("Raw httpx POST /v1/chat/completions (30s timeout)...")
t = time.perf_counter()
try:
    r = httpx.post(URL, json=payload, headers=headers, timeout=30)
    dt = time.perf_counter() - t
    print(f"  HTTP {r.status_code} in {dt:.2f}s")
    if r.status_code == 200:
        print("  ✅ reply:", r.json()["choices"][0]["message"]["content"].strip())
        print("  → The endpoint + POST work fine. Problem is INSIDE the OpenAI SDK.")
    else:
        print("  body:", r.text[:500])
        print("  → Endpoint rejected the request; the error above is the real cause.")
except Exception as e:
    print(f"  ❌ FAILED after {time.perf_counter()-t:.2f}s: {type(e).__name__}: {e}")
    print("  → Even raw POST hangs; likely a network middlebox blocking POST bodies.")
