# Material Design — bottom sheets and chips

Fetched 2026-09-07. Extracts, not a rewrite: the wording is the source's. Read this file only when a rule in SKILL.md cites it and you need the surrounding argument.

Material Design documentation is published under CC BY 4.0 (Google). Pages render client-side; extracted with a browser. Material's vocabulary: *preset heights* and *drag handle*.

Trimmed 2026-09-08 to what SKILL.md cites. Material 3 is the live system and carries the map case: «location information over a map» is a Material 3 line, not a Material 2 one. The Material 2 page was consulted in full and dropped except the three passages a [M2] rule rests on, kept below under their own heading; it says nothing about maps or location that Material 3 does not already say. The Material 3 specs page (tokens, colour roles, 640 dp measurements) is cited by no rule and is not extracted.

Sources:
- Material 3, bottom sheets, guidelines: https://m3.material.io/components/bottom-sheets/guidelines
- Material 3, bottom sheets, accessibility: https://m3.material.io/components/bottom-sheets/accessibility
- Material 3, chips, guidelines: https://m3.material.io/components/chips/guidelines
- Material 3, bottom sheets, specs (consulted, not extracted): https://m3.material.io/components/bottom-sheets/specs
- Material 2, Sheets: bottom (archived but live; consulted in full, partially extracted): https://m2.material.io/components/sheets-bottom

## Material 3 — bottom sheets, guidelines

### Standard bottom sheets

Standard bottom sheets co-exist with the screen’s main UI region and allow for simultaneously viewing and interacting with both regions, especially when the main UI region is frequently scrolled or panned.

Use a standard bottom sheet to display content that complements the screen’s primary content, such as an audio player in a music app.

At full-screen height, standard bottom sheets contain a collapse icon in an app bar to return to their initial position.

Standard bottom sheets can contain supplementary content that continues below the screen, such as location information over a map.

A bottom sheet can have preset positions from full-screen height to preview

### Modal bottom sheets — visibility

To provide access to its top actions, the initial vertical position of modal bottom sheets is capped at 50% of the screen height.

Modal bottom sheets whose contents exceed 50% of the screen height can then be pulled across the full screen and scrolled internally to access their remaining items.

The initial vertical position of modal bottom sheets can't exceed 50% of the screen height

Modal bottom sheets are above a scrim while standard bottom sheets don't have a scrim.

### Responsive layout

In compact breakpoints, like mobile devices, bottom sheets extend across the width of a screen and are elevated above the primary content.

For larger screens with medium and expanded breakpoints, bottom sheets have a default max-width to prevent undesired layouts and awkward spacing. However, this can be overridden if needed. For more complex tasks and flows, consider using a non-transient surface such as a floating sheet.

On larger expanded breakpoints, like desktop, a bottom sheet can be swapped for a side sheet that shows similar content.

Side sheets can contain the same content as bottom sheets and may be more suitable for desktop

### Behavior — custom positioning

The drag handle can be dragged or selected to change the bottom sheet height.

Sheets should be able to cycle through preset heights and close completely without dragging. Selecting the drag handle should toggle through preset heights or close the sheet, while selecting the scrim should always close the bottom sheet.

If the bottom sheet has multiple preset heights but can’t use a drag handle, Material requires the inclusion of a single-pointer alternative to change height.

Interacting with the drag handle can quickly move a bottom sheet through preset heights

A bottom sheet can automatically resize to another height after interacting with the drag handle

## Material 3 — bottom sheets, accessibility

### Use cases

Users should be able to:
- Resize bottom sheets without having to rely on touch gestures

### Interaction & style

**Touch target area.** The top 48dp portion of the bottom sheet is interactive when user-initiated resizing is available and the drag handle is present.

To ensure touch target accessibility, the top portion of a bottom sheet can be reserved for resize interactions

**Initial focus.** The optional drag handle can be focused in the tab order and interacted with using non-touch inputs, such as keyboard or switch controls.

**Dragging.** Include a single-pointer alternative for any action that can be completed by dragging.

Drag handles should cycle the bottom sheet through available heights when selected. If a drag handle can’t be used, add a button to do this action.

### Keyboard navigation

| Keys | Actions |
|---|---|
| Tab | Focus lands on drag handle |
| Space / Enter | Toggles between available heights |

### Labeling

Label only the drag handle. The accessibility role for the drag handle is “button.”

## Material 3 — chips, guidelines

### Usage

Chips help people enter information, make selections, filter content, or trigger actions. They're best used to help people accomplish their current task faster and easier.

Chips appear as a group of interactive elements

Multiple chips should appear together in a set, whereas there should be no more than 3 buttons in a single arrangement.

Chip sets can be scrolled horizontally.

Don’t display a single chip by itself. Chips should appear in a set.

### Anatomy — container

Shadows & elevation

Chip containers can be elevated if placed on top of an image or dynamic background.

When on complicated backgrounds, chip containers can be elevated

Use an outline to define the edge of the chip's container on regular backgrounds

Chips may use elevation when placed on an image

Chips shouldn't be elevated when placed directly on the page

Avoid using elevation to indicate a chip's pressed state. Instead, use the visual ripple effect.

### Anatomy — label text

Chip label text should be 20 characters or fewer, and have the same typography style as buttons.

Chip labels should remain brief for the limited space available. Skip conventional grammar rules, such as articles (take "a" walk), to save space.

Avoid chip labels longer than 20 characters

### Anatomy — trailing icon (optional, input and filter chips only)

Secondary actions (such as a trailing icon button for Remove) must have a 48x48dp interaction target that doesn’t interfere with the chip's primary action (such as Edit or Drag). To achieve this, apply a minimum width of 88dp to the chip, or 42dp to the label text.

### Filter chips

Filter chips use tags or descriptive words to filter content. They can be a good alternative to segmented buttons or checkboxes when viewing a list or search results.

Write filter chips with nouns that describe the category to include in the results. Avoid negative phrases like Exclude images.

Tap a chip to select it. Multiple chips can be selected or unselected.

Alternatively, a single chip can be selected. This offers an alternative to segmented buttons, radio buttons, or single select menus.

However, avoid mixing chip set behaviors. All chip sets on a page should be either single-select or multi-select.

In medium and expanded breakpoints, filter chips may contain a trailing icon to directly remove the chip or open a menu of options.

In compact windows, the trailing icon's target area is too small to be accessible on its own. However, if the whole chip can be selected to accomplish the action, the chip is likely still accessible.

In compact windows, make sure the whole chip opens the menu. Otherwise, the target area is likely too small to be accessible.

Filter chips can be used with other components, such as search fields and sheets.

Use a side sheet to organize many filter chips

Filter chips can wrap to a new row. If there are more than two rows, consider using horizontal scrolling to access them all.

Filter chips should not present only a single option

### Suggestion chips — placement and targets

When displaying multiple chips together, place them inline as a row of options, not listed vertically. Overflowing chips should break to the next line.

If the field is only one row high, chip sets can scroll horizontally instead.

Keep an 8dp minimum space between chips. Chips must also have a minimum 48dp target size, regardless of placement or density. If required, the target can extend beyond the visible container of the chip.

Text labels for chips should be concise. Chip labels will truncate when in a wrapped layout, and when they are wider than the full width of the window.

## Material 2 — Sheets: bottom (what [M2] rules rest on)

The archived page never names a map or a location: its map value is the generic «main UI region … scrolled or panned», which Material 3 states in the same words and then makes explicit. What survives here is only what a [M2] tag in SKILL.md cites.

### Standard bottom sheet — usage and interaction

Standard bottom sheets co-exist with the screen’s main UI region and allow for simultaneously viewing and interacting with both regions. They are commonly used to keep a feature or secondary content visible on screen when content in main UI region is frequently scrolled or panned.

Standard bottom sheets remain on-screen when a user interacts with the main UI region or the sheet itself. They have a default elevation of 8dp, which allows content in the main UI region behind to scroll or pan and for the sheet to temporarily cover the main UI region when made full-screen. At full-screen height, they should contain a collapse icon in an app bar to return to their initial position.

### Behavior — visibility

**Initial appearance.** When bottom sheets initially appear on screen, they may contain content that extends below the bottom of the screen. They can be swiped or dragged up to become full-screen. Depending on the content, bottom sheets can also become full-screen by tapping on their surface or an expand icon.

**Full-screen.** When full-screen, bottom sheets can be internally scrolled to reveal additional content. A toolbar should be used to provide a collapse or close affordance to exit this view.

To provide initial access to its top actions, the initial vertical position of modal bottom sheets is capped at 50% of the screen height.

### Scaling and adaptation, placement

On mobile devices, bottom sheets extend across the width of a screen and are elevated above the primary content. Bottom sheets should scale to fit larger screens in one of three ways:
- Setting a maximum width
- Switching to a floating sheet
- Switching to a side sheet to reduce the amount of space occupied on larger screens.

A bottom sheet on mobile can also be swapped for a side sheet that shows supporting content on larger screens.

The contents of standard bottom sheets on mobile can be moved into side sheets on larger screen sizes given the additional horizontal space.

### The bottom trailing corner (background for contradiction 3)

Expanding bottom sheets are fixed to the bottom, trailing corner of the screen to minimize obstructing the screen’s main content.

On mobile devices, an expanding bottom sheet affects other bottom-aligned components. It could obstruct important features such as bottom navigation, or create confusion when placed next to a floating action button.
