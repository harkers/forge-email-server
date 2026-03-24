# PowerPoint MCP Skill

## Purpose

Create, edit, and save PowerPoint presentations (.pptx) using the `powerpoint__*` tools. 37 tools covering the full python-pptx surface area: slides, text, tables, charts, shapes, images, templates, themes, transitions, hyperlinks, connectors, fonts, and slide masters.

Files are persisted to the `infra_powerpoint_files` Docker volume, mounted at `/pptx` inside the container.

---

## Quick Start

### Always follow this sequence

```
1. create_presentation  OR  open_presentation  OR  create_presentation_from_template
2. [add slides, content, design]
3. save_presentation
4. [copy file out if needed]
```

You MUST create or open a presentation before calling any other tool. All tools operate on the **currently active presentation** tracked by global state inside the server.

---

## All 37 Tools

### Presentation Management

| Tool | Purpose | Key Args |
|------|---------|----------|
| `powerpoint__create_presentation` | New blank presentation | `title`, `width_inches`, `height_inches` |
| `powerpoint__create_presentation_from_template` | Clone a .pptx template | `template_path`, `title` |
| `powerpoint__open_presentation` | Open existing .pptx | `file_path` |
| `powerpoint__save_presentation` | Save to disk | `file_path` (e.g. `/pptx/output.pptx`) |
| `powerpoint__get_presentation_info` | Slide count, dimensions, metadata | — |
| `powerpoint__get_template_file_info` | Inspect a template file | `template_path` |
| `powerpoint__set_core_properties` | Set title/author/subject/keywords | `title`, `author`, `subject`, `keywords`, `comments` |
| `powerpoint__list_presentations` | List all open presentations | — |
| `powerpoint__switch_presentation` | Change active presentation | `presentation_id` |
| `powerpoint__get_server_info` | Server version + tool count | — |

### Content — Slides

| Tool | Purpose | Key Args |
|------|---------|----------|
| `powerpoint__add_slide` | Add a slide | `layout_index`, `background_color`, `gradient_*` |
| `powerpoint__get_slide_info` | Shapes, placeholders, dimensions | `slide_index` |
| `powerpoint__extract_slide_text` | All text from one slide | `slide_index` |
| `powerpoint__extract_presentation_text` | All text from all slides | — |
| `powerpoint__populate_placeholder` | Fill a layout placeholder | `slide_index`, `placeholder_idx`, `text` |
| `powerpoint__add_bullet_points` | Bulleted text box | `slide_index`, `bullets` (list), `left/top/width/height` |
| `powerpoint__optimize_slide_text` | Auto-resize/wrap text | `slide_index`, `max_font_size`, `min_font_size` |

### Content — Text

| Tool | Purpose | Key Args |
|------|---------|----------|
| `powerpoint__manage_text` | Unified text operations | `operation`: `add`, `format`, `validate`, `style_runs` |

**manage_text operations:**

```json
// Add text box
{
  "operation": "add",
  "slide_index": 0,
  "text": "Hello World",
  "left": 1, "top": 1, "width": 8, "height": 1,
  "font_size": 24,
  "font_bold": true,
  "font_color": "1F4E79",
  "alignment": "center"
}

// Format existing shape
{
  "operation": "format",
  "slide_index": 0,
  "shape_index": 0,
  "font_size": 18,
  "font_italic": true
}
```

### Content — Images

| Tool | Purpose | Key Args |
|------|---------|----------|
| `powerpoint__manage_image` | Add or enhance images | `operation`: `add`, `enhance` |

```json
// Add image from file
{
  "operation": "add",
  "slide_index": 0,
  "image_path": "/pptx/logo.png",
  "left": 1, "top": 1, "width": 4, "height": 3
}

// Add image from base64
{
  "operation": "add",
  "slide_index": 0,
  "image_data": "<base64-string>",
  "image_format": "png",
  "left": 1, "top": 1, "width": 4, "height": 3
}

// Enhance (brightness, contrast, saturation, filters)
{
  "operation": "enhance",
  "slide_index": 0,
  "shape_index": 2,
  "brightness": 1.2,
  "contrast": 1.1,
  "filter": "grayscale"
}
```

### Structural Elements

| Tool | Purpose | Key Args |
|------|---------|----------|
| `powerpoint__add_table` | Insert a table | `slide_index`, `rows`, `cols`, `data` (2D list), `left/top/width/height`, `header_color`, `body_color` |
| `powerpoint__format_table_cell` | Style individual cell | `slide_index`, `shape_index`, `row`, `col`, `font_*`, `bg_color`, `alignment` |
| `powerpoint__add_shape` | Insert auto-shape | `slide_index`, `shape_type` (see below), `left/top/width/height`, `fill_color`, `text` |
| `powerpoint__add_chart` | Insert chart | `slide_index`, `chart_type`, `categories`, `series_data`, `left/top/width/height` |
| `powerpoint__add_connector` | Line/arrow between points | `slide_index`, `connector_type`, `begin_x/y`, `end_x/y`, `line_color`, `line_width` |

**Shape types for add_shape:**
`rectangle`, `rounded_rectangle`, `oval`, `triangle`, `right_arrow`, `left_arrow`,
`up_arrow`, `down_arrow`, `star_5`, `star_6`, `star_8`, `heart`, `lightning_bolt`,
`cloud`, `hexagon`, `octagon`, `cross`, `diamond`, `parallelogram`, `trapezoid`,
`chevron`, `plus`, `callout`, `document`

**Chart types:**
`column`, `bar`, `line`, `pie`, `scatter`, `radar`

**Connector types:**
`straight`, `elbow`, `curved`

### Templates

| Tool | Purpose | Key Args |
|------|---------|----------|
| `powerpoint__list_slide_templates` | Show 25+ built-in layouts | — |
| `powerpoint__get_template_info` | Detail on a specific template | `template_name` |
| `powerpoint__apply_slide_template` | Apply layout to existing slide | `slide_index`, `template_name`, `color_scheme`, `content_map` |
| `powerpoint__create_slide_from_template` | New slide from template | `template_name`, `color_scheme`, `content_map` |
| `powerpoint__create_presentation_from_templates` | Full deck from template sequence | `slides` (list of template specs) |
| `powerpoint__auto_generate_presentation` | Auto-generate whole deck | `topic`, `num_slides` (3-20), `style` (`business`/`academic`/`creative`) |

**Color schemes:**
`modern_blue`, `corporate_gray`, `elegant_green`, `warm_red`

**Example auto-generate:**
```json
{
  "topic": "Q1 2026 Sales Review",
  "num_slides": 8,
  "style": "business",
  "color_scheme": "modern_blue"
}
```

### Professional Design

| Tool | Purpose | Key Args |
|------|---------|----------|
| `powerpoint__apply_professional_design` | Themes, backgrounds, visual enhancements | `operation`: `apply_theme`, `set_background`, `enhance_slide` |
| `powerpoint__apply_picture_effects` | Shadow, glow, bevel, reflection, etc. | `slide_index`, `shape_index`, `effects` (dict) |
| `powerpoint__manage_fonts` | Analyse/optimise/recommend fonts | `operation`: `analyze`, `optimize`, `recommend` |

**apply_picture_effects — available effects:**
```json
{
  "shadow": { "blur": 10, "distance": 5, "color": "000000", "transparency": 0.5 },
  "reflection": { "size": 0.3, "distance": 0, "transparency": 0.5 },
  "glow": { "size": 10, "color": "4472C4", "transparency": 0.3 },
  "soft_edges": { "radius": 5 },
  "bevel": { "width": 6, "height": 6 },
  "rotation": { "angle": 15 },
  "transparency": 0.2,
  "filter": "grayscale"
}
```

### Charts, Hyperlinks, Masters, Transitions

| Tool | Purpose | Key Args |
|------|---------|----------|
| `powerpoint__update_chart_data` | Replace chart data | `slide_index`, `shape_index`, `categories`, `series_data` |
| `powerpoint__manage_hyperlinks` | Add/remove/list/update links | `operation`, `slide_index`, `shape_index`, `url` |
| `powerpoint__manage_slide_masters` | List masters and layouts | `operation`: `list_masters`, `get_layouts`, `get_master_info`, `get_layout_info` |
| `powerpoint__manage_slide_transitions` | Set/remove/get transitions | `operation`, `slide_index`, `transition_type`, `duration` |

---

## Common Workflows

### Workflow 1 — Quick deck from scratch

```
1. powerpoint__create_presentation
     title="Q1 Review", width_inches=13.33, height_inches=7.5

2. powerpoint__add_slide
     layout_index=0, background_color="1F4E79"

3. powerpoint__manage_text
     operation="add", slide_index=0,
     text="Q1 2026 Review", left=1, top=2.5, width=11, height=2,
     font_size=44, font_bold=true, font_color="FFFFFF", alignment="center"

4. powerpoint__add_slide
     layout_index=1

5. powerpoint__add_bullet_points
     slide_index=1,
     bullets=["Revenue up 23%", "Pipeline at $4.2M", "3 new enterprise accounts"],
     left=1, top=2, width=11, height=4, font_size=24

6. powerpoint__save_presentation
     file_path="/pptx/q1-review.pptx"
```

### Workflow 2 — Auto-generate then customise

```
1. powerpoint__auto_generate_presentation
     topic="DataDNA Helix Platform Overview"
     num_slides=10, style="business"

2. powerpoint__get_presentation_info          # check what was created

3. powerpoint__apply_professional_design
     operation="apply_theme", theme="modern_blue"

4. powerpoint__manage_text                    # edit specific slide text
     operation="format", slide_index=0, shape_index=0, font_size=40

5. powerpoint__save_presentation
     file_path="/pptx/datadna-helix.pptx"
```

### Workflow 3 — Add chart + table

```
1. powerpoint__open_presentation
     file_path="/pptx/existing.pptx"

2. powerpoint__add_slide  layout_index=6

3. powerpoint__add_chart
     slide_index=2, chart_type="column",
     categories=["Q1", "Q2", "Q3", "Q4"],
     series_data=[
       {"name": "Revenue", "values": [120, 145, 132, 178]},
       {"name": "Target",  "values": [130, 140, 150, 160]}
     ],
     left=0.5, top=1.5, width=8, height=5

4. powerpoint__add_table
     slide_index=2,
     data=[["Metric","Q1","Q2","Q3","Q4"],
           ["Revenue","120","145","132","178"],
           ["Target", "130","140","150","160"]],
     left=9, top=1.5, width=4, height=5,
     header_color="1F4E79", body_color="D6E4F0"

5. powerpoint__save_presentation
     file_path="/pptx/existing.pptx"
```

### Workflow 4 — Template-based deck

```
1. powerpoint__list_slide_templates           # see available templates

2. powerpoint__create_presentation_from_templates
     slides=[
       {"template": "title_slide",  "color_scheme": "modern_blue",
        "content": {"title": "My Deck", "subtitle": "March 2026"}},
       {"template": "content_slide", "color_scheme": "modern_blue",
        "content": {"title": "Overview", "bullets": ["Point 1","Point 2"]}},
       {"template": "chart_slide",  "color_scheme": "modern_blue",
        "content": {"title": "Financials"}}
     ]

3. powerpoint__save_presentation
     file_path="/pptx/template-deck.pptx"
```

---

## Coordinates & Units

All position/size arguments are in **inches**:

| Argument | Default slide (13.33 × 7.5 in widescreen) |
|----------|-------------------------------------------|
| `left=0` | Left edge |
| `top=0` | Top edge |
| `width=13.33` | Full width |
| `height=7.5` | Full height |
| Safe content area | `left=0.5, top=0.75, width=12.33, height=6.0` |

---

## File Access

Files created by the server live at `/pptx` inside the container, backed by the `infra_powerpoint_files` Docker volume.

### Copy a file out to the host

```bash
DOCKER_API_VERSION=1.41 docker cp openclaw-powerpoint-mcp:/pptx/output.pptx ./output.pptx
```

### List files currently in the volume

```bash
# Via the bonus endpoint
curl http://127.0.0.1:18102/files

# Or directly
DOCKER_API_VERSION=1.41 docker exec openclaw-powerpoint-mcp ls /pptx
```

### Copy a file IN (template or image)

```bash
DOCKER_API_VERSION=1.41 docker cp ./my-template.pptx openclaw-powerpoint-mcp:/pptx/my-template.pptx
```

### Template directory

Custom templates go in `/pptx/templates/` inside the container:

```bash
DOCKER_API_VERSION=1.41 docker cp ./brand-template.pptx openclaw-powerpoint-mcp:/pptx/templates/brand-template.pptx
```

Then reference as `template_path="/pptx/templates/brand-template.pptx"`.

---

## Service Details

| Property | Value |
|----------|-------|
| Container | `openclaw-powerpoint-mcp` |
| Port | `18102` |
| Profile | `powerpoint` |
| Gateway label | `powerpoint` |
| Tool prefix | `powerpoint__` |
| Volume | `infra_powerpoint_files` → `/pptx` |
| Template env var | `PPT_TEMPLATE_PATH=/pptx/templates` |
| Upstream package | `office-powerpoint-mcp-server==2.0.7` |
| Bridge pattern | stdio subprocess (same as github-mcp) |
| Tool call timeout | 120s (image/font ops are slow) |

**Endpoints:**
```
GET  http://127.0.0.1:18102/health   # subprocess status + dirs
GET  http://127.0.0.1:18102/tools    # all 37 tools
POST http://127.0.0.1:18102/call     # invoke a tool
GET  http://127.0.0.1:18102/files    # list .pptx files in /pptx
```

---

## Start / Stop

```bash
# Start
DOCKER_API_VERSION=1.41 MINIO_ROOT_PASSWORD=unused POSTGRES_PASSWORD=unused PIHOLE_WEBPASSWORD=unused \
  docker compose -f infra/docker-compose.yml --profile powerpoint up -d

# Stop
DOCKER_API_VERSION=1.41 docker compose -f infra/docker-compose.yml --profile powerpoint down

# Restart (e.g. after subprocess crash)
DOCKER_API_VERSION=1.41 docker restart openclaw-powerpoint-mcp

# Rebuild after code changes
DOCKER_API_VERSION=1.41 docker build -t openclaw/powerpoint-mcp:latest services/powerpoint-mcp/
DOCKER_API_VERSION=1.41 docker restart openclaw-powerpoint-mcp
```

---

## Troubleshooting

### "subprocess": "stopped" in /health

The `ppt_mcp_server` subprocess crashed. Check logs:

```bash
DOCKER_API_VERSION=1.41 docker logs openclaw-powerpoint-mcp --tail 50
```

The bridge auto-restarts the subprocess on the next tool call. Or force it:

```bash
DOCKER_API_VERSION=1.41 docker restart openclaw-powerpoint-mcp
```

### "No active presentation" error

You called a tool before `create_presentation` or `open_presentation`. The server loses state when restarted — always start with create/open.

### File path not found

Paths inside the container must start with `/pptx/`. Do not use host paths. Use `docker cp` to move files in/out.

### Image from base64 failing

Make sure `image_format` matches the actual format (`png`, `jpeg`, `gif`). Base64 must be raw (no `data:image/...;base64,` prefix).

### Font analysis slow

`manage_fonts` with `operation="analyze"` runs fonttools over system fonts — can take 5-15s. Normal behaviour.

### Tools not in MCP proxy

Re-approve if gateway was lost:

```bash
OPKEY=$(grep OPERATOR_API_KEY infra/.env | cut -d= -f2)
GW_ID=$(curl -s -H "X-API-Key: $OPKEY" http://127.0.0.1:8888/api/v1/gateways | \
  python3 -c "import json,sys; gws=[g for g in json.load(sys.stdin) if g['gateway_label']=='powerpoint']; print(gws[0]['id'])")
curl -s -X PATCH "http://127.0.0.1:8888/api/v1/gateways/$GW_ID/approval" \
  -H "X-API-Key: $OPKEY" -H "Content-Type: application/json" \
  -d '{"action":"approve","reason":"re-approve","approved_by":"stu"}'
curl -s -X POST http://127.0.0.1:18100/tools/refresh
```

---

## Built-in Template Reference

Run `powerpoint__list_slide_templates` to get the full list. Common ones:

| Template Name | Description |
|---------------|-------------|
| `title_slide` | Large title + subtitle |
| `content_slide` | Title + bullet points |
| `two_column` | Side-by-side content |
| `image_left` | Image left, text right |
| `image_right` | Text left, image right |
| `chart_slide` | Title + chart placeholder |
| `table_slide` | Title + table placeholder |
| `section_divider` | Section header with accent |
| `quote_slide` | Full-bleed quote layout |
| `team_slide` | Team member cards |
| `timeline_slide` | Horizontal timeline |
| `comparison_slide` | A vs B comparison |
| `statistics_slide` | Big numbers + labels |
| `thank_you` | Closing slide |

---

## Example: Full Business Deck (end-to-end)

```
powerpoint__create_presentation
  title="DataDNA Helix — Investor Brief"

powerpoint__add_slide layout_index=0, background_color="0D1B2A"
powerpoint__manage_text
  operation="add", slide_index=0,
  text="DataDNA Helix", left=1, top=2, width=11, height=1.5,
  font_size=54, font_bold=true, font_color="00D4FF", alignment="center"
powerpoint__manage_text
  operation="add", slide_index=0,
  text="Transforming clinical data into actionable intelligence",
  left=1, top=3.8, width=11, height=1,
  font_size=20, font_color="AAAAAA", alignment="center"

powerpoint__add_slide layout_index=1
powerpoint__add_bullet_points
  slide_index=1,
  bullets=["$4.2M ARR growing 89% YoY",
           "47 enterprise clients across 12 countries",
           "ISO 27001 certified, HIPAA compliant",
           "Series A: seeking $12M"],
  left=1, top=1.5, width=11, height=5, font_size=26

powerpoint__add_slide layout_index=6
powerpoint__add_chart
  slide_index=2, chart_type="line",
  categories=["Q1 '25","Q2 '25","Q3 '25","Q4 '25","Q1 '26"],
  series_data=[{"name":"ARR ($M)","values":[1.8,2.4,3.1,3.8,4.2]}],
  left=1, top=1.5, width=11, height=5.5

powerpoint__set_core_properties
  title="DataDNA Helix Investor Brief"
  author="DataDNA Team"
  subject="Series A Fundraising 2026"

powerpoint__save_presentation
  file_path="/pptx/datadna-helix-investor-brief.pptx"
```
