"""
weather_api.py
Implementasi Redis Caching untuk mempercepat API call.

Sesuai Redis Caching Exercise — Pemrograman Sisi Server
Universitas Dian Nuswantoro
"""
import redis
import json
import time

# ─────────────────────────────────────────────────────────────
# Koneksi ke Redis
# ─────────────────────────────────────────────────────────────
r = redis.Redis(
    host='localhost',  # atau 'redis' jika pakai Docker network
    port=6379,
    db=0,
    decode_responses=True  # Agar nilai yang dikembalikan berupa string, bukan bytes
)

# TTL Cache: 5 menit = 300 detik
CACHE_TTL = 300


def _fetch_from_api(city: str) -> dict:
    """
    Simulasi API call yang lambat (2 detik).
    Di dunia nyata ini adalah requests.get ke external API.
    """
    time.sleep(2)  # Simulate slow API (JANGAN dihapus, ini untuk demo!)
    # Simulasi response dari weather API
    weather_data = {
        "city": city,
        "temperature": 28,
        "feels_like": 30,
        "condition": "Sunny",
        "humidity": 75,
        "source": "api"  # Penanda: data dari API (bukan cache)
    }
    return weather_data


def get_weather(city: str) -> dict:
    """
    Mendapatkan data cuaca dengan Redis Cache-Aside Pattern.

    Alur:
    1. Buat cache key dari nama kota
    2. Cek cache → jika ada (cache HIT), langsung return
    3. Jika tidak ada (cache MISS) → call API (lambat)
    4. Simpan hasil ke Redis dengan TTL 300 detik
    5. Return hasil

    Args:
        city: Nama kota yang ingin dicek cuacanya

    Returns:
        dict: Data cuaca (temperature, condition, dll)
    """
    # ── Langkah 1: Buat cache key ────────────────────────────
    # Gunakan nama kota sebagai bagian key, lowercase untuk konsistensi
    cache_key = f"weather:{city.lower()}"

    # ── Langkah 2: Cek cache dulu ────────────────────────────
    cached_data = r.get(cache_key)

    if cached_data is not None:
        # ✅ CACHE HIT — data ditemukan di Redis
        print(f"[CACHE HIT] '{city}' — data dari Redis (cepat!)")
        result = json.loads(cached_data)
        result["source"] = "cache"  # Penanda: data dari cache
        return result

    # ── Langkah 3: Cache MISS — harus call API ───────────────
    print(f"[CACHE MISS] '{city}' — memanggil API... (tunggu 2 detik)")
    weather_data = _fetch_from_api(city)

    # ── Langkah 4: Simpan ke Redis dengan TTL 300 detik ──────
    # json.dumps() mengubah dict menjadi string JSON untuk disimpan di Redis
    r.set(cache_key, json.dumps(weather_data), ex=CACHE_TTL)
    print(f"[CACHE SET] Data '{city}' disimpan di Redis (TTL: {CACHE_TTL}s)")

    # ── Langkah 5: Return hasil ───────────────────────────────
    return weather_data


def get_cache_info(city: str) -> dict:
    """
    Mendapatkan informasi cache untuk sebuah kota.
    Berguna untuk debugging dan dokumentasi.
    """
    cache_key = f"weather:{city.lower()}"
    ttl = r.ttl(cache_key)
    exists = r.exists(cache_key)

    return {
        "city": city,
        "cache_key": cache_key,
        "is_cached": bool(exists),
        "ttl_remaining": ttl if ttl > 0 else 0,
    }


def clear_cache(city: str = None) -> str:
    """
    Menghapus cache.
    Jika city=None, hapus semua cache weather.
    """
    if city:
        cache_key = f"weather:{city.lower()}"
        r.delete(cache_key)
        return f"Cache untuk '{city}' dihapus"
    else:
        # Hapus semua key weather:*
        keys = r.keys("weather:*")
        if keys:
            r.delete(*keys)
        return f"{len(keys)} cache entries dihapus"