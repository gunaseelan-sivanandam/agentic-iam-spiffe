# Review task (short list)

Review the change for defects that matter within the threat model of the approved rules. Answer
three questions:

1. Can a test, gate or check pass while the behaviour it claims to prove is broken (a false green)?
2. Can a key, secret, socket or token reach a service, file or record outside its holders?
3. Does the change contradict a rule, a requirement, a document or another part of the code?

Report each defect as a finding with its exact location (file and line in the reviewed commit). Use
the kind "blocking" for a concrete defect with a failure scenario; everything else is advisory.
