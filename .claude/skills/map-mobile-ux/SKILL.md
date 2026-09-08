---
name: map-mobile-ux
description: Design rules for the public map at phone widths, resolved from Apple HIG, Material, Google Maps SDKs, Mapbox, WCAG and NN/g. Load before proposing any change to the mobile map: sheet, chips, legend, controls, clusters, touch targets, attribution.
metadata:
  rules: 2026-09-05
  type: domain
  reader: both
---

# map-mobile-ux

Rules for designing the public map (`nuxt/pages/mapa.vue`, `nuxt/components/map/`) on a phone. They come from six published sources that mostly agree; where they disagreed, the resolution is written here once, so nobody re-litigates it mid-session. Cartography (style, colour, hierarchy) and rendering cost are not this skill's: load `mapbox-cartography` and `mapbox-web-performance-patterns` (root `.claude/skills/`) for those.

This skill informs the dialogue with Ricardo. It never authorizes a creative solution: a rule cited here justifies a proposal, not an implementation. See «Before proposing a change» at the end.

Source tags: [Apple] `references/apple-hig.md` · [M2] [M3] `references/material.md` · [Google] `references/google-maps-sdk.md` · [Mapbox] `references/mapbox.md` · [WCAG] `references/wcag.md` · [NN/g] `references/nngroup.md`. Read a reference only when you need the argument around a rule.

The archived Material 2 bottom-sheet page was consulted in full: it adds the 8 dp elevation of a standard sheet co-existing with a panned region, the initial-appearance and full-screen behaviour, and the mobile→side-sheet scaling. It names no map or location case — that one is Material 3's — so `references/material.md` keeps only the [M2] passages the rules above cite, under their own heading.

## Vocabulary

Material's words are the skill's: **drag handle** and **preset heights**. Apple calls the same things *grabber* and *detents*; NN/g says *grab handle*. In code the term is **snap** (`snapPoints` in vaul-vue, the sheet library the panel uses). One pattern, four names.

## The sheet over the map

- **The sheet is a standard (non-modal) bottom sheet, elevated, without scrim.** It co-exists with the map so the user keeps panning and zooming with it open; Material names «location information over a map» as the canonical case. [M2, M3, NN/g]
- **The map keeps operating behind the sheet; nothing about the sheet may steal the map's gestures or focus.** Non-interactive elements that obscure the map break what people expect from a map. [Apple]
- **Initial and resting heights stay at or below half the screen.** Material caps the initial height of a modal sheet at 50 % so its top actions stay reachable; NN/g adds that sheets start non-modal in their minimized state. A sheet that opens near full height hides the map the user just navigated. [M3, NN/g]
- **Never open the sheet full-screen on arrival.** Tall content is reached by dragging; full height puts the top content out of thumb reach. [M2]
- **Preset heights are cycled by the drag handle, which is a button.** It sits in the tab order, toggles heights on Space/Enter, and is the only labelled part of the sheet. If a design has no drag handle, a visible single-pointer control must change the height instead. [M3 accessibility]
- **The top 48 dp of the sheet are the drag zone.** Anything placed there competes with the gesture. [M3 accessibility]
- **Never stack sheets.** The project detail must not open as a second sheet over the list: one swipe-down closes the whole stack and the user lands on a map they do not recognize. NN/g documents exactly this failure in Google Maps. Replace the content of the one sheet and give it a Back affordance. [NN/g]
- **A visible close (X) exists besides the swipe.** Swipe-down is supported but never the only dismissal: screen-reader and keyboard users cannot swipe, and users do not reliably discover the gesture. [NN/g]
- **At wide widths the bottom sheet becomes a side sheet.** Google's rationale is geometric: on desktop width exceeds height, so the panel should take width, not height. The map's `smAndDown` switch already encodes this. [M2]
- **At full height the sheet shows a collapse control in its app bar** to return to the initial position. [M3]

## Logical map padding

The canvas fills the whole container so dragging the sheet never reveals a seam; what the sheet covers is subtracted from the *logical* map, not from the canvas. Camera center, `fitBounds`, `getBounds`, control placement and attribution are computed over the uncovered region. Google exposes this as `setPadding`; Mapbox GL JS has the same model in `map.setPadding` and the `padding` option of `fitBounds`, `easeTo`, `flyTo`. [Google, Mapbox]

- **Re-apply the padding on every snap change**, not only on mount: a sheet at a different height covers a different region. [Google]
- **Padding is the legitimate way to move attribution and logo; hiding them is not.** Both Google and Mapbox forbid covering the copyright and logo permanently; temporary cover while a sheet is dragged is fine. Apple anchors its legal link to the lowest resting position of the card, which is the same idea. [Google, Apple, Mapbox]
- **Controls flow toward the nearest free corner** when their position collides with attribution. [Google]

## Chips over the canvas

- **Chips are elevated only when they sit on the map or an image; flat with an outline on plain surfaces.** [M3]
- **Never a single chip; chips come in a set.** [M3]
- **Horizontal scroll once the set would need more than two rows.** [M3]
- **Filter chips carry nouns naming what is included, 20 characters or fewer; no negatives.** [M3]
- **One selection mode per screen**: all chip sets single-select or all multi-select, never mixed. [M3]
- **On compact widths the whole chip is the tap target**, not a trailing icon. [M3]

## Controls

- **A map smaller than 200×200 px shows no controls.** Google hides them by default at that size; use it as the threshold for what survives when a sheet reduces the visible map. [Google]
- **Corner conventions**: zoom bottom-right, compass top-left and only when bearing or tilt is non-zero, locate top-right, marker toolbar bottom-right on selection. Use logical positions (start/end) so RTL works. [Google]
- **Bottom-right belongs to the map controls on this map.** Material would put a FAB there, but this map has no FAB. Whether the zoom buttons survive on phones (pinch already zooms) is undecided; it is Ricardo's call, not a convention. [Google, M2, resolved]
- **Cooperative gestures only when the map lives inside a scrolling page.** A full-screen map takes every gesture (`greedy`); a map embedded in a page requires two fingers or Ctrl so page scroll does not zoom it. Mapbox: `cooperativeGestures`. [Google]
- **Distinguish interactive elements from the map without hover**, and space them for imprecise taps. A label that shares the app's tint colour looks tappable. [Mapbox]

## Markers and clusters

- **Tapping a cluster zooms to the bounds of its children**; it does not open a list. The count lives on the cluster icon. Clusters dissolve into pins as zoom increases. [Google, Apple]
- **Selected elements get a distinct style** (outline plus colour), because on a phone there is no hover to confirm the selection. [Apple, Mapbox]
- **Progressive disclosure by zoom** is the mobile answer to density: fewer, larger things at low zoom. [Apple]

## Touch targets and legibility

- **Minimum tap target: 48 × 48 CSS px, with spacing for imprecise taps.** [M3, WCAG, Mapbox, resolved]
- **Translucent surfaces over the map must stay legible whatever the map shows underneath**: check contrast against satellite and against the lightest basemap area. [Mapbox]
- **Use a muted basemap when the map carries a lot of information-rich content that must stand out.** This map does: conflicts and pins over Mexico. [Apple]
- **Offer search combined with category filters** as the way to find places; that is the pattern both Apple and Google converge on. [Apple]

## The legend gap

No source covers a legend on a phone. Google Maps has none on mobile; Material and the Maps Platform documentation never mention the component; Apple and Mapbox treat colour as style, not as a key. Any decision about the legend (collapsed chip, section of the sheet, absent on mobile, something else) is made in dialogue with Ricardo, never by convention, and this skill offers no default.

What the accessibility literature does constrain, whatever the design (questions taken in our own words from the `maps` skill of https://github.com/mgifford/accessibility-skills, AGPL-3.0, so its text is not copied here): the legend is content, not decoration, so its text lives in HTML and describes the active layers; it is never the only structured way to read the map; every task, including reading and toggling the legend, must be completable with a single pointer; opening a popup moves focus into it; a cluster exposes an accessible name and its count. Legend labels on this map use `short_name` of the extractivism type, as the desktop legend already does.

## Contradictions and their resolutions

Four points where the sources disagree. Resolved once, here.

1. **Target size: 48 dp (Material) vs 44 pt (Apple) vs 24 CSS px (WCAG 2.2 AA).** Google's own text notes the discrepancy with iOS. Resolution: **48 px CSS**, which satisfies all three; 44 is Apple's and WCAG AAA, 24 is a floor, not a design value.
2. **Visible close button: NN/g requires it, Material 3 labels only the drag handle and reserves the close affordance for the full-screen state.** Resolution: **NN/g wins**; usability research outranks a design system on an accessibility point.
3. **Bottom-right corner: Material gives it to the FAB, Google Maps to the zoom controls.** Resolution: **map controls keep it** because this map has no FAB; zoom survival on mobile stays open.
4. **Vocabulary: detents/grabber (Apple) vs preset heights/drag handle (Material).** Resolution: **Material's words**, Apple's glossed, `snap` in code. Same pattern, not two.

Google and Mapbox contradict each other nowhere: padding model, attribution and gesture handling coincide.

## Before proposing a change

1. Name the rule you are applying and its tag; if no rule covers the case, say so instead of inventing one.
2. Check the rule against what the code does today (`nuxt/components/map/CLAUDE.md` lists the mechanisms and their gotchas); if skill and code disagree, raise it rather than silently follow either.
3. Present the proposal to Ricardo with the rule, the trade-off and what it changes on screen. Implement only after his yes.
