# Canadian Privacy Legislation - Reference Index

Source: Government of Canada Justice Laws
Ingested: 2026-03-28

## Acts Ingested into RAG

### PIPEDA - Personal Information Protection and Electronic Documents Act
- **URL:** https://laws-lois.justice.gc.ca/eng/acts/p-8.6/FullText.html
- **Chunks:** 95
- **Jurisdiction:** Canada (Federal)
- **Scope:** Private sector privacy, electronic commerce
- **Key topics:**
  - Consent requirements for collection, use, disclosure
  - Exemptions for investigative purposes
  - Business contact information exemption
  - Security safeguards and breach notification
  - Cross-border disclosure

### Privacy Act (R.S.C., 1985, c. P-21)
- **URL:** https://laws-lois.justice.gc.ca/eng/acts/P-21/FullText.html
- **Chunks:** 120
- **Jurisdiction:** Canada (Federal)
- **Scope:** Federal government institutions, personal information handling
- **Key topics:**
  - Access to personal information held by government
  - Collection limitations
  - Disclosure exemptions (national security, law enforcement)
  - Privacy Commissioner powers
  - Correction of personal information

## Related Legislation (Not Yet Ingested)

### Provincial Privacy Acts
- **Alberta:** Personal Information Protection Act (PIPA)
- **British Columbia:** Personal Information Protection Act (PIPA)
- **Quebec:** Act Respecting the Protection of Personal Information in the Private Sector
- **Ontario:** Personal Health Information Protection Act (PHIPA)

### Sector-Specific
- **Canada Health Act** - health information handling
- **Digital Charter Implementation Act** - Bill C-27 (proposed)
- **Consumer Privacy Protection Act** - CPPA (proposed)

## Search Queries

To search these documents in RAG:
```
docker run --rm --network infra_internal curlimages/curl:latest \
  curl -s -X POST http://embedding-worker:8080/call \
  -H "Content-Type: application/json" \
  -d '{"name": "search_documents", "arguments": {"query": "<your query>", "top_k": 5}}'
```