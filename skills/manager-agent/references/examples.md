# Manager Agent Examples

## Example: build flow

Input:
- user wants a feature shipped
- repo scope is known

Good manager move:
1. classify as build
2. decide whether planning is needed
3. dispatch coding-worker with bounded scope
4. verify code and validation evidence
5. route to reviewer if needed
6. accept or reject

## Example: weak handoff rejection

Worker says:
- "done"
- gives a commit hash

But:
- build path in repo does not exist
- claimed files are missing

Good manager response:
- reject the handoff
- name the exact mismatch
- reroute or tighten the contract
