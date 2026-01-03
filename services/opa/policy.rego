package capiss

default allow = false

allow if {
  input.sub == "spiffe://example.org/agent-a"
  input.aud == "tool-b"
  input.act == "read"
  input.res == "/secret"
}
