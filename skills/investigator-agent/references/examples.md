# Investigator Agent Examples

## Good investigation output
- Reproduced the failure on POST requests only.
- Confirmed the route exists but rejects requests because the nonce header is missing.
- Confidence: high.
- Next step: route to coding-worker to add nonce propagation in the frontend request helper.

## Weak investigation output
- It might be auth or maybe caching.

Reason it is weak:
- no evidence
- no narrowing
- no next decisive step
