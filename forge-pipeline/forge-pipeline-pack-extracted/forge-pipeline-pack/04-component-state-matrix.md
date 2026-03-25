# Component / State Matrix

## PageHeader
Purpose: anchors page identity and system status
States: default, loading, error, stale

## KpiTile
Purpose: surface high-level counts
States: default, loading, empty, alert

## InsightStrip
Purpose: surface generated management insight
States: default, loading, empty

## FilterBar
Purpose: refine visible work without leaving page
States: default, expanded, collapsed, active-filters

## BoardColumn
Types: next-up, blocked, activity
States: default, empty, loading, error

## TaskCard
States: default, hover, selected, overdue, due-soon, stale, at-risk, loading

## BlockedCard
States: default, hover, selected, critical, aging-blocker

## ActivityCard
States: default, hover, selected, new

## EmptyState
States: default, illustrated, compact

## FocusCard
States: default, none-available, loading

## SourceHealthItem
States: healthy, delayed, error, paused

## DetailDrawer
States: closed, open, loading, error, saving
