import dns.resolver
import redis

# Redis connection
r = redis.Redis(host="localhost", port=6379, decode_responses=True)


def resolve_domain(domain: str):
    cache_key = f"dns:{domain}"

    # 1️⃣ Check cache
    cached_ip = r.get(cache_key)
    if cached_ip:
        ttl = r.ttl(cache_key)
        print("🟢 CACHE HIT")
        print(f"Domain: {domain}")
        print(f"IP: {cached_ip}")
        print(f"TTL: {ttl}")
        return

    print("🟡 CACHE MISS")

    # 2️⃣ Query upstream DNS
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["8.8.8.8"]

    answer = resolver.resolve(domain, "A")
    ip = answer[0].to_text()
    ttl = answer.rrset.ttl

    # 3️⃣ Store in Redis with TTL
    r.setex(cache_key, ttl, ip)

    print(f"Domain: {domain}")
    print(f"IP: {ip}")
    print(f"TTL: {ttl}")


if __name__ == "__main__":
    resolve_domain("google.com")
