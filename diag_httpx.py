"""Isolate whether the hang is httpx transport (likely IPv6) vs the OpenAI SDK."""
import socket, time
from dotenv import dotenv_values

HOST = "integrate.api.nvidia.com"
key = dotenv_values(".env")["NVIDIA_API_KEY"]

# 1) What addresses does this host resolve to? IPv6 present?
print("① DNS resolution:")
for fam, *_rest, sockaddr in socket.getaddrinfo(HOST, 443):
    kind = "IPv6" if fam == socket.AF_INET6 else "IPv4" if fam == socket.AF_INET else str(fam)
    print(f"   {kind}: {sockaddr[0]}")

# 2) Raw httpx GET to the SAME endpoint curl hit successfully.
print("\n② httpx GET /v1/models (15s timeout)...")
import httpx
t = time.perf_counter()
try:
    r = httpx.get(f"https://{HOST}/v1/models",
                  headers={"Authorization": f"Bearer {key}"}, timeout=15)
    print(f"   ✅ httpx OK: HTTP {r.status_code} in {time.perf_counter()-t:.2f}s")
    print("   → httpx transport is FINE; problem is elsewhere in the SDK call.")
except Exception as e:
    print(f"   ❌ httpx FAILED after {time.perf_counter()-t:.2f}s: {type(e).__name__}: {e}")
    print("   → confirms httpx transport hang (IPv6 is the usual cause).")
