import sys
import dns.resolver
import redis

r = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)

SUPPORTED_TYPES = {"A", "AAAA", "CNAME"}

RATE_LIMIT = 5      # max requests
WINDOW = 10         # seconds

# ---------------- METRICS ----------------

def incr_metric(name: str):
    r.incr(f"dns:metrics:{name}")

def get_metrics():
    total = r.get("dns:metrics:total") or 0
    hit = r.get("dns:metrics:hit") or 0
    miss = r.get("dns:metrics:miss") or 0
    blocked = r.get("dns:metrics:blocked") or 0

    print("📊 DNS Cache Metrics")
    print("-------------------")
    print(f"Total Queries : {total}")
    print(f"Cache Hits    : {hit}")
    print(f"Cache Misses : {miss}")
    print(f"Rate Blocked : {blocked}")

# ---------------- RATE LIMITING ----------------

def is_rate_limited(domain: str) -> bool:
    key = f"dns:rate:{domain}"

    count = r.incr(key)
    if count == 1:
        r.expire(key, WINDOW)

    if count > RATE_LIMIT:
        incr_metric("blocked")
        ttl = r.ttl(key)
        print(f"🚫 RATE LIMITED (retry in {ttl}s)")
        return True

    return False

# ---------------- DNS LOGIC ----------------

def resolve_domain(domain: str, record_type: str):
    record_type = record_type.upper()

    if record_type not in SUPPORTED_TYPES:
        print(f"❌ Unsupported record type: {record_type}")
        return

    incr_metric("total")

    # 🔒 Rate limit check
    if is_rate_limited(domain):
        return

    cache_key = f"dns:{domain}:{record_type}"

    cached_value = r.get(cache_key)
    if cached_value:
        incr_metric("hit")
        ttl = r.ttl(cache_key)
        print("🟢 CACHE HIT")
        print(f"Domain : {domain}")
        print(f"Type   : {record_type}")
        print(f"Value  : {cached_value}")
        print(f"TTL    : {ttl}")
        return

    incr_metric("miss")
    print("🟡 CACHE MISS")

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["8.8.8.8"]

    try:
        answer = resolver.resolve(domain, record_type)
    except Exception as e:
        print(f"❌ DNS lookup failed: {e}")
        return

    value = answer[0].to_text()
    ttl = answer.rrset.ttl

    r.setex(cache_key, ttl, value)

    print(f"Domain : {domain}")
    print(f"Type   : {record_type}")
    print(f"Value  : {value}")
    print(f"TTL    : {ttl}")

# ---------------- ENTRYPOINT ----------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Resolve domain:")
        print("    docker compose run resolver <domain> [A|AAAA|CNAME]")
        print("  View metrics:")
        print("    docker compose run resolver stats")
        sys.exit(1)

    if sys.argv[1] == "stats":
        get_metrics()
        sys.exit(0)

    domain = sys.argv[1]
    record_type = sys.argv[2] if len(sys.argv) > 2 else "A"

    resolve_domain(domain, record_type)
