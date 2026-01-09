set -euo pipefail

TMPDIR=/tmp/mtls_expired
rm -rf "$TMPDIR"
mkdir -p "$TMPDIR/ca/certs" "$TMPDIR/ca/newcerts" "$TMPDIR/ca/private"
: >"$TMPDIR/ca/index.txt"
echo 1000 >"$TMPDIR/ca/serial"

echo "[1/5] Create test CA"
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout "$TMPDIR/ca/private/ca.key" \
  -out "$TMPDIR/ca/certs/ca.pem" \
  -days 365 -subj "/CN=toolb-test-ca" >/dev/null 2>&1

cat >"$TMPDIR/ca/ca.conf" <<'EOF'
[ ca ]
default_ca = CA_default

[ CA_default ]
dir = /tmp/mtls_expired/ca
database = $dir/index.txt
new_certs_dir = $dir/newcerts
certificate = $dir/certs/ca.pem
private_key = $dir/private/ca.key
serial = $dir/serial
default_md = sha256
policy = policy_any
x509_extensions = usr_cert
unique_subject = no

[ policy_any ]
commonName = supplied

[ usr_cert ]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth
EOF

echo "[2/5] Create expired client cert (2000-01-01 to 2000-01-02)"
start="20000101000000Z"
end="20000102000000Z"

openssl req -newkey rsa:2048 -nodes \
  -keyout "$TMPDIR/exp.key" \
  -out "$TMPDIR/exp.csr" \
  -subj "/CN=rogue-expired" >/dev/null 2>&1

openssl ca -batch -config "$TMPDIR/ca/ca.conf" \
  -in "$TMPDIR/exp.csr" \
  -startdate "$start" -enddate "$end" \
  -out "$TMPDIR/exp.pem" >/dev/null 2>&1

echo "[3/5] Prove premise: cert exists + is expired"
openssl x509 -noout -subject -dates -in "$TMPDIR/exp.pem"
if openssl x509 -in "$TMPDIR/exp.pem" -checkend 0 -noout >/dev/null 2>&1; then
  echo "ERROR: cert is NOT expired (checkend 0 passed)"; exit 1
else
  echo "OK: cert is expired (checkend 0 failed)"
fi

echo "[4/5] Connect to Envoy with TLS trace (writes /tmp/mtls_trace.txt)"
openssl s_client -connect localhost:8443 \
  -servername tool-b-envoy \
  -cert "$TMPDIR/exp.pem" -key "$TMPDIR/exp.key" \
  -state -msg -tlsextdebug -brief < /dev/null | tee /tmp/mtls_trace.txt

echo "[5/5] Quick classifiers:"
echo "---- Did server request a client cert? (CertificateRequest) ----"
grep -n "CertificateRequest" -n /tmp/mtls_trace.txt || echo "NO CertificateRequest FOUND"

echo "---- Did client send a cert? (Certificate) ----"
grep -n "^>>> TLS" -n /tmp/mtls_trace.txt | head -n 20 || true
grep -n "Certificate" /tmp/mtls_trace.txt | head -n 20 || echo "NO Certificate message FOUND (could be missing or too verbose)"

echo "---- Did handshake succeed? ----"
grep -n "Verify return code" /tmp/mtls_trace.txt || true
grep -n "Handshake has read" /tmp/mtls_trace.txt || true
grep -n "handshake failure\|certificate expired\|expired\|verify error\|alert" /tmp/mtls_trace.txt || echo "No obvious TLS failure markers"
