package capiss

default allow = false

allow if {
  input.decision_type == "root_mint"
  input.sub == "spiffe://example.org/agent-a"
  input.aud == "tool-b"
  input.act == "read"
  input.res == "tool-b:/secret"
}

allow if {
  input.decision_type == "root_mint"
  input.sub == "spiffe://example.org/agent-a"
  input.aud == "tool-b"
  input.act == "read"
  input.res == "tool-b:/search"
}

allow if {
  input.decision_type == "resource_mint"
  input.sub == "spiffe://example.org/agent-a"
  input.aud == "tool-b"
  input.act == "read"
  startswith(input.res, "tool-b:/read-file:")
  input.registry_hit == true
}
