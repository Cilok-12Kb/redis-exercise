"""
test_cache.py
Testing script untuk membuktikan efektivitas caching.
"""
import time
from weather_api import get_weather, get_cache_info, clear_cache

print("=" * 55)
print("  REDIS CACHING TEST — Simple Weather API")
print("=" * 55)

# ── Bersihkan cache terlebih dahulu ──────────────────────────
clear_cache()
print("\n[SETUP] Cache dibersihkan.\n")

# ── TEST 1: First call — harus lambat (2 detik, dari API) ────
print("─" * 55)
print("TEST 1: First call to Jakarta")
start = time.time()
result1 = get_weather("Jakarta")
time1 = time.time() - start
print(f"  ⏱️  Waktu: {time1:.2f}s")
print(f"  📦 Source: {result1.get('source', 'unknown')}")
print(f"  🌡️  Suhu: {result1['temperature']}°C")

# ── TEST 2: Second call — harus cepat (dari cache) ───────────
print("\n─" * 55)
print("TEST 2: Second call to Jakarta (should be cached)")
start = time.time()
result2 = get_weather("Jakarta")
time2 = time.time() - start
print(f"  ⏱️  Waktu: {time2:.4f}s")
print(f"  📦 Source: {result2.get('source', 'unknown')}")
print(f"  🌡️  Suhu: {result2['temperature']}°C")

# ── TEST 3: Kota berbeda — harus lambat (cache miss) ─────────
print("\n─" * 55)
print("TEST 3: Different city — Surabaya (cache miss)")
start = time.time()
result3 = get_weather("Surabaya")
time3 = time.time() - start
print(f"  ⏱️  Waktu: {time3:.2f}s")
print(f"  📦 Source: {result3.get('source', 'unknown')}")

# ── TEST 4: Surabaya lagi — harus cepat ──────────────────────
print("\n─" * 55)
print("TEST 4: Surabaya again (should be cached now)")
start = time.time()
result4 = get_weather("Surabaya")
time4 = time.time() - start
print(f"  ⏱️  Waktu: {time4:.4f}s")
print(f"  📦 Source: {result4.get('source', 'unknown')}")

# ── Cache Info ────────────────────────────────────────────────
print("\n─" * 55)
print("CACHE INFO:")
info_jkt = get_cache_info("Jakarta")
info_sby = get_cache_info("Surabaya")
print(f"  Jakarta  → cached: {info_jkt['is_cached']}, TTL sisa: {info_jkt['ttl_remaining']}s")
print(f"  Surabaya → cached: {info_sby['is_cached']}, TTL sisa: {info_sby['ttl_remaining']}s")

# ── Ringkasan Perbandingan ────────────────────────────────────
print("\n" + "=" * 55)
print("  RINGKASAN PERBANDINGAN PERFORMA")
print("=" * 55)
print(f"  First call  (API)   : {time1:.2f}s")
print(f"  Second call (cache) : {time2:.4f}s")
speedup = time1 / time2 if time2 > 0 else float('inf')
print(f"  Speedup             : {speedup:.0f}x lebih cepat!")
print()
print("  Third call  (API)   : {:.2f}s (kota baru)".format(time3))
print("  Fourth call (cache) : {:.4f}s (kota sama)".format(time4))
print()
print("  [Catatan] Setelah 5 menit (300 detik), cache expired")
print("  dan request berikutnya akan lambat lagi (call API).")
print("=" * 55)