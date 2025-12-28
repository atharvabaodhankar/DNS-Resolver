import sys
import dns.resolver
import redis

r = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)


def resolve_domain(domain: str):
    cache_key = f"dns:{domain}"

    cached_ip = r.get(cache_key)
    if cached_ip:
        ttl = r.ttl(cache_key)
        print("🟢 CACHE HIT")
        print(f"Domain: {domain}")
        print(f"IP: {cached_ip}")
        print(f"TTL: {ttl}")
        return

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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python server.py <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    resolve_domain(domain)
