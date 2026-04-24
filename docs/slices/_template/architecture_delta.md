# Architecture Delta

## Responsibility changes
- Describe component or trust-boundary responsibility changes for this slice.

## Authoritative state inventory

| State / Key | Store / System | Writer | Reader | TTL / Lifecycle | Decision impact | Type |
|---|---|---|---|---|---|---|
| Example | Redis | service-a | service-b | TTL or retention | What decision depends on it | Authoritative / Advisory |

## Hidden behavior disclosure
- Record any runtime-significant behavior that would otherwise only be visible from code.
