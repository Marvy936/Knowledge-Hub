# Praktický sieťový projekt od namespace po HTTPS request

Predchádzajúce kapitoly sledovali Atlas request po jednotlivých mechanizmoch. Teraz ich spojíme do jedného Linux labu. Na jednom hoste vytvoríme päť network namespaces, dve Ethernet broadcast domény, DNS resolver, edge router s DNAT a firewallom, TLS termination, HAProxy load balancing a dva HTTP backendy.

Lab je určený pre izolovaný Linux host alebo VM. Mení network namespaces, bridges a nftables iba v namespace `net-edge`, no stále vyžaduje `root`. Pred spustením skontroluj, že názvy `net-client`, `net-dns`, `net-edge`, `net-app1`, `net-app2`, `br-atlas-client` a `br-atlas-app` nepoužíva iný experiment.

## 1. Výsledná topológia

```text
net-client
10.24.8.37/24
    |
    | br-atlas-client
    |
net-dns 10.24.8.53       net-edge 10.24.8.1
dnsmasq                         |
api.atlas.test                  | DNAT
→ 203.0.113.40                  | 203.0.113.40:443
                                → 10.50.0.10:443
                                HAProxy + TLS
                                |
                                | br-atlas-app
                    ┌───────────┴───────────┐
                    |                       |
             net-app1                 net-app2
             10.60.1.21:8080          10.60.1.22:8080
```

Klient používa DNS, nie `--resolve`. Packet na public VIP sa routuje k edge namespace-u. DNAT ho preloží na lokálny TLS listener. HAProxy vytvorí nové upstream TCP spojenie k jednému z backendov.

Tým vzniknú tri odlišné identity:

```text
DNS answer: api.atlas.test → 203.0.113.40

client flow:
10.24.8.37:<ephemeral> → 203.0.113.40:443

po DNAT:
10.24.8.37:<ephemeral> → 10.50.0.10:443

proxy upstream:
10.60.1.1:<ephemeral> → 10.60.1.21|22:8080
```

## 2. Predpoklady a adresár

Lab potrebuje Linux kernel s network namespaces, veth, bridge a nftables podporou. Príkazy `ip netns`, `ip link` a `nft` menia kernelový network state a vyžadujú `root` alebo ekvivalentné capabilities; nejde iba o inštaláciu CLI balíkov. Lab preto patrí do izolovanej VM alebo disposable hosta, nie na produkčný router ani na workstation s nezdokumentovanými namespaces.

Pred prvým spustením sa skontroluje, že mená všetkých namespaces, bridges a `/etc/netns/net-client` nepatria inému experimentu. `cleanup.sh` vlastní iba explicitne pomenované resources. Úspešný package install preukazuje dostupnosť binaries, nie kernel features, permissions ani to, že porty a mená nie sú obsadené. Tieto predpoklady overí až setup preflight a následný runtime read-back.

Na Debian/Ubuntu systéme možno nástroje pripraviť:

```bash
sudo apt-get update
sudo apt-get install -y \
  iproute2 iputils-ping nftables dnsmasq haproxy openssl \
  curl tcpdump jq python3
```

Vytvor projekt:

```bash
mkdir -p atlas-network-lab/{pki,run,logs}
cd atlas-network-lab
```

Výsledná štruktúra bude:

```text
atlas-network-lab/
├── orders_api.py
├── dnsmasq.conf
├── haproxy.cfg.template
├── setup.sh
├── verify.sh
├── break-backend.sh
├── recover-backend.sh
├── break-firewall.sh
├── recover-firewall.sh
├── cleanup.sh
├── pki/
├── run/
└── logs/
```

Súbory `orders_api.py`, `dnsmasq.conf`, `haproxy.cfg.template` a shell skripty sú versionovateľný source labu. Adresár `run/` obsahuje generated effective configuration a PID references pre aktuálne spustenie; `logs/` obsahuje runtime evidence. PID file sám nepreukazuje živý ani správny process a generated HAProxy config nepreukazuje, že ho worker načítal. Preto sa po setup-e kontrolujú namespaces, listeners, process command lines, effective nftables ruleset a reálny HTTPS request.

## 3. Backend aplikácia

Vytvor `orders_api.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import ClassVar


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    seen: ClassVar[dict[str, dict[str, str]]] = {}

    def send_json(self, status: int, payload: dict[str, str]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path in {"/healthz", "/readyz"}:
            self.send_json(200, {
                "status": "ok",
                "backend": os.environ["BACKEND"],
            })
            return
        self.send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/v1/orders":
            self.send_json(404, {"error": "not_found"})
            return

        if os.getenv("FAIL_POST") == "1":
            self.send_json(503, {
                "error": "business_path_unavailable",
                "backend": os.environ["BACKEND"],
            })
            return

        key = self.headers.get("Idempotency-Key")
        if not key:
            self.send_json(400, {"error": "missing_idempotency_key"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(400, {"error": "invalid_json"})
            return

        request_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

        existing = self.seen.get(key)
        if existing and existing["requestHash"] != request_hash:
            self.send_json(409, {"error": "idempotency_conflict"})
            return

        if existing is None:
            order_id = "ord-" + hashlib.sha256(key.encode()).hexdigest()[:8]
            existing = {
                "orderId": order_id,
                "requestHash": request_hash,
                "backend": os.environ["BACKEND"],
            }
            self.seen[key] = existing

        self.send_json(201, {
            "orderId": existing["orderId"],
            "backend": existing["backend"],
            "requestHash": existing["requestHash"],
        })

    def log_message(self, fmt: str, *args: object) -> None:
        print(
            json.dumps({
                "backend": os.environ["BACKEND"],
                "client": self.client_address[0],
                "message": fmt % args,
            }),
            flush=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", required=True)
    args = parser.parse_args()
    host, port = args.bind.rsplit(":", 1)
    ThreadingHTTPServer((host, int(port)), Handler).serve_forever()


if __name__ == "__main__":
    main()
```

Aplikácia má plytké `/healthz` a `/readyz` endpointy a business `POST /v1/orders`. Premenná `FAIL_POST=1` zámerne vytvorí stav, pri ktorom health zostane zelený, ale business request zlyhá. To bude prvý failure walkthrough.

Idempotency store je iba process-local memory. Lab ním demonštruje contract jedného backendu, nie production-grade distribuovanú deduplikáciu. V reálnom load-balanced systéme musí operation record zdieľať celý backend pool.

## 4. DNS konfigurácia

Vytvor `dnsmasq.conf`:

```ini
no-resolv
no-hosts
bind-interfaces
listen-address=10.24.8.53
address=/api.atlas.test/203.0.113.40
log-queries
log-facility=-
```

Resolver odpovedá iba na lab hostname. `api.atlas.test` používa reserved `.test` suffix a dokumentačný VIP. `no-resolv` zabráni tomu, aby lab náhodne forwardoval ďalšie queries do hostiteľskej siete.

## 5. HAProxy konfigurácia

Vytvor `haproxy.cfg.template`:

```haproxy
global
    log stdout format raw local0
    maxconn 256

defaults
    log global
    mode http
    option httplog
    timeout connect 2s
    timeout client 10s
    timeout server 10s

frontend atlas_https
    bind 10.50.0.10:443 ssl crt __ROOT__/pki/server.pem
    http-request set-header X-Forwarded-Proto https
    http-request set-header X-Forwarded-For %[src]
    default_backend orders

backend orders
    balance roundrobin
    option httpchk GET /readyz
    http-check expect status 200
    server app1 10.60.1.21:8080 check inter 500ms fall 2 rise 2
    server app2 10.60.1.22:8080 check inter 500ms fall 2 rise 2
```

`__ROOT__` sa pri setup-e nahradí absolútnou cestou. Health check kontroluje iba readiness endpoint. Zámerne nepozná business `POST`, takže prvý failure ukáže hranicu zeleného health dôkazu.

## 6. Setup skript

Vytvor `setup.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
RUN="$ROOT/run"
LOGS="$ROOT/logs"
PKI="$ROOT/pki"

namespaces=(net-client net-dns net-edge net-app1 net-app2)
bridges=(br-atlas-client br-atlas-app)
required=(ip ping nft dnsmasq haproxy openssl curl tcpdump jq python3)

if ((EUID != 0)); then
  echo "Run as root: sudo ./setup.sh" >&2
  exit 1
fi

for command in "${required[@]}"; do
  command -v "$command" >/dev/null || {
    echo "Missing required command: $command" >&2
    exit 1
  }
done

"$ROOT/cleanup.sh" --quiet || true
mkdir -p "$RUN" "$LOGS" "$PKI"

for ns in "${namespaces[@]}"; do
  ip netns add "$ns"
  ip -n "$ns" link set lo up
done

ip link add br-atlas-client type bridge
ip link add br-atlas-app type bridge
ip link set br-atlas-client up
ip link set br-atlas-app up

connect_ns() {
  local ns=$1
  local host_if=$2
  local ns_if=$3
  local bridge=$4

  ip link add "$host_if" type veth peer name "$ns_if"
  ip link set "$ns_if" netns "$ns"
  ip link set "$host_if" master "$bridge"
  ip link set "$host_if" up
  ip -n "$ns" link set "$ns_if" up
}

connect_ns net-client v-client client0 br-atlas-client
connect_ns net-dns    v-dns    dns0    br-atlas-client
connect_ns net-edge   v-edge-c edge0   br-atlas-client
connect_ns net-edge   v-edge-a edge1   br-atlas-app
connect_ns net-app1   v-app1   app0    br-atlas-app
connect_ns net-app2   v-app2   app0    br-atlas-app

ip -n net-client addr add 10.24.8.37/24 dev client0
ip -n net-dns    addr add 10.24.8.53/24 dev dns0
ip -n net-edge   addr add 10.24.8.1/24  dev edge0

ip -n net-edge addr add 10.60.1.1/24  dev edge1
ip -n net-app1 addr add 10.60.1.21/24 dev app0
ip -n net-app2 addr add 10.60.1.22/24 dev app0

ip -n net-edge addr add 10.50.0.10/32 dev lo
ip -n net-edge addr add 203.0.113.40/32 dev lo

ip -n net-client route add default via 10.24.8.1
ip -n net-app1 route add default via 10.60.1.1
ip -n net-app2 route add default via 10.60.1.1

mkdir -p /etc/netns/net-client
printf 'nameserver 10.24.8.53\noptions timeout:1 attempts:1\n' \
  > /etc/netns/net-client/resolv.conf

if [[ ! -s "$PKI/ca.crt" ]]; then
  openssl req -x509 -newkey rsa:2048 -nodes \
    -keyout "$PKI/ca.key" \
    -out "$PKI/ca.crt" \
    -subj "/CN=Atlas Network Lab CA" \
    -days 7

  openssl req -newkey rsa:2048 -nodes \
    -keyout "$PKI/server.key" \
    -out "$PKI/server.csr" \
    -subj "/CN=api.atlas.test"

  cat >"$PKI/server.ext" <<'EOF'
subjectAltName=DNS:api.atlas.test
extendedKeyUsage=serverAuth
keyUsage=digitalSignature,keyEncipherment
EOF

  openssl x509 -req \
    -in "$PKI/server.csr" \
    -CA "$PKI/ca.crt" \
    -CAkey "$PKI/ca.key" \
    -CAcreateserial \
    -out "$PKI/server.crt" \
    -days 7 \
    -sha256 \
    -extfile "$PKI/server.ext"
fi

cat "$PKI/server.crt" "$PKI/server.key" >"$PKI/server.pem"
chmod 600 "$PKI/ca.key" "$PKI/server.key" "$PKI/server.pem"

sed "s|__ROOT__|$ROOT|g" \
  "$ROOT/haproxy.cfg.template" >"$RUN/haproxy.cfg"

ip netns exec net-edge nft -f - <<'EOF'
table inet atlas_filter {
  chain prerouting {
    type nat hook prerouting priority dstnat; policy accept;
    ip daddr 203.0.113.40 tcp dport 443 dnat to 10.50.0.10:443
  }

  chain input {
    type filter hook input priority filter; policy drop;
    iifname "lo" accept
    ct state established,related accept
    ip protocol icmp accept
    iifname "edge0" ip saddr 10.24.8.0/24 \
      ip daddr 10.50.0.10 tcp dport 443 ct state new accept
  }

  chain forward {
    type filter hook forward priority filter; policy drop;
    ct state established,related accept
  }

  chain output {
    type filter hook output priority filter; policy accept;
  }
}
EOF

nohup ip netns exec net-dns \
  dnsmasq --no-daemon --conf-file="$ROOT/dnsmasq.conf" \
  >"$LOGS/dnsmasq.log" 2>&1 &
echo $! >"$RUN/dnsmasq.pid"

nohup ip netns exec net-app1 \
  env BACKEND=app1 python3 "$ROOT/orders_api.py" \
  --bind 10.60.1.21:8080 \
  >"$LOGS/app1.log" 2>&1 &
echo $! >"$RUN/app1.pid"

nohup ip netns exec net-app2 \
  env BACKEND=app2 python3 "$ROOT/orders_api.py" \
  --bind 10.60.1.22:8080 \
  >"$LOGS/app2.log" 2>&1 &
echo $! >"$RUN/app2.pid"

nohup ip netns exec net-edge \
  haproxy -f "$RUN/haproxy.cfg" \
  >"$LOGS/haproxy.log" 2>&1 &
echo $! >"$RUN/haproxy.pid"

sleep 2
"$ROOT/verify.sh"
```

Všimni si poradie firewallu. DNAT sa vykoná v `prerouting`, takže `input` rule už vidí destination `10.50.0.10`, nie public VIP. Práve túto hranicu neskôr zámerne pokazíme.

## 7. Verification script

Vytvor `verify.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
CA="$ROOT/pki/ca.crt"
URL=https://api.atlas.test/v1/orders

run_client() {
  ip netns exec net-client "$@"
}

echo "== DNS =="
answer=$(run_client getent ahostsv4 api.atlas.test | awk 'NR==1 {print $1}')
[[ "$answer" == "203.0.113.40" ]] || {
  echo "Unexpected DNS answer: $answer" >&2
  exit 1
}

echo "== Route =="
run_client ip route get 203.0.113.40

echo "== Neighbor =="
run_client ping -c 1 -W 1 10.24.8.1 >/dev/null
run_client ip neigh show 10.24.8.1

echo "== TLS identity =="
run_client curl --noproxy '*' --silent --show-error \
  --cacert "$CA" \
  https://api.atlas.test/healthz | jq -e '.status == "ok"' >/dev/null

echo "== Forbidden direct backend path =="
if run_client curl --noproxy '*' --silent --show-error \
  --connect-timeout 1 --max-time 2 \
  http://10.60.1.21:8080/healthz >/dev/null; then
  echo "Direct client-to-backend path must remain blocked" >&2
  exit 1
fi

echo "== Two business requests =="
declare -A backends=()

for key in lab-1001 lab-1002; do
  response=$(
    run_client curl --noproxy '*' --silent --show-error \
      --cacert "$CA" \
      --header 'Content-Type: application/json' \
      --header "Idempotency-Key: $key" \
      --data '{"customerId":"cus-742","currency":"EUR","amount":"59.90"}' \
      "$URL"
  )
  echo "$response" | jq .
  backend=$(jq -r '.backend' <<<"$response")
  backends["$backend"]=1
done

[[ ${#backends[@]} -eq 2 ]] || {
  echo "Expected both backends, got: ${!backends[*]}" >&2
  exit 1
}

echo "Verification passed"
```

Skript overuje DNS, route, neighbor resolution, TLS identity, zakázaný direct-backend path a business response. `jq -e` vracia non-zero, ak JSON podmienka neplatí; v kombinácii so `set -Eeuo pipefail` tak zlyhá celý verification, nie iba posledný formatter. Negatívny `curl` je zámerne vložený do `if`, takže očakávaný non-zero exit status neukončí skript, ale úspešné priame spojenie sa zmení na explicitný failure.

Dva business requests očakávajú oba round-robin backends. To je deterministický oracle iba v čistom lab-e bez ďalších connections, retries alebo HTTP/2 multiplexingu. Production test má zbierať backend identity cez dostatočnú vzorku a nesmie predpokladať presné poradie assignmentu. Zelený verification tiež nepreukazuje distribuovanú idempotency, pretože ukážkový store je process-local.

## 8. Cleanup

Vytvor `cleanup.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
quiet=false
[[ ${1:-} == "--quiet" ]] && quiet=true

if ((EUID != 0)); then
  echo "Run as root: sudo ./cleanup.sh" >&2
  exit 1
fi

for pid_file in "$ROOT"/run/*.pid; do
  [[ -e "$pid_file" ]] || continue
  pid=$(cat "$pid_file")
  kill "$pid" 2>/dev/null || true
done

sleep 0.2

for ns in net-client net-dns net-edge net-app1 net-app2; do
  ip netns del "$ns" 2>/dev/null || true
done

ip link del br-atlas-client 2>/dev/null || true
ip link del br-atlas-app 2>/dev/null || true
rm -rf /etc/netns/net-client
rm -f "$ROOT"/run/*.pid "$ROOT"/run/haproxy.cfg

$quiet || echo "Lab removed"
```

Cleanup používa `|| true`, aby zostal opakovateľný aj po partial setup-e. Text `Lab removed` preto oznamuje dokončenie pokusov, nie dokázanú absenciu každého resource-u. Po cleanup-e sa vykoná read-back:

```bash
ip netns list | grep -E '^(net-client|net-dns|net-edge|net-app1|net-app2)( |$)' && exit 1 || true
ip -brief link | grep -E 'br-atlas-(client|app)' && exit 1 || true
pgrep -af 'dnsmasq|orders_api.py|haproxy' || true
test ! -e /etc/netns/net-client/resolv.conf
```

Prvé dva commands musia nemať match. `pgrep` je iba investigation hint, pretože host môže legitímne prevádzkovať iný dnsmasq alebo HAProxy; PID a command line sa porovnajú s files v `run/`. Ak zostal lab process alebo namespace, cleanup nie je úspešný a ďalší setup by mohol pracovať so stale state-om.

Nastav executable bits:

```bash
chmod +x \
  orders_api.py setup.sh verify.sh cleanup.sh \
  break-backend.sh recover-backend.sh \
  break-firewall.sh recover-firewall.sh
```

## 9. Spustenie a read-back

Spusť:

```bash
sudo ./setup.sh
```

Potom čítaj state po vrstvách:

```bash
sudo ip netns exec net-client getent ahostsv4 api.atlas.test
sudo ip netns exec net-client ip route get 203.0.113.40
sudo ip netns exec net-client ip neigh
sudo ip netns exec net-edge nft -a list ruleset
sudo ip netns exec net-edge ss -lntp
sudo ip netns exec net-app1 ss -lntp
sudo ip netns exec net-app2 ss -lntp
```

TLS:

```bash
sudo ip netns exec net-client \
  openssl s_client \
    -connect api.atlas.test:443 \
    -servername api.atlas.test \
    -CAfile "$PWD/pki/ca.crt" \
    -verify_return_error </dev/null
```

HAProxy a backend logs:

```bash
tail -f logs/haproxy.log logs/app1.log logs/app2.log
```

Každý výstup dokazuje inú vrstvu. DNS answer nepreukazuje route, listener nepreukazuje firewall, TLS verify nepreukazuje business POST a backend log nepreukazuje client response.

## 10. Packet capture cez dva flowy

Spusť captures v dvoch termináloch:

```bash
sudo ip netns exec net-client \
  tcpdump -ni client0 -vv 'host 203.0.113.40 and tcp port 443'
```

```bash
sudo ip netns exec net-edge \
  tcpdump -ni edge1 -vv 'tcp port 8080'
```

Potom vykonaj request:

```bash
sudo ip netns exec net-client \
  curl --noproxy '*' --silent --show-error \
    --cacert "$PWD/pki/ca.crt" \
    -H 'Content-Type: application/json' \
    -H 'Idempotency-Key: capture-1001' \
    --data '{"customerId":"cus-742","currency":"EUR","amount":"59.90"}' \
    https://api.atlas.test/v1/orders | jq .
```

Prvý capture ukáže client-to-edge TLS flow. Druhý ukáže proxy-to-backend plaintext HTTP flow. Nie je možné korelovať ich iba podľa transportného tuple; použiteľná korelácia potrebuje request ID alebo proxy log.

## 11. Failure 1: zelený health, chybný business backend

Vytvor `break-backend.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

pid=$(cat "$ROOT/run/app2.pid")
kill "$pid"
wait "$pid" 2>/dev/null || true

nohup ip netns exec net-app2 \
  env BACKEND=app2 FAIL_POST=1 python3 "$ROOT/orders_api.py" \
  --bind 10.60.1.22:8080 \
  >"$ROOT/logs/app2.log" 2>&1 &
echo $! >"$ROOT/run/app2.pid"

sleep 2
```

Vytvor `recover-backend.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

pid=$(cat "$ROOT/run/app2.pid")
kill "$pid"
wait "$pid" 2>/dev/null || true

nohup ip netns exec net-app2 \
  env BACKEND=app2 python3 "$ROOT/orders_api.py" \
  --bind 10.60.1.22:8080 \
  >"$ROOT/logs/app2.log" 2>&1 &
echo $! >"$ROOT/run/app2.pid"

sleep 2
"$ROOT/verify.sh"
```

Aktivuj poruchu:

```bash
sudo ./break-backend.sh
```

HAProxy health zostane zelený:

```bash
sudo ip netns exec net-client \
  curl --noproxy '*' --cacert "$PWD/pki/ca.crt" \
  --silent https://api.atlas.test/healthz | jq .
```

Opakované business requests však budú striedať `201` a `503`:

```bash
for n in 1 2 3 4; do
  sudo ip netns exec net-client \
    curl --noproxy '*' --silent \
      --cacert "$PWD/pki/ca.crt" \
      -H 'Content-Type: application/json' \
      -H "Idempotency-Key: broken-$n" \
      --data '{"customerId":"cus-742","currency":"EUR","amount":"59.90"}' \
      https://api.atlas.test/v1/orders
  echo
done
```

Competing hypotheses zahŕňajú client issue, LB algorithm, jeden backend alebo proxy retry. HAProxy log ukáže pravidelnú väzbu `503 → app2`. Backend health endpoint nepozoruje business path, preto ho treba doplniť o loaded configuration alebo bounded dependency signal a business synthetic mimo load-balancer health loopu.

Obnov:

```bash
sudo ./recover-backend.sh
```

## 12. Failure 2: allow rule na nesprávnej NAT identite

Vytvor `break-firewall.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

ip netns exec net-edge nft flush chain inet atlas_filter input

ip netns exec net-edge nft add rule inet atlas_filter input \
  iifname lo accept
ip netns exec net-edge nft add rule inet atlas_filter input \
  ct state established,related accept
ip netns exec net-edge nft add rule inet atlas_filter input \
  ip protocol icmp accept

# Zámerná chyba: po prerouting DNAT už input chain nevidí public VIP.
ip netns exec net-edge nft add rule inet atlas_filter input \
  iifname edge0 ip saddr 10.24.8.0/24 \
  ip daddr 203.0.113.40 tcp dport 443 ct state new accept
```

Vytvor `recover-firewall.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

ip netns exec net-edge nft flush chain inet atlas_filter input

ip netns exec net-edge nft add rule inet atlas_filter input \
  iifname lo accept
ip netns exec net-edge nft add rule inet atlas_filter input \
  ct state established,related accept
ip netns exec net-edge nft add rule inet atlas_filter input \
  ip protocol icmp accept
ip netns exec net-edge nft add rule inet atlas_filter input \
  iifname edge0 ip saddr 10.24.8.0/24 \
  ip daddr 10.50.0.10 tcp dport 443 ct state new accept

"$ROOT/verify.sh"
```

Aktivuj chybu:

```bash
sudo ./break-firewall.sh
```

Request timeoutuje. Counter na zlom rule zostane nulový:

```bash
sudo ip netns exec net-edge nft -a list chain inet atlas_filter input
```

Trace ukáže translated destination:

```bash
sudo ip netns exec net-edge nft monitor trace
```

V druhom termináli spusti jeden request s krátkym timeoutom:

```bash
sudo ip netns exec net-client \
  curl --noproxy '*' --connect-timeout 2 \
    --cacert "$PWD/pki/ca.crt" \
    https://api.atlas.test/healthz
```

Capture na `edge0` ukáže SYN na public VIP pri vstupe, no filter hook po DNAT rozhoduje nad `10.50.0.10`. Oprava nie je pridať ďalší široký allow, ale použiť správny packet identity a hook:

```bash
sudo ./recover-firewall.sh
```

## 13. Cleanup a acceptance

Po skončení:

```bash
sudo ./cleanup.sh
```

Acceptance labu zahŕňa viac než zelený `verify.sh`:

- **Source a resolved state:** DNS odpoveď pochádza z `net-dns`, route smeruje VIP cez `10.24.8.1` a neighbor mapping patrí edge namespace-u. Každý read-back sa vykonáva v rovnakom namespace ako klient.
- **Dataplane transition:** capture a nftables trace ukážu DNAT z `203.0.113.40:443` na `10.50.0.10:443`. Firewall povoľuje client-to-proxy path, ale nový forbidden test potvrdí, že client nemôže volať `10.60.1.21:8080` priamo.
- **TLS a application outcome:** certifikát platí pre `api.atlas.test`; business POST vráti `orderId`, request hash a backend identity. Dve operácie prejdú cez oba healthy backends bez tvrdenia, že jeden HTTP status sám dokazuje celý pool.
- **Failure discrimination:** broken `app2` sa koreluje s `503` pri stále zelenom health endpoint-e. Nesprávne firewall rule má po DNAT nulový match a trace ukáže skutočnú translated identity.
- **Recovery a second run:** oba recovery skripty spustia celý `verify.sh`. Po recovery sa verification vykoná ešte raz bez opätovného setup-u; tým sa testuje ďalšia operácia nad existujúcim state-om a odhalí jednorazový alebo stale-connection úspech.
- **Cleanup closure:** po `cleanup.sh` read-back nepotvrdí žiadny vlastnený namespace, bridge, PID ani resolver file. Až táto absencia uzatvára lab lifecycle.

Lab nepreukazuje production capacity, HA, DNSSEC, internet routing, certificate revocation ani distribuovanú idempotency. Jeho účelom je urobiť jednotlivé network identities a observation points viditeľné na jednom hoste a nacvičiť positive, forbidden, failure, recovery a second-operation paths.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: REST API a WebSockety](rest-apis-and-websockets.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Network troubleshooting →](network-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
