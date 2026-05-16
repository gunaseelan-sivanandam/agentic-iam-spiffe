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

# DD: DD-127
# Implements: ARCH-013, ARCH-021
# Title: allow_jira_project_root_mint OPA Jira project root mint policy
allow if {
  input.decision_type == "root_mint"
  input.sub == "spiffe://example.org/agent-a"
  input.aud == "jira-tool"
  input.act == "read"
  input.res == "jira-tool:/project:IAM"
}

# DD: DD-128
# Implements: ARCH-021, ARCH-025
# Title: allow_jira_project_write_root_mint OPA Jira project write mint policy
allow if {
  input.decision_type == "root_mint"
  input.sub == "spiffe://example.org/agent-a"
  input.aud == "jira-tool"
  input.act == "write"
  input.res == "jira-tool:/project:IAM"
}

# DD: DD-130
# Implements: ARCH-028
# Title: allow_jira_mcp_summary_root_mint OPA Jira MCP summary mint policy
allow if {
  input.decision_type == "root_mint"
  input.sub == "spiffe://example.org/codex-jira-mcp-adapter"
  input.aud == "jira-mcp-gateway"
  input.act == "read_project_summary"
  input.res == "jira-mcp:/project:IAM"
}

# DD: DD-131
# Implements: ARCH-028
# Title: allow_jira_mcp_story_root_mint OPA Jira MCP story mint policy
allow if {
  input.decision_type == "root_mint"
  input.sub == "spiffe://example.org/codex-jira-mcp-adapter"
  input.aud == "jira-mcp-gateway"
  input.act == "create_story"
  input.res == "jira-mcp:/project:IAM"
}

allow if {
  input.decision_type == "resource_mint"
  input.sub == "spiffe://example.org/agent-a"
  input.aud == "tool-b"
  input.act == "read"
  startswith(input.res, "tool-b:/read-file:")
  input.registry_hit == true
}
