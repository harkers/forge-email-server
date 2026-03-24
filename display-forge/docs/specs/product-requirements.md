# Display Forge — Product Requirements Document

Version: 1.0

## Overview

Display Forge is a digital signage platform designed to run promotional adverts, announcements, and dynamic content on a 55-inch TV. It is intended to be reliable, visually polished, and low-maintenance. It should ingest content from RSS feeds and other sources, schedule content automatically, and self-manage based on active dates, expiry rules, and display priorities.

The goal is to make the system feel like a forge rather than a file dump: content comes in, is shaped, timed, approved, and rendered beautifully on screen without requiring daily manual intervention.

## Core Purpose

The platform should:

- display adverts and promotional content on a 55-inch TV
- ingest content from RSS feeds and other configurable sources
- automatically activate and deactivate content based on timing rules
- support both fully automated and manually curated content flows
- manage multiple pieces of content in rotation
- ensure expired or superseded content is removed automatically
- present content in a visually consistent, high-impact format
- be easy to manage by non-technical users

## Primary Use Cases

- Retail / showroom advertising
- Corporate / office display
- Hospitality / waiting area content
- Community / public-facing notices

## Display Environment

Primary target:

- 55-inch TV
- landscape orientation
- 16:9 aspect ratio
- full-screen continuous playback
- 1080p baseline, 4K-ready where possible

Viewing assumptions:

- medium viewing distance
- readable in a few seconds
- motion used sparingly
- glanceable rather than text-heavy

## Functional Scope

### Content Intake

Required intake options:

- RSS feeds
- manual content entry
- image upload
- text-and-image slide creation
- emergency override message entry
- structured API / JSON input

Optional later intake:

- weather
- date/time
- calendar feeds
- events feeds
- stock/pricing feeds
- social content

### Content Model

Each content item should support fields such as:

- content ID
- title
- source type
- source URL / origin
- media asset(s)
- summary / body copy
- call to action
- target layout
- category
- tags
- priority
- status
- active from
- active until
- display duration
- approval status
- screen target
- region / location target
- recurrence rule
- fallback eligibility
- created by
- updated date

### Scheduling and Timing

Required capabilities:

- active from date/time
- active until date/time
- day-of-week scheduling
- time-of-day scheduling
- recurring schedules
- blackout windows
- campaign priority weighting
- automatic expiry
- automatic archiving
- pre-scheduled future activation

### Playlist Engine

Required behaviour:

- dynamically generate active playlist
- include only active content
- remove expired content automatically
- weight priority content more frequently
- suppress duplicates / stale items
- fill gaps with fallback content
- allow emergency override content

### Layout System

Suggested layouts:

- full-screen advert
- split layout
- ticker layout
- multi-panel layout
- template-driven cards

### RSS Behaviour

RSS should support:

- scheduled polling
- parsing title, description, date, media, enclosure, category
- new vs existing item detection
- feed-to-template mapping
- feed-level filtering
- default expiry rules
- approval workflows where required

### Governance

Required controls:

- draft / approved / active / expired / archived states
- role-based access
- approval workflow option
- audit trail
- preview before publish
- asset validation
- duplicate detection
- expiry warnings
- broken feed detection

### Self-Management Rules

The system should:

- auto-expire content
- hide inactive content automatically
- quarantine failed feed items
- use fallback logic for missing assets
- remove stale RSS items after configured time
- revert to default channel when schedules are empty
- reconnect and resume after reboot/outage
- alert admins if screen or feed fails

### Administration Interface

Core sections:

- dashboard
- content library
- feed manager
- schedule manager
- playlist preview
- templates
- screens / devices
- alerts / health
- logs / audit trail
- settings

### Screen Player Requirements

The playback client should support:

- full-screen kiosk mode
- automatic launch on startup
- offline cache of active content
- scheduled refresh
- graceful network-loss handling
- smooth transitions
- heartbeat reporting
- remote restart / refresh
- tamper-resistant mode

## Non-Functional Requirements

The system should be:

- reliable
- usable
- scalable
- maintainable
- performant
- secure

## MVP Recommendation

First release scope:

- one 55-inch landscape display
- RSS ingestion from multiple feeds
- manual content upload
- start/end scheduling
- playlist rotation with priority
- expiry automation
- one or two branded templates
- admin dashboard
- player with offline cache and auto-start
- default fallback playlist

## Success Criteria

Display Forge succeeds if:

- users can publish content in minutes
- RSS-fed content appears automatically and correctly
- adverts start and stop without manual intervention
- expired content never lingers on screen
- the TV display remains stable and attractive
- the system runs largely unattended
- one operator can manage the setup with minimal effort
