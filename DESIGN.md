# Concord - Design System

Concord checks freight documents (invoice, packing list, certificate of origin, AWB/CMR) against each other and flags discrepancies before customs. Users are freight forwarders and customs brokers in Baku. They work fast, under pressure, and need to trust every flag.

**Design read:** B2B operations tool. Calm, precise, trust-first. Blue brand, data in mono, color used only for meaning.

---

## 1. Principles

1. **Evidence over opinion.** Every flag shows the value from each document and where it was found (page, field). Never show a verdict without its source.
2. **Color means status.** Blue is the brand and the action color. Orange, amber and green are reserved for discrepancy status. No decorative color.
3. **Show who decided.** Each finding says whether code (rule, arithmetic) or AI (semantic match) produced it.
4. **Fast scan.** A broker should see "3 errors, 1 to review" in under 2 seconds.

---

## 2. Color tokens

### Brand (blue)
| Token | Hex | Use |
|---|---|---|
| `navy-900` | `#0E1B3D` | Primary text, header background, logo plane |
| `cobalt-600` | `#1F45C9` | Primary buttons, active tab, selected row border, logo C |
| `cobalt-700` | `#18379F` | Primary button hover / pressed |
| `sky-400` | `#4C8DF6` | Accent, focus ring, logo variant, links on dark |
| `mist-50` | `#EEF2F9` | Page background |
| `white` | `#FFFFFF` | Surfaces (cards, panels, inputs) |
| `line-200` | `#D5DCE8` | Borders, dividers |
| `steel-600` | `#4A5670` | Secondary text, labels, metadata |

### Status (semantic, the only non-blue colors)
| Token | Text | Background | Meaning |
|---|---|---|---|
| `error` | `#9A3412` | `#FBE3D2` | Xəta: documents disagree, must be fixed |
| `warn` | `#7A5200` | `#FCEFC7` | Yoxlanmalı: AI is unsure, human must confirm |
| `ok` | `#1E6B4A` | `#E2F0E8` | Uyğun: documents agree |

Status colors are never used for anything else. Every status also carries a text label, never color alone.

### CSS variables
```css
:root {
  --navy-900: #0E1B3D;
  --cobalt-600: #1F45C9;
  --cobalt-700: #18379F;
  --sky-400: #4C8DF6;
  --mist-50: #EEF2F9;
  --surface: #FFFFFF;
  --line-200: #D5DCE8;
  --steel-600: #4A5670;
  --error-fg: #9A3412; --error-bg: #FBE3D2;
  --warn-fg: #7A5200;  --warn-bg: #FCEFC7;
  --ok-fg: #1E6B4A;    --ok-bg: #E2F0E8;
}
```

---

## 3. Typography

- **UI:** IBM Plex Sans (400, 500, 600)
- **Data:** IBM Plex Mono (400, 500) for every number, code, ID, weight, amount, AWB, VÖEN, HS code
- Load from Google Fonts: `family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500`

| Role | Size / weight | Notes |
|---|---|---|
| Page title | 28px / 600, tracking -0.02em | AWB number inside uses Mono 500 |
| Section title | 22px / 600 | |
| Finding title | 15px / 600 | |
| Body | 15px / 400, line-height 1.45 | max-width 65ch |
| Label / meta | 13-14px / 400, `steel-600` | |
| Big count (3 xəta) | Mono 32px / 500 | colored with status fg |

Never use Inter, Roboto or Arial. Never use a serif.

---

## 4. Logo

- **Mark:** letter C; its lower end turns into an airplane flying up and out of the C. Meaning: documents come together (concord) and the cargo leaves on time.
- **Colors:** C in `cobalt-600`, plane in `navy-900` on light. On `navy-900` background: C in `white`, plane in `sky-400`.
- **Wordmark:** "Concord" in IBM Plex Sans 600, tracking -0.01em, to the right of the mark.
- **Minimum size:** mark 32px. At 32px and below use the app icon (white C, navy plane on a `cobalt-600` rounded square, radius 22%); the plane's wings disappear under 24px.
- **Clear space:** half the C's height on all sides.
- **Files** (`/public/brand/`):
  - `concord-mark.svg` - mark on light backgrounds
  - `concord-mark-dark.svg` - mark on `navy-900` (white C, `sky-400` plane)
  - `concord-mark-mono.svg` - single color `navy-900` (fax, stamps, print)
  - `concord-lockup.svg`, `concord-lockup-dark.svg` - mark + "Concord" wordmark (text converted to outlines)
  - `concord-app-icon.svg`, `favicon-32.png` - app icon and favicon
- Never stretch, rotate, recolor outside these variants, or put the light mark on a busy photo.

---

## 5. Layout

- Max content width 1360px, side padding 32px (16px on mobile).
- Header: 64px, `navy-900` background, logo left, "Yeni yük" button right.
- Result screen:
  1. Shipment header: AWB, route, cargo, then three counts (xəta / yoxlanmalı / uyğun)
  2. Document chips row (one chip per uploaded document, with page count)
  3. Tabs: Uyğunsuzluqlar / Düzəliş məktubu
  4. Two columns: findings list (flex 1 1 380px) + detail panel (flex 999 1 560px). Stacks on mobile.
- Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64.
- Radius: 6px buttons and chips, 8px list rows and tables, 10px panels and drop zones. Nothing else.

---

## 6. Components

**Buttons**
- Primary: `cobalt-600` bg, white text, 600, height 44-48px, radius 6. Hover `cobalt-700`. Pressed `scale(0.98)`.
- Secondary: white bg, 1px `#A7B2C6` border, `navy-900` text, 500.
- Header button (on navy): `#1A2A55` bg, 1px `#2E3F6E` border, white text.
- One label per intent. Labels max 3 words.

**Status badge:** 12px / 600, padding 2px 8px, radius 4, status fg on status bg. Labels: Xəta, Yoxlanmalı, Uyğun.

**Finding row (button):** full width, padding 14px 16px, radius 8. Unselected: transparent bg, 1.5px `line-200` border. Selected: white bg, 1.5px `cobalt-600` border. Content: badge + field name, then title.

**Evidence table:** columns Sənəd / Dəyər / Harada. Header row `#F2F5FA`. Value in Mono 14px; the wrong value gets `error` bg and fg. Wrap in `overflow-x: auto`.

**Detail panel:** white, 1px `line-200`, radius 10, padding 28. Order: badge, title, summary, evidence table, "Kim aşkarladı" + "Təklif olunan düzəliş", actions.

**Drop zone:** 1.5px dashed `#A7B2C6`, `#F7F9FC` bg, radius 10, min-height 180. Real `<input type="file">` with a `<label>`.

**Passed checks:** small chips in `ok` colors, wrap.

---

## 7. States

- **Loading:** skeleton rows in the findings list and a skeleton table; text "Sənədlər oxunur..." then "Tutuşdurulur...". No spinners.
- **Empty:** upload screen with four document slots and a "Nümunə yükü aç" button.
- **Error (API/OCR failure):** inline in the panel: which document failed, why, and "Yenidən yoxla". Never a silent failure.
- **Low confidence:** finding goes to `warn` and says what the human should check.

---

## 8. Copy

- UI language: Azerbaijani. Document field names may stay in their original language ("Gross weight", "Consignee").
- Numbers: space as thousands separator, comma for decimals in Azerbaijani UI (`18 412,50 USD`, `1 284 kq`).
- Plain, functional sentences. No marketing verbs, no em-dashes, no emoji.
- Correction letter to shippers is in English.

---

## 9. Accessibility

- Text contrast at least 4.5:1 (3:1 for 24px+).
- Status never by color alone: always a text label.
- All interactive elements are real `<button>`, `<a>`, `<input>`. Touch targets at least 44px.
- Focus ring: 2px `sky-400` outline, 2px offset.
- Respect `prefers-reduced-motion`. Motion is limited to 150-200ms state transitions.
