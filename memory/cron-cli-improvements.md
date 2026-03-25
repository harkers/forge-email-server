# Cron CLI Improvements Implementation Summary

## Date: 2026-03-25

### Changes Implemented

#### 1. Schema Changes (CronJobState and CronJob)

**File: `src/cron/types.ts`**
- Added `suspendedUntil?: number` to `CronJobState` type
  - Stores timestamp when suspension expires
  - Job is temporarily disabled until this time

**File: `src/cron/types-shared.ts`**
- Added `tags?: string[]` to `CronJobBase` type
  - Optional array of tags for organization and filtering
  - Max 20 tags per job

**File: `src/gateway/protocol/schema/cron.ts`**
- Updated `CronJobStateSchema` with `suspendedUntil` field
- Updated `CronJobSchema` with `tags` field
- Added `CronSuspendParamsSchema` and `CronTriggerParamsSchema`
- Updated `CronJobsEnabledFilterSchema` to include "suspended"
- Updated `CronListParamsSchema` with `tags` and `tag` parameters

**File: `src/gateway/protocol/index.ts`**
- Exported new schemas: `CronSuspendParamsSchema`, `CronTriggerParamsSchema`
- Added validators: `validateCronSuspendParams`, `validateCronTriggerParams`

#### 2. Service Layer Changes

**File: `src/cron/service/ops.ts`**
- Added `CronJobsEnabledFilter` type with "suspended" option
- Added `isJobSuspended()` helper function
- Added `matchesTags()` helper function
- Updated `listPage()` to filter by state (enabled/disabled/suspended) and tags
- Added `trigger()` function - runs job once without mutating schedule
- Added `suspend()` function - suspends job for specified duration
- Added `checkSuspendedJobs()` function - called by timer to auto-enable expired suspensions

**File: `src/cron/service.ts`**
- Added `trigger()` method to CronService class
- Added `suspend()` method to CronService class
- Added `findJob()` method - resolves job by ID or name
- Added `findJobsByName()` method - finds all jobs matching a name

**File: `src/cron/service/timer.ts`**
- Added import for `checkSuspendedJobs`
- Updated `onTimer()` to call `checkSuspendedJobs()` before processing due jobs

#### 3. Gateway Handlers

**File: `src/gateway/server-methods/cron.ts`**
- Added `"cron.trigger"` handler - calls `context.cron.trigger()`
- Added `"cron.suspend"` handler - calls `context.cron.suspend()`
- Updated `"cron.list"` handler to support `tags`, `tag`, and `enabled="suspended"` parameters

#### 4. CLI Commands

**New Files Created:**

**File: `src/cli/cron-cli/register.cron-show.ts`**
- `openclaw cron show <id-or-name>` - Display job details
- `openclaw cron inspect <id-or-name>` - Alias for show
- Shows: ID, name, description, state, schedule, execution config, tags, run history, delivery config

**File: `src/cli/cron-cli/register.cron-trigger.ts`**
- `openclaw cron trigger <id-or-name>` - Run job once without mutating schedule
- Supports `--json` output
- Supports `-y, --yes` to skip confirmation
- Shows job summary before execution

**File: `src/cli/cron-cli/register.cron-suspend.ts`**
- `openclaw cron suspend <id-or-name> --for <duration>` - Temporarily suspend job
- Duration formats: `2h`, `30m`, `1d`, `500ms`
- Auto-enables after duration expires
- Supports `--json` output
- Supports `-y, --yes` to skip confirmation

**File: `src/cli/cron-cli/register.cron-history.ts`**
- `openclaw cron history [id-or-name]` - Show run history
- `openclaw cron runs [id-or-name]` - Alias for history
- Options: `--json`, `-l/--limit`, `--offset`, `--status`, `--errors`

**Updated Files:**

**File: `src/cli/cron-cli/register.cron-simple.ts`**
- Updated `enable`, `disable`, `remove` to support name-based targeting
- Added disambiguation for ambiguous names
- Added confirmation prompts for destructive actions

**File: `src/cli/cron-cli/register.cron-add.ts`**
- Updated `list` command:
  - Added `--state <state>` filter (enabled, disabled, suspended, all)
  - Added `--tag <tag>` filter
  - Added `ls` alias

**File: `src/cli/cron-cli/register.ts`**
- Registered new commands: show, trigger, suspend, history

### CLI Command Summary

```bash
# List jobs with filtering
openclaw cron list --state enabled
openclaw cron list --state disabled
openclaw cron list --state suspended
openclaw cron list --tag dispatch

# Inspect job details
openclaw cron show auto-dispatch
openclaw cron show c5ce9bc4-7f5e-49cc-9ead-479e43df9c22

# Safe control commands
openclaw cron disable auto-dispatch    # Preserves schedule
openclaw cron enable auto-dispatch     # Restores to runnable state
openclaw cron trigger auto-dispatch    # Run once, keeps schedule
openclaw cron suspend auto-dispatch --for 2h  # Temp suspend with auto-resume

# View history
openclaw cron history auto-dispatch
openclaw cron history --errors
openclaw cron history --status error

# Remove job (destructive, requires confirmation)
openclaw cron rm auto-dispatch -y
```

### State Machine

Jobs now have three states:
1. **enabled** - Job runs according to schedule
2. **disabled** - Job is paused, schedule preserved
3. **suspended** - Job is temporarily disabled, auto-enables after `suspendedUntil` time

### Backward Compatibility

- `remove` and `run` commands continue to work
- Existing jobs without `tags` field work normally
- Existing jobs without `suspendedUntil` field work normally

### Tests Required (Manual Testing)

1. `disable` then `enable` preserves schedule
2. `trigger` does not mutate schedule
3. `suspend` expires correctly and auto-enables
4. Name lookup resolves uniquely
5. Ambiguous names fail with disambiguation prompt
6. List filtering by state and tag works correctly

### Implementation Notes

1. The timer automatically checks `checkSuspendedJobs()` on each tick to re-enable expired suspensions
2. Suspension duration is stored in milliseconds in `state.suspendedUntil`
3. Tags are optional arrays on the job for filtering
4. Name resolution prefers exact ID match, then exact name match
5. All new commands support `--json` for programmatic use