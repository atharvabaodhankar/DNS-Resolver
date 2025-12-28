import sys
import dns.resolver
import redis

r = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)

# ---------------- METRICS ----------------

def incr_metric(name: str):
    r.incr(f"dns:metrics:{name}")

def get_metrics():
    total = r.get("dns:metrics:total") or 0
    hit = r.get("dns:metrics:hit") or 0
    miss = r.get("dns:metrics:miss") or 0

    print("📊 DNS Cache Metrics")
    print("-------------------")
    print(f"Total Queries : {total}")
    print(f"Cache Hits    : {hit}")
    print(f"Cache Misses : {miss}")

# ---------------- DNS LOGIC ----------------

def resolve_domain(domain: str):
    incr_metric("total")
    cache_key = f"dns:{domain}"

    cached_ip = r.get(cache_key)
    if cached_ip:
        incr_metric("hit")
        ttl = r.ttl(cache_key)
        print("🟢 CACHE HIT")
        print(f"Domain: {domain}")
        print(f"IP: {cached_ip}")
        print(f"TTL: {ttl}")
        return

    incr_metric("miss")
    print("🟡 CACHE MISS")

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["8.8.8.8"]

    answer = resolver.resolve(domain, "A")
    ip = answer[0].to_text()
    ttl = answer.rrset.ttl

    r.setex(cache_key, ttl, ip)

    print(f"Domain: {domain}")
    print(f"IP: {ip}")
    print(f"TTL: {ttl}")

# ---------------- ENTRYPOINT ----------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  resolve domain : docker compose run resolver google.com")
        print("  view metrics   : docker compose run resolver stats")
        sys.exit(1)

    command = sys.argv[1]

    if command == "stats":
        get_metrics()
    else:
        resolve_domain(command)
