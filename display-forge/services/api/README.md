# API Service

Current MVP stub:

- `GET /api/health`
- `GET /api/dashboard/summary`
- `GET /api/campaigns`
- `POST /api/campaigns`
- `PUT /api/campaigns/{id}`
- `DELETE /api/campaigns/{id}`
- `GET /api/screens/default/playlist`

Current persistence:

- file-backed JSON store at `services/api/app/storage/campaigns.json`

Current scheduling logic:

- only `status=active` campaigns are eligible for playback
- `activeFrom` schedules a campaign into the future
- `activeUntil` expires a campaign automatically
- playlist endpoint returns only currently eligible campaigns
- campaign listing includes simple eligibility reasons

Run locally:

```bash
cd services/api
python3 app/main.py
```
