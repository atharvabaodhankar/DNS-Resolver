import dns.resolver

def resolve_domain(domain):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["8.8.8.8"]  # Google DNS

    answer = resolver.resolve(domain, "A")

    print(f"Domain: {domain}")
    for rdata in answer:
        print(f"IP: {rdata}")
    
    print(f"TTL: {answer.rrset.ttl}")


if __name__ == "__main__":
    resolve_domain("google.com")
