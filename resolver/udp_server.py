import socket
import dns.message
import dns.query
import dns.rcode
import redis
import time

REDIS_HOST = "redis"
REDIS_PORT = 6379

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 1053

UPSTREAM_DNS = "8.8.8.8"

RATE_LIMIT = 5
WINDOW = 10  # seconds

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def rate_limited(domain: str) -> bool:
    key = f"dns:rate:{domain}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, WINDOW)
    return count > RATE_LIMIT


def handle_query(data, addr, sock):
    try:
        request = dns.message.from_wire(data)
        question = request.question[0]
        domain = question.name.to_text().rstrip(".")
        qtype = dns.rdatatype.to_text(question.rdtype)

        # Rate limit
        if rate_limited(domain):
            response = dns.message.make_response(request)
            response.set_rcode(dns.rcode.SERVFAIL)
            sock.sendto(response.to_wire(), addr)
            return

        cache_key = f"dns:{domain}:{qtype}"
        cached = r.get(cache_key)

        if cached:
            response = dns.message.make_response(request)
            response.answer = dns.message.from_text(
                f"{domain} 60 IN {qtype} {cached}"
            ).answer
            sock.sendto(response.to_wire(), addr)
            print(f"🟢 CACHE HIT {domain} {qtype}")
            return

        # Forward to upstream DNS
        upstream_response = dns.query.udp(request, UPSTREAM_DNS, timeout=2)

        # Cache first answer if exists
        if upstream_response.answer:
            rrset = upstream_response.answer[0]
            ttl = rrset.ttl
            value = rrset[0].to_text()
            r.setex(cache_key, ttl, value)

        sock.sendto(upstream_response.to_wire(), addr)
        print(f"🟡 CACHE MISS {domain} {qtype}")

    except Exception as e:
        print("❌ Error:", e)


def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))
    print(f"🚀 UDP DNS Server listening on {LISTEN_PORT}")

    while True:
        data, addr = sock.recvfrom(512)
        handle_query(data, addr, sock)


if __name__ == "__main__":
    start_server()
