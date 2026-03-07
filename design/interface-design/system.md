# Domuscura — Interface Design System

## Intent

**Who:** A homeowner managing their own maintenance — practical, not precious. Using this at a desk, probably when something broke or they're doing their weekend todo list.

**What they accomplish:** See what's overdue, log that they did it, add things they noticed, track what they've spent.

**How it should feel:** Like a well-organized notebook. Warm, structured, and quiet — not a SaaS dashboard. Confidence, not delight.

---

## Design Direction

**Domain:** Home maintenance — wood, slate, plaster, pipe, soil. Physical things in a physical space.

**Color world:** The inside of a well-built house — warm plaster walls, slate tile, aged wood, dark iron fixtures.

**Signature:** Slate blue-gray as the single accent — the color of a slate roof tile, of galvanized pipe. Everything else recedes; this one color carries all interaction weight.

**Rejected defaults:** Bright teal (too SaaS), pure white backgrounds (too sterile), amber/orange accent (too alert-like for a primary color).

---

## Token System

### Brand
```css
--dm-slate:        #4a6b7a;   /* Slate roof tile — primary action color */
--dm-slate-dark:   #3a5668;   /* Hover state */
--dm-slate-tint:   rgba(74, 107, 122, 0.08);  /* Subtle backgrounds */
--dm-slate-focus:  rgba(74, 107, 122, 0.25);  /* Focus rings */
```

### Surfaces
```css
--dm-paper:        #fafaf8;   /* Warm off-white — page background */
--dm-paper-raised: #ffffff;   /* Cards, modals */
--dm-paper-inset:  #f1f1ee;   /* Input backgrounds, inset areas */
```

### Text
```css
--dm-ink:          #1e2a30;   /* Primary text — near-black with blue undertone */
--dm-ink-secondary:#546870;   /* Supporting text */
--dm-ink-muted:    #8a9da5;   /* Placeholders, disabled, metadata */
```

### Borders
```css
--dm-border:       rgba(74, 107, 122, 0.14);  /* Whisper-quiet, tinted with slate */
```

### Semantic
```css
--dm-ok:           #3d6a52;   /* Sage green — completed, healthy */
--dm-warning:      #c2711a;   /* Amber — due soon, caution */
--dm-danger:       #b83232;   /* Red — overdue, critical */
```

### Backward-compat aliases (do not remove)
```css
--color-warning:        var(--dm-warning);   /* status_badge.html */
--color-severity-major: #b35c00;             /* issues/list.html inline style */
```

---

## Dark Mode Tokens

```css
--dm-slate:        #7aaabb;
--dm-paper:        #192028;
--dm-paper-raised: #1f2c36;
--dm-paper-inset:  #141c23;
--dm-ink:          #e0eaed;
--dm-ink-secondary:#92adb8;
--dm-ink-muted:    #5c7a87;
--dm-border:       rgba(122, 170, 187, 0.14);
--dm-ok:           #5aaa7a;
--dm-warning:      #f0a64b;
--dm-danger:       #e06060;
```

---

## PicoCSS Overrides

```css
--pico-primary:              var(--dm-slate);
--pico-primary-hover:        var(--dm-slate-dark);
--pico-primary-focus:        var(--dm-slate-focus);
--pico-background-color:     var(--dm-paper);
--pico-card-background-color:var(--dm-paper-raised);
--pico-muted-color:          var(--dm-ink-muted);
--pico-muted-border-color:   var(--dm-border);
--pico-ins-color:            var(--dm-ok);
--pico-del-color:            var(--dm-danger);
--pico-font-size:            93.75%;   /* 15px base */
```

---

## Components

### Priority Badges
Inline chips on schedule names. Only shown for non-normal priorities.

```css
.priority-badge           /* base: small, uppercase, rounded */
.priority-badge--critical /* red tint */
.priority-badge--high     /* amber tint */
.priority-badge--low      /* slate tint */
```

Priority values from model: `critical`, `high`, `normal` (hidden), `low`

### Status Text
```css
.status-overdue     /* dm-danger, bold */
.status-due-soon    /* dm-warning, bold */
.status-ok          /* dm-ok */
.status-never-done  /* dm-ink-muted */
```

### Form Actions Row
Replaces `style="display: flex; gap: 0.5rem;"` on all form button rows.
Prevents PicoCSS `button { width: 100% }` default from stretching Save/Cancel.

```css
.form-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.form-actions button, .form-actions a[role="button"] { width: auto; }
```

### Filter Strip
```css
.filter-actions  /* flex row, compact button sizing */
```

### Spending Summary Grid
Forces 2×2 layout on the four summary cards regardless of viewport.
```css
.spending-summary { display: grid; grid-template-columns: 1fr 1fr; }
```
At ≤600px collapses to single column.

### Table Utilities
- `figure` — horizontal scroll wrapper
- `table th/td` — `white-space: nowrap` except first column
- `.col-mobile-hide` — hidden at ≤600px
- `.table-group-header` — section dividers (Overdue / Due Soon)
- `.btn-action` — 44px min touch target for table buttons
- `.btn-card` — card action buttons

---

## Depth Strategy

**Borders only.** No shadows. Fits the "structured notebook" intent — clean lines, no decoration.
Border: `rgba(74, 107, 122, 0.14)` — tinted with slate so it's not a neutral gray.

---

## Typography

PicoCSS defaults, scaled to 93.75% (15px base). No custom typeface — system font stack is appropriate for a personal utility tool.

---

## Spacing

PicoCSS spacing system (`--pico-spacing`). Base unit ~1rem. No custom spacing tokens needed at this scope.

---

## File: `maintenance/static/css/app.css`
Single CSS file. Loads after PicoCSS. Contains all tokens, overrides, and component classes. No inline styles in templates except the error toast in `base.html` (Alpine.js `x-show` requires inline positioning).
