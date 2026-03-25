# Calibration changelog

## Priority behavior comparison

- Old threshold bands: P0 >= 18, P1 13..17, P2 8..12, P3 0..7
- New threshold bands: P0 >= 24, P1 16..23, P2 8..15, P3 0..7
- Added mandatory P0 cap rule requiring severity >= 4 or blockingBreadth >= 3 or deadlineProximity >= 4
- Tie-break order is now: higher blockingBreadth, earlier deadline, higher businessImpact, lower estimatedTokens, older queue insertion time
- Decision traces now log calibrated factor scores and tie-break reasons

## Distribution comparison on calibration pack

- Legacy P0 count: 12 of 19 (63.16%)
- New P0 count: 1 of 19 (5.26%)
- New P1 count: 12 of 19 (63.16%)
- New P2 count: 4 of 19 (21.05%)
- New P3 count: 2 of 19 (10.53%)

## Acceptance observations

- P0 materially reduced vs legacy model: True
- Mixed queue includes P2: True
- Mixed queue includes P3: True
- Tie-break usage visible: True
