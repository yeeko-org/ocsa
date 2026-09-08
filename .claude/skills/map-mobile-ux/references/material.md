# Material Design — bottom sheets and chips

Fetched 2026-09-07. Extracts, not a rewrite: the wording is the source's. Read this file only when a rule in SKILL.md cites it and you need the surrounding argument.

Material Design documentation is published under CC BY 4.0 (Google). Pages render client-side; extracted with a browser. Material's vocabulary: *preset heights* and *drag handle*.

The Material 2 page is kept in full as a note: if a session proves it useful it graduates to a documenter reference; until then it lives here.

Sources:
- Material 2, Sheets: bottom (archived but live; the only page that names map + sheet as a canonical case): https://m2.material.io/components/sheets-bottom
- Material 3, bottom sheets, guidelines: https://m3.material.io/components/bottom-sheets/guidelines
- Material 3, bottom sheets, specs: https://m3.material.io/components/bottom-sheets/specs
- Material 3, bottom sheets, accessibility: https://m3.material.io/components/bottom-sheets/accessibility
- Material 3, chips, guidelines: https://m3.material.io/components/chips/guidelines

## Material 2 — Sheets: bottom (full extract)

# Sheets: bottom
Bottom sheets are surfaces containing supplementary content that are anchored to the bottom of the screen.
- Usage
- Anatomy
- Behavior
- Standard bottom sheet
- Modal bottom sheet
- Expanding bottom sheet
- Theming
- Specs
## Usage
Bottom sheets are supplementary surfaces primarily used on mobile. There are three types suitable for different use cases:
- Standard bottom sheets display content that complements the screen’s primary content. They remain visible while users interact with the primary content.
- Modal bottom sheets are an alternative to inline menus or simple dialogs on mobile and provide room for additional items, longer descriptions, and iconography. They must be dismissed in order to interact with the underlying content.
- Expanding bottom sheets provide a small, collapsed surface that can be expanded by the user to access a key feature or task. They offer the persistent access of a standard sheet with the space and focus of a modal sheet.
Containing content & links on a single subject
Related article
arrow_downward
Menus display a list of choices on temporary surfaces.
Surfaces containing supplementary content that are anchored to the left or right edge of the screen.
### Principles
#### Supporting
Bottom sheets contain content that supplements the screen’s primary UI region.
#### Flexible
Bottom sheets can display a wide variety of content and layouts.
#### Ergonomic
Bottom sheets are easy to reach on a mobile device.
## Anatomy
### Sheet
Bottom sheets are anchored to the bottom edge of the screen and appear in front of other UI elements. Standard and modal bottom sheets are...
Bottom sheets are anchored to the bottom edge of the screen and appear in front of other UI elements. Standard and modal bottom sheets are full-width on mobile and can be inset or full-width on tablet or desktop.
### Contents
Bottom sheets can display a wide variety of content and layouts, ranging from menu items (in list and grid layouts), to supplemental content laid out...
Bottom sheets can display a wide variety of content and layouts, ranging from menu items (in list and grid layouts), to supplemental content laid out according to the layout grid.
Content from a bottom sheet that initially appears below the screen edge can become visible when the sheet is dragged into view.
## Behavior
### Visibility
When bottom sheets initially appear on screen, they may contain content that extends below the bottom of the screen. They can be swiped or dragged...When bottom sheets initially appear on screen, they may contain content that extends below the bottom of the screen. They can be swiped or dragged...
#### Initial appearance
When bottom sheets initially appear on screen, they may contain content that extends below the bottom of the screen. They can be swiped or dragged up to become full-screen. Depending on the content, bottom sheets can also become full-screen by tapping on their surface or an expand icon.
#### Full-screen
When full-screen, bottom sheets can be internally scrolled to reveal additional content. A toolbar should be used to provide a collapse or close affordance to exit this view.
### Scaling and adaptation
On mobile devices, bottom sheets extend across the width of a screen and are elevated above the primary content. Bottom sheets should scale to fit larger screens...
On mobile devices, bottom sheets extend across the width of a screen and are elevated above the primary content. Bottom sheets should scale to fit larger screens in one of three ways:
- Setting a maximum width
- Switching to a floating sheet
- Switching to a side sheet to reduce the amount of space occupied on larger screens.
On large screens, bottom sheets that contain a set of actions can become a context menu to preserve the intent and context of the primary content.
A bottom sheet on mobile can also be swapped for a side sheet that shows supporting content on larger screens.
## Standard bottom sheet
### Usage
Standard bottom sheets co-exist with the screen’s main UI region and allow for simultaneously viewing and interacting with both regions. They are commonly used to...
Standard bottom sheets co-exist with the screen’s main UI region and allow for simultaneously viewing and interacting with both regions. They are commonly used to keep a feature or secondary content visible on screen when content in main UI region is frequently scrolled or panned.
### Behavior
Standard bottom sheets remain on-screen when a user interacts with the main UI region or the sheet itself. They have a default elevation of 8dp,...
#### Interaction
Standard bottom sheets remain on-screen when a user interacts with the main UI region or the sheet itself. They have a default elevation of 8dp, which allows content in the main UI region behind to scroll or pan and for the sheet to temporarily cover the main UI region when made full-screen. At full-screen height, they should contain a collapse icon in an app bar to return to their initial position.
### Placement
The contents of standard bottom sheets on mobile can be moved into side sheets on larger screen sizes given the additional horizontal space. Side sheets...
The contents of standard bottom sheets on mobile can be moved into side sheets on larger screen sizes given the additional horizontal space.
## Modal bottom sheet
Modal bottom sheets present a set of choices while blocking interaction with the rest of the screen. They are an alternative to inline menus and...
Modal bottom sheets present a set of choices while blocking interaction with the rest of the screen. They are an alternative to inline menus and simple dialogs on mobile, providing additional room for content, iconography, and actions.
Modal bottom sheets are used in mobile apps only.
Modal bottom sheets have a default elevation of 16dp. This elevation allows them to appear over most UI elements and allows them to be pulled...
#### Elevation and scrim
Modal bottom sheets have a default elevation of 16dp. This elevation allows them to appear over most UI elements and allows them to be pulled up in front of the entire UI to display more options.
A modal bottom sheet causes all content and UI elements behind it to display a scrim, which indicates that they will not respond to user interaction. Tapping the scrim dismisses both the modal bottom sheet and scrim from view.
#### Visibility
To provide initial access to its top actions, the initial vertical position of modal bottom sheets is capped at 50% of the screen height.
Modal bottom sheets whose contents exceed 50% of the screen height can then be pulled across the full screen, scrolling internally to access their remaining items.
#### Control
Modal bottom sheets appear when triggered by a user action, such as tapping a button or an overflow icon. They can be dismissed by:
- Tapping a menu item or action within the bottom sheet
- Tapping the scrim
- Swiping the sheet down
- Using a close affordance within the bottom sheet’s top app bar, if available
Modal bottom sheets are most effective on small screens. Menus display a list of choices on temporary surfaces. Related Article arrow_downward Dialogs inform users about...
Modal bottom sheets are most effective on small screens.
On larger screens, use menus or dialogs to create clear visual connections to the triggering UI element.
Dialogs inform users about a specific task and may contain critical information, require decisions, or involve multiple tasks. They remain until dismissed or a required action has been taken.
## Expanding bottom sheet
An expanding bottom sheet is a surface anchored to the bottom of the screen that users can expand to access a feature or task. It...
An expanding bottom sheet is a surface anchored to the bottom of the screen that users can expand to access a feature or task. It can be used for:
- Persistently displaying a cross-app feature, such as a shopping cart
- Collecting and acting on user selections from a set of items, such as photos in a gallery
- Supporting tasks, such as chat and comments
- Indirect navigation between items, such as videos in a playlist
Expanding bottom sheets are recommended for use on mobile and tablet.
Expanding bottom sheets and floating action buttons shouldn’t be used for the same purposes.
- Floating action buttons are used for actions only, and they don’t respond to a user’s interaction with the rest of the screen. They can transform into larger surfaces to allow a user to complete an action.
- Expanding bottom sheets transform into larger surfaces and can update their content to reflect user interactions.
### Anatomy
Expanding bottom sheets are anchored to the bottom corner of the screen. They have two states: a small, collapsed state and a larger, expanded state....
Expanding bottom sheets are anchored to the bottom corner of the screen. They have two states: a small, collapsed state and a larger, expanded state.
#### Collapsed
When collapsed, an expanding bottom sheet is intended to be small and informative.
- It can use shape and color to express that it is interactive.
- An icon is required at minimum, and larger screen sizes should also include a short text label.
- To avoid blocking content, the width shouldn’t exceed half the screen.
#### Expanded
When expanded, an expanding bottom sheet is full-screen on mobile (1), but can be smaller on tablet and desktop based on its content (2).
- It contains a fixed header with a title and an affordance to collapse the sheet.
Expanding bottom sheets can be expanded and collapsed.
#### Controls
- When collapsed, the entire container is interactive, and tapping it expands the sheet.
- Once expanded, the sheet displays an app bar with an action icon that enables collapsing the sheet. In addition, it can display a contextual action in the sheet that completes a task, such as “Checkout”, “Submit”, or “Download” buttons.
Expanding bottom sheets are fixed to the bottom, trailing corner of the screen to minimize obstructing the screen’s main content. On mobile devices, an expanding...
Expanding bottom sheets are fixed to the bottom, trailing corner of the screen to minimize obstructing the screen’s main content.
#### Mobile
On mobile devices, an expanding bottom sheet affects other bottom-aligned components. It could obstruct important features such as bottom navigation, or create confusion when placed next to a floating action button.
The following recommendations suggest when and how to pair an expanding bottom sheet with nearby components:
#### Tablet and desktop
On larger screens, expanding bottom sheets don’t need to expand to the screen’s height or width. At a smaller size, expanding bottom sheets enable multi-tasking and other uses of screen space.
As their placement at the bottom of the screen may make them less noticeable, their content can be placed in a side sheet or accessed from a top app bar.
## Theming
### Posivibes Material Theme
This social media app’s bottom sheets have been customized using Material Theming. Areas of customization include color and shape. Posivibe’s bottom sheets use custom color...
This social media app’s bottom sheets have been customized using Material Theming. Areas of customization include color and shape.
#### Color
Posivibe’s bottom sheets use custom color on three elements: container, text, and icons.
Create a color theme that reflects your brand or style
In a UI, color has a variety of roles: from containing meaning, to expressing a look and feel.
Direct attention, identify components, communicate state, and express brand
Related link
#### Shape
Posivibe’s bottom sheets use a custom container shape. Bottom sheets can only be shaped on the top left and top right corners.
### Shrine Material Theme
Shrine is a retail app, and its expanding bottom sheet has been customized using Material Theming. Areas of customization include color and shape. Shrine’s expanding...
Shrine is a retail app, and its expanding bottom sheet has been customized using Material Theming. Areas of customization include color and shape.
Shrine’s expanding bottom sheet uses custom colors on its container and icon.
The collapsed state of Shrine’s expanding bottom sheet uses a custom container shape. The top leading corner is shaped to help indicate it is interactive.*Expanding bottom sheets can only be shaped on the top left corner.
## Specs
#### Modal bottom sheet for mobile
- max-height 1/2 screen
Measurement max-height 1/2 screen
- 360 Measurement 360
- 16
Measurement 16
- 56
Measurement 56
- 36
Measurement 36
- Roboto
16dp
#0000008a
#000000de
- Elevation open_in_new
Elevation
- Components open_in_new
List
- General
Scrim
#000000 Opacity:32%
- #ffffff
R255 G255 B255
#### Standard bottom sheet for mobile
- min height: 56dp
Measurement min height: 56dp
8dp
Bottom sheets are available in the Material library for Jetpack Compose. Visit the library reference documentation on Android Developers to get started.
- open_in_newBottomSheetScaffold API Reference
- open_in_newModalBottomSheetLayout API Reference
## Using bottom sheets
Before you can use Material bottom sheets, you need to add a dependency to the
Material Components for Android library. For more information, go to the
Getting started
page.
Standard bottom sheet basic usage:
Modal bottom sheet basic usage:
More info on each individual section below.
### Setting behavior
There are several attributes that can be used to adjust the behavior of both
standard and modal bottom sheets.
In standard bottom sheets, they can be applied in xml by setting them on the
same child View that has the app:layout_behavior set on it, or
programmaticaly like so:
In modal bottom sheets they can be applied via app-level theme attributes and
styles:
Or programmaticaly like so:
More info about these attributes and their default values in the
behavior attributes section.
### Retaining behavior on configuration change
In order to save and restore specific behaviors of the bottom sheet on
configuration change, the following flags can be set (or combined with bitwise
OR operations):
- SAVE_PEEK_HEIGHT: app:behavior_peekHeight is preserved.
- SAVE_HIDEABLE: app:behavior_hideable is preserved.
- SAVE_SKIP_COLLAPSED: app:behavior_skipCollapsed is preserved.
- SAVE_FIT_TO_CONTENTS: app:behavior_fitToContents is preserved.
- SAVE_ALL: All aforementioned attributes are preserved.
- SAVE_NONE: No attribute is preserved. This is the default value.
That can be done in code like so:
Or in xml via the app:behavior_saveFlags attribute.
### Setting state
Standard and modal bottom sheets have the following states:
- STATE_COLLAPSED: The bottom sheet is visible but only showing its peek
height. This state is usually the 'resting position' of a bottom sheet, and
should have enough height to indicate there is extra content for the user to
interact with.
- STATE_EXPANDED: The bottom sheet is visible at its maximum height and it
is neither dragging or settling (see below).
- STATE_HALF_EXPANDED: The bottom sheet is half-expanded (only applicable if
behavior_fitToContents has been set to false), and is neither dragging or
settling (see below).
- STATE_HIDDEN: The bottom sheet is no longer visible and can only be
re-shown programmatically.
- STATE_DRAGGING: The user is actively dragging the bottom sheet up or down.
- STATE_SETTLING: The bottom sheet is settling to specific height after a
drag/swipe gesture. This will be the peek height, expanded height, or 0, in
case the user action caused the bottom sheet to hide.
You can set a state on the bottom sheet like so:
Note: STATE_SETTLING and STATE_DRAGGING should not be set programmatically.
### Listening to state and slide changes
A BottomSheetCallback can be added to a BottomSheetBehavior like so:
### Handling insets and fullscreen
BottomSheetBehavior can automatically handle insets (such as for
edge to edge) by
specifying any of:
- app:paddingBottomSystemWindowInsets
- app:paddingLeftSystemWindowInsets
- app:paddingRightSystemWindowInsets
- app:paddingTopSystemWindowInsets
to true on the view.
On API 21 and above the modal bottom sheet will be rendered fullscreen (edge to
edge) if the navigation bar is transparent and app:enableEdgeToEdge is true.
It can automatically add insets if any of the padding attributes above are set
to true in the style, either by updating the style passed to the constructor, or
by updating the default style specified by the ?attr/bottomSheetDialogTheme
attribute in your theme.
BottomSheetDialog will also add padding to the top when the bottom sheet
slides under the status bar to prevent content from being drawn underneath it.
### Making bottom sheets accessible
The contents within a bottom sheet should follow their own accessibility
guidelines, such as images having content descriptions set on them.
Standard bottom sheets co-exist with the screen’s main UI region and allow for
simultaneously viewing and interacting with both regions. They are commonly used
to keep a feature or secondary content visible on screen when content in main UI
region is frequently scrolled or panned.
BottomSheetBehavior is applied to a child of
CoordinatorLayout
to make that child a persistent bottom sheet, which is a view that comes up
from the bottom of the screen, elevated over the main content. It can be dragged
vertically to expose more or less of their content.
API and source code:
- BottomSheetBehaviorClass definitionClass source
- Class definition
- Class source
### Standard bottom sheet example
The following example shows a standard bottom sheet in its collapsed and
expanded state:
BottomSheetBehavior works in tandem with CoordinatorLayout to let you
display content on a bottom sheet, perform enter/exit animations, respond to
dragging/swiping gestures, etc.
Apply the BottomSheetBehavior to a direct child View of CoordinatorLayout
like so:
In this example, the bottom sheet is in fact the FrameLayout.
Modal bottom sheets present a set of choices while blocking interaction with the
rest of the screen. They are an alternative to inline menus and simple dialogs
on mobile, providing additional room for content, iconography, and actions.
BottomSheetDialogFragment is a thin layer on top of the regular support
library Fragment that renders your fragment as a modal bottom sheet,
fundamentally acting as a dialog.
Modal bottom sheets render a shadow on the content below them to indicate that
they are modal. If the content outside of the dialog is tapped then the bottom
sheet is dismissed. Modal bottom sheets can be dragged vertically and dismissed
by completely sliding them down.
- BottomSheetDialogFragmentClass definitionClass source
### Modal bottom sheet example
The following example shows a modal bottom sheet in its collapsed and expanded
state:
First, subclass BottomSheetDialogFragment and overwrite onCreateView to
provide a layout for the contents of the sheet (in this example, it's
modal_bottom_sheet_content.xml):
Then, inside an AppCompatActivity, to show the bottom sheet:
BottomSheetDialogFragment is a subclass of AppCompatFragment, which means
you need to use Activity.getSupportFragmentManager().
Note: Don't call setOnCancelListener or setOnDismissListener on a
BottomSheetDialogFragment, instead you can override
onCancel(DialogInterface) or onDismiss(DialogInterface) if necessary.
## Anatomy and key properties
Bottom sheets have a sheet, content, and, if modal, a scrim.
- Sheet
- Content
- Scrim (in modal bottom sheets)
### Sheet attributes
### Behavior attributes
More info about these attributes and how to use them in the
setting behavior section.
To save behavior on configuration change:
### Styles
Default style theme attribute:?attr/bottomSheetStyle
### Theme overlays
Default theme overlay attribute: ?attr/bottomSheetDialogTheme
See the full list of
styles,
attrs,
and
themes and theme overlays.
## Theming bottom sheets
Bottom sheets support
Material Theming and can
be customized in terms of color and shape.
### Bottom sheet theming example
The following example shows a bottom sheet with Material Theming, in its
collapsed and expanded states.
#### Implementing bottom sheet theming
Setting the theme attribute bottomSheetDialogTheme to your custom
ThemeOverlay will affect all bottom sheets.
In res/values/themes.xml:
In res/values/styles.xml:
Note: The benefit of using a custom ThemeOverlay is that any changes to your
main theme, such as updated colors, will be reflected in the bottom sheet (as
long as they're not overridden in your custom theme overlay). If you use a
custom Theme instead (by extending from one of the
Theme.MaterialComponents.*.BottomSheetDialog variants) you have more control
over exactly what attributes are included in each, but it also means you'll have
to duplicate any changes that you've made in your main theme into these as well.
Bottom sheets are supplementary surfaces primarily used on mobile.
Before you can use bottom sheets, you need to import the Material Components package for Flutter:
You need to be using a MaterialApp.
For more information on getting started with the Material for Flutter, go to the Flutter Material library page.
Flutter's APIs support accessibility setting for large fonts, screen readers, and sufficient contrast. For more information, go to Flutter's accessibility and internationalization pages.
For more guidance on writing labels, go to our page on how to write a good accessibility label.
## Types
There are three types of bottom sheets: 1. Standard bottom sheets 2. Modal bottom sheets 3. Expanding bottom sheets
BottomSheet
- GitHub source
- Dartpad demo
The following is an example expanded standard bottom sheet:
The persistent bottom sheet can be used for a standard bottom sheet.
Use a DraggableScrollableSheet for more custom dragging and snap points.
### Anatomy and key properties
The following shows the anatomy of a standard bottom sheet:
- Contents
#### Sheets properties
#### Contents properties
There are no specific properties for content because the content can be any composition of widgets.
The following is an example modal bottom sheet:
The following shows the anatomy of a modal bottom sheet:
#### Scrim properties
Expanding bottom sheets provide a small, collapsed surface that can be expanded by the user to access a key feature or task to offer the persistent access of a standard sheet with the space and focus of a modal sheet.
Expanding bottom sheets require creating a custom widget. See Expanding bottom sheet for more info.
Bottom Sheets support Material Theming and can be customized in terms of color, elevation and shape.
Source code API:
Theming for bottom sheet content can be done by theming the widgets that are inside the widget returned by the builder of showBottomSheet or showModalBottomSheet.
- The widget used for list items is commonly a ListTile, and can be themed with ListTileTheme.
- Other Texts and Icons can be themed with TextTheme and IconTheme.
The following shows a modal bottom sheet with Shrine theming:
As of July 15 2021, Material's iOS libraries are in maintenance mode. Learn more.
### Installing
In order to install with Cocoapods, first add the component to your Podfile:
Then run the installer:
From there, import the relevant target or file.
#### Swift
#### Objective-C
As a user of the bottom sheet component, it is up to you to determine that its contents are accessible. The bottom sheet ccomponent does not have any specific APIs for managing the accessibility of a bottom sheet's contents. MDCBottomSheetController does, however, have such APIs for the scrim:
- isScrimAccessibilityElement
- scrimAccessibilityLabel
- scrimAccessibilityHint
- scrimAccessibilityTraits
We recommend giving all of these properties appropriate values for your use case.
Types
There are three types suitable for different use cases:
- Standard bottom sheets display content that complements the screen’s primary content and remain visible while users interact with the primary content
- Modal bottom sheets are an alternative to inline menus or simple dialogs on mobile and provide room for additional items, longer descriptions, and iconography, and must be dismissed in order to interact with the underlying content
Note: Standard bottom sheets aren't supported on iOS. This is because the iOS bottom sheet implementation makes use of custom view controller transitions, which do not allow interaction with the presenting view controller, even when the presented view controller does not take up the whole screen.
### Modal bottom sheet examples
#### Basic modal sheet example
Use MDCBottomSheetController and its accompanying presentation controller class, MDCBottomSheetPresentationController, to achieve a modal bottom sheet on iOS.
- MDCBottomSheetControllerGitHub source
- MDCBottomSheetPresentationController GitHub source
Something like the above example can be achieved using the code below.
#### Behavioral customizations
You can also choose to have your bottom sheet not be dismissable when dragged downwards by using the dismissOnDraggingDownSheet property on MDCBottomSheetController.
Note: A bottom sheet similar to the one shown above is easily attainable with the ActionSheet component, which makes use of MDCBottomSheetPresentationController.
#### Sheet properties
### Expanding bottom sheet example
To generate an expanding bottom sheet on iOS, set the trackingScrollView property on your MDCBottomSheetController. If the contentSize of the scroll view has a large enough height the bottom sheet will expand to the top.
Unlike most Material components on iOS, bottom sheets do not offer theming with a container scheme. However, MDCBottomSheetController does have a shape themer. In order to use the shape themer, first add the following to your Podfile:
Next, import the relevant taret or file and call the correct theming method.
## Up next
### COMPONENTS
#### Sheets: side
#### Backdrop
#### Navigation drawer

## Material 3 — bottom sheets, guidelines

# Bottom sheets
- Usage
- Anatomy
- Standard bottom sheets
- Modal bottom sheets
- Responsive layout
- Behavior
## Usage
Bottom sheets display supplementary content and actions on a mobile screen.
Bottom sheet containing contacts and applications
Bottom sheets are a versatile component that can contain a wide variety of information and layouts, including menu items (in list or grid layouts), actions, and supplemental content.
Bottom sheet with menu items in a list
## Anatomy
A container is the only required element of a bottom sheet. Bottom sheet layouts can vary widely to support the kinds of content they contain.
- Container
- Drag handle (optional)
- Scrim (modal only)
### Container
Bottom sheet containers hold all bottom sheet elements. Their size is determined by the space those elements occupy.
The container is the only required element of a bottom sheet. All other elements are optional.
Bottom sheets are flexible containers that adapt to their content and available space
### List items (optional)
Lists are a continuous group of text or images. List items can include label text, icons, and text buttons, among other elements.
Bottom sheet containing a list with icons
### Dividers (optional)
Dividers can be used to separate related content in bottom sheets.
Bottom sheet with a divider separating kinds of actions
### Media (optional)
Thumbnail
Bottom sheets can include thumbnails for an avatar or logo.
Image
Bottom sheets can include photos, illustrations, and other graphics, such as weather icons.
Video
Bottom sheets can include video.
Bottom sheets can contain thumbnails, images, and video
## Standard bottom sheets
Standard bottom sheets co-exist with the screen’s main UI region and allow for simultaneously viewing and interacting with both regions, especially when the main UI region is frequently scrolled or panned.
Use a standard bottom sheet to display content that complements the screen’s primary content, such as an audio player in a music app.
The music player in this standard bottom sheet allows people to control their music while browsing albums
At full-screen height, standard bottom sheets contain a collapse icon in an app bar to return to their initial position.
Standard bottom sheets can contain supplementary content that continues below the screen, such as location information over a map.
A bottom sheet can have preset positions from full-screen height to preview
## Modal bottom sheets
Like dialogs, modal bottom sheets appear in front of app content, disabling all other app functionality when they appear, and remaining on screen until confirmed, dismissed, or a required action has been taken.
A modal bottom sheet must be interacted with or dismissed. Its blocking behavior makes it suitable for a menu, such as in this files app, to help people focus on their available choices.
Use a modal bottom sheet as an alternative to inline menus or simple dialogs on mobile, especially when offering a long list of action items, or when items require longer descriptions and icons.
Modal bottom sheets are used in mobile apps only.
Modal bottom sheets can be used instead of menus to present additional actions
### Visibility
To provide access to its top actions, the initial vertical position of modal bottom sheets is capped at 50% of the screen height.
Modal bottom sheets whose contents exceed 50% of the screen height can then be pulled across the full screen and scrolled internally to access their remaining items.
The initial vertical position of modal bottom sheets can't exceed 50% of the screen height
Modal bottom sheets appear when triggered by a user action, such as tapping a button or an overflow icon. They can be dismissed by:
- Tapping a menu item or action within the bottom sheet
- Tapping the scrim
- Swiping the sheet down
- Using a close affordance within the bottom sheet’s app bar, if available
Display a close affordance in a full-screen modal bottom sheet.
Tapping the scrim dismisses a modal bottom sheet
A modal bottom sheet can be dismissed by swiping the sheet down
## Responsive layout
### Compact breakpoint
In compact breakpoints, like mobile devices, bottom sheets extend across the width of a screen and are elevated above the primary content.
Bottom sheets should extend to the width of the screen on mobile
### Medium and expanded breakpoints
For larger screens with medium and expanded breakpoints, bottom sheets have a default max-width to prevent undesired layouts and awkward spacing. However, this can be overridden if needed. For more complex tasks and flows, consider using a non-transient surface such as a floating sheet.
Bottom sheets on larger screens like tablet have a max width that can be overridden
On larger expanded breakpoints, like desktop, a bottom sheet can be swapped for a side sheet that shows similar content.
Side sheets can contain the same content as bottom sheets and may be more suitable for desktop
## Behavior
Bottom sheets can offer an expansion option where the sheet is fully raised and toggled between a collapsed and expanded state. This provides a more predictable footprint of the sheet, and can be set by the system or toggled by the user.
A bottom sheet for sharing can appear fully raised if needed
Alternately, a bottom sheet for sharing can appear collapsed for a more focused set of actions
### Custom positioning
The drag handle can be dragged or selected to change the bottom sheet height.
Sheets should be able to cycle through preset heights and close completely without dragging. Selecting the drag handle should toggle through preset heights or close the sheet, while selecting the scrim should always close the bottom sheet.
If the bottom sheet has multiple preset heights but can’t use a drag handle, Material requires the inclusion of a single-pointer alternative to change height.
Interacting with the drag handle can quickly move a bottom sheet through preset heights
A bottom sheet can automatically resize to another height after interacting with the drag handle
### Scrolling
Bottom sheets can be horizontally scrolled, independent of the rest of the screen’s content.
Bottom sheets should be scrollable when their content exceeds the initial viewable height
### Back
On Android, a gesture called predictive back allows a user to swipe left or right on the bottom sheet.
- Bottom sheet detaches from the left and right edges of the screen to signal it will close
- Previous screen is revealed in a preview
A list of compatible components is available in the gestures article.
Preview of the result of the gesture, release to commit, fling to commit, and cancel
Material Design is an adaptable system of guidelines, components, and tools that support the best practices of user interface design. Backed by open-source code, Material Design streamlines collaboration between designers and developers, and helps teams quickly build beautiful products.
- Social
### Social
- GitHub
- YouTube
- Blog RSS
- Libraries
### Libraries
- Android
- Compose
- Flutter
- Web
- More Google sites
### More Google sites
- Google Design
- Archived versions
### Archived versions
- Material Design 1
- Material Design 2
- Privacy Policy
- Terms of Service
- Join research studies
- Feedback

## Material 3 — bottom sheets, specs

# Bottom sheets
- Tokens and specs
- Color
- Measurements
Modal bottom sheets are above a scrim while standard bottom sheets don't have a scrim. Besides this, both variants of bottom sheets have the same specs.
- Container
- Drag handle (optional)
- Scrim
## Tokens and specs
Browse the component elements, attributes, tokens, and their values. Learn more about design tokens
## Color
Color values are implemented through design tokens. For design, this means working with color values that correspond with tokens. For implementation, a color value will be a token that references a value. Learn more about design tokens
Bottom sheet color roles used for both light and dark schemes:
- Scrim*
- On surface variant
- Surface container low
*On Android platforms, the scrim color and opacity is automatically handled by the system UI.
## Measurements
Bottom sheet padding and size measurements
Bottom sheets span the full window width up to 640dp. When the window width exceeds 640dp, bottom sheets adjust to have a top margin of 56dp and side margins of 56dp.
| Attribute
| Value
| Drag handle alignment (horizontal)
Drag handle alignment (horizontal)
| Center
Center
| Drag handle padding top/bottom
Drag handle padding top/bottom
| 22dp
22dp
| Top margin
Top margin
| 72dp
72dp
| Top margin (window width > 640dp)
| 56dp
| Start/end margin (window width > 640dp)
Start/end margin (window width > 640dp)
56dp
| Width
Width
| Full width, up to max-width 640dp
Full width, up to max-width 640dp
| Height
| Variable
Material Design is an adaptable system of guidelines, components, and tools that support the best practices of user interface design. Backed by open-source code, Material Design streamlines collaboration between designers and developers, and helps teams quickly build beautiful products.
- Social
### Social
- GitHub
- YouTube
- Blog RSS
- Libraries
### Libraries
- Android
- Compose
- Flutter
- Web
- More Google sites
### More Google sites
- Google Design
- Archived versions
### Archived versions
- Material Design 1
- Material Design 2
- Privacy Policy
- Terms of Service
- Join research studies
- Feedback

## Material 3 — bottom sheets, accessibility

# Bottom sheets
- Use cases
- Interaction & style
- Keyboard navigation
- Labeling
## Use cases
Users should be able to:
- Resize bottom sheets without having to rely on touch gestures
## Interaction & style
### Touch target area
The top 48dp portion of the bottom sheet is interactive when user-initiated resizing is available and the drag handle is present.
To ensure touch target accessibility, the top portion of a bottom sheet can be reserved for resize interactions
### Initial focus
The optional drag handle can be focused in the tab order and interacted with using non-touch inputs, such as keyboard or switch controls.
Visible focus shown on the drag handle affordance
### Dragging
Include a single-pointer alternative for any action that can be completed by dragging.
Drag handles should cycle the bottom sheet through available heights when selected. If a drag handle can’t be used, add a button to do this action.
Interacting with the drag handle can quickly move a bottom sheet through preset heights
A bottom sheet can automatically resize to another height after interacting with the drag handle
## Keyboard navigation
| Keys
| Actions
| Tab
| Focus lands on drag handle
| Space / Enter
| Toggles between available heights
## Labeling
Label only the drag handle. The accessibility role for the drag handle is “button.”
Label the drag handle
Material Design is an adaptable system of guidelines, components, and tools that support the best practices of user interface design. Backed by open-source code, Material Design streamlines collaboration between designers and developers, and helps teams quickly build beautiful products.
- Social
### Social
- GitHub
- YouTube
- Blog RSS
- Libraries
### Libraries
- Android
- Compose
- Flutter
- Web
- More Google sites
### More Google sites
- Google Design
- Archived versions
### Archived versions
- Material Design 1
- Material Design 2
- Privacy Policy
- Terms of Service
- Join research studies
- Feedback

## Material 3 — chips, guidelines

# Chips
- Usage
- Anatomy
- Assist chips
- Filter chips
- Input chips
- Suggestion chips
There are four variants of chips: Assist, filter, input, and suggestion
## Usage
Chips help people enter information, make selections, filter content, or trigger actions. They're best used to help people accomplish their current task faster and easier.
Chips appear as a group of interactive elements
### Chips aren’t buttons
Chips and buttons are similar. They both provide visual cues to prompt people to take actions and make selections.
While buttons appear consistently and with familiar calls to action, chips are dynamic to the situation, and appear as a group of interactive elements.
Use chips to enhance a person's current journey and encourage action. Use buttons to progress them through the product and for significant actions.
Use chips to present contextual, supplemental options
Avoid replacing major actions with chips. Actions that progress people to the next or previous step should always be displayed as buttons.
Chips should dynamically offer various actions depending on the current task, whereas a button should be a persistent fixture of a layout.
Chips represent forking paths for a current task, while buttons represent linear steps.
Use buttons for the final step in a task
Avoid using chips to finish or progress a task
Multiple chips should appear together in a set, whereas there should be no more than 3 buttons in a single arrangement.
Chip sets can be scrolled horizontally.
Chips can be scrolled horizontally
Don’t display a single chip by itself. Chips should appear in a set.
### Variants
Choose the chip variant based on its purpose and author.
Does the chip represent an action (assist chip) or filter results (filter chip)?
Is its content generated by the product (suggestion chip), or by the person using the product (input chip)?
There are four chip variants:
- Assist
- Filter
- Input
- Suggestion
| Purpose
Purpose
| Chip variant
Chip variant
| Rationale
Rationale
| Example
Example
| Action
Action
| Assist chip
Assist chip
| Assist chips represent smart or automated actions that can span multiple apps
Assist chips represent smart or automated actions that can span multiple apps
| Add to calendar action
Add to calendar action
| Filter
| Filter chip
Filter chip
| Filter chips represent filters for a collection
Filter chips represent filters for a collection
| Platform selector on material.io/components
Platform selector on material.io/components
| Information, user-authored
Information, user-authored
| Input chip
Input chip
| Input chips represent discrete pieces of information entered by a person
Input chips represent discrete pieces of information entered by a person
| Gmail contact in the To field
Gmail contact in the To field
| Information, product-authored
Information, product-authored
| Suggestion chip
Suggestion chip
| Suggestion chips help narrow a person’s intent by presenting dynamically-generated suggestions
Suggestion chips help narrow a person’s intent by presenting dynamically-generated suggestions
| Suggested chat response
Suggested chat response
## Anatomy
- Container
- Label text
- Leading icon or image (optional)
- Trailing icon (required for input chips, optional for filter chips)
### Container
All chips are slightly rounded with an 8dp corner.
Chips have rounded corners
Shadows & elevation
Chip containers can be elevated if placed on top of an image or dynamic background.
When on complicated backgrounds, chip containers can be elevated
Use an outline to define the edge of the chip's container on regular backgrounds
Chips may use elevation when placed on an image
Chips shouldn't be elevated when placed directly on the page
Avoid using elevation to indicate a chip's pressed state. Instead, use the visual ripple effect.
### Label text
Chip label text should be 20 characters or fewer, and have the same typography style as buttons.
Chip labels should remain brief for the limited space available. Skip conventional grammar rules, such as articles (take "a" walk), to save space.
Keep chip labels short
Avoid chip labels longer than 20 characters
### Leading icon or image (optional)
Chips can contain a leading icon, logo, or circular image. Use a system icon to help identify a chip's category.
Chips can contain a logo, icon, or circular image
The leading icon color for unselected chips can be customized through theming. While the default color role is primary, the on surface variant color role is a good alternative when the icon style requires less emphasis.
Primary color (left) and on surface variant color (right)
Leading circular images are sized larger than leading icons to provide more space for detail. Icons are designed to be legible at small sizes.
See the Specs tab for precise measurement values.
Leading images, such as avatars, are sized larger than leading icons or logos
### Trailing icon (optional, input and filter chips only)
The trailing icon is present for input and filter chips.
On input chips, it's required and must be used to remove the chip. On filter chips, it's optional, and can be used to open a menu or remove the chip.
Secondary actions (such as a trailing icon button for Remove) must have a 48x48dp interaction target that doesn’t interfere with the chip's primary action (such as Edit or Drag). To achieve this, apply a minimum width of 88dp to the chip, or 42dp to the label text.
Interaction targets for actions like Edit or Close have a size of 48x48. This can be achieved by setting the minimum container width to 88dp.
## Assist chips
Assist chips represent smart or automated actions that can span multiple apps, such as opening a calendar event from the home screen. Assist chips function as though the person asked an assistant to complete the action. They should appear dynamically and contextually in a UI.
An alternative to assist chips are buttons, which should appear persistently and consistently.
The text in most assist chips begins with a short verb, like Get or Add
An assist chip can surface supplemental information like a calendar event, as well as provide contextual actions
During an interaction, assist chips can transform into modals, transition into full-screen views of new content, or readjust to display more results inline
Assist chips can trigger an action or show progress and confirmation.
Write assist chips like buttons: start with a verb. Adjust text dynamically if the state changes, like Save to Saved.
Tapping an assist chip triggers a contextual action
Assist chips can show progress and confirmation feedback
Assist chips are displayed after primary content, such as below a card or persistently at the bottom of a screen.
Assist chips should be shown underneath primary content
## Filter chips
Filter chips use tags or descriptive words to filter content. They can be a good alternative to segmented buttons or checkboxes when viewing a list or search results.
Tapping on a filter chip activates it and appends a leading checkmark icon to the starting edge of the chip label.
Write filter chips with nouns that describe the category to include in the results. Avoid negative phrases like Exclude images.
Filter chips rely on tags or descriptive words to filter content
Filter chips in a shopping app
Filter chips in a real estate app
Tap a chip to select it. Multiple chips can be selected or unselected.
An icon can be added to indicate when a filter chip is selected
Filter chip suggestions can dynamically change as a person starts to select filters
Alternatively, a single chip can be selected. This offers an alternative to segmented buttons, radio buttons, or single select menus.
However, avoid mixing chip set behaviors. All chip sets on a page should be either single-select or multi-select.
Filter chips can be set so that selecting a single chip automatically deselects all other chips in the set
In medium and expanded breakpoints, filter chips may contain a trailing icon to directly remove the chip or open a menu of options.
In compact windows, the trailing icon's target area is too small to be accessible on its own. However, if the whole chip can be selected to accomplish the action, the chip is likely still accessible.
The remove icon helps users remove the filter
Filter chips can open a menu for more filtering options
When combined with a menu, the filter chip opens a list of selectable options.
In compact windows, make sure the whole chip opens the menu. Otherwise, the target area is likely too small to be accessible.
Filter chips can be used with other components, such as search fields and sheets.
Filter chips can be shown underneath a search field
Use a side sheet to organize many filter chips
Filter chips can wrap to a new row. If there are more than two rows, consider using horizontal scrolling to access them all.
Filter chips can scroll horizontally to show many options
Filter chips should not present only a single option
## Input chips
Input chips represent discrete pieces of information entered by a person, such as Gmail contacts or filter options within a search field.
They enable user input and verify that input by converting text into chips.
Input chips transform text based on a person's input
Input chips can support editing to change their contents, such as correcting an email address. In edit mode, the chip reverts back to a text string. Editing can be triggered by interacting with the chip, either by selecting it or by a second interaction after selection.
Input chips converted from email addresses are editable
Using the backspace key with the cursor before a chip selects the entire chip. The chip can then be deleted when the user taps the backspace key again.
A single field can contain multiple input chips. These chips can be reordered or moved into other fields.
Multiple input chips in one field
Input chips being moved from one field to another
Input chips can expand to show more information or options. A container transform transition pattern is used to reveal additional content.
Input chips can expand
### Placement
Input chips can be integrated with other components.
They can appear:
- Inline with the cursor in a text field
- In a stacked list
- In a list that can be horizontally scrolled
Input chips can wrap to a new row if all chips need to be visible
Input chips can scroll horizontally
### Icons & images
The leading icon of input chips can be an icon, logo, or circular image.
Input chips can contain an icon, logo, or circular image
The trailing icon is always aligned to the end side of the container. It’s placed:
- On the right for left-to-right (LTR) languages, such as English
- On the left for right-to-left (RTL) languages, such as Farsi
Input chips can be a more flexible way to filter search results, compared to filter chips
Input chips make it easier to add and remove contacts
Overflowed chips in a text field should follow the same behavior as regular text. An unfocused text field with overflowed content should display the beginning of the input. Tapping the field snaps the user to the end of the input with the cursor and keyboard active.
## Suggestion chips
Suggestion chips help narrow a user’s intent by presenting dynamically generated suggestions, such as possible responses or search filters.
Write suggestion chips as nouns or short phrases, depending on context. Avoid exceeding 20 characters when possible.
The text labels within suggestion chips are most often nouns or short phrases
Suggestion chips can offer quick-reply options in a chat or email app
A suggestion chip can help the user start a search
When displaying multiple chips together, place them inline as a row of options, not listed vertically. Overflowing chips should break to the next line.
If the field is only one row high, chip sets can scroll horizontally instead.
Keep an 8dp minimum space between chips. Chips must also have a minimum 48dp target size, regardless of placement or density. If required, the target can extend beyond the visible container of the chip.
Text labels for chips should be concise. Chip labels will truncate when in a wrapped layout, and when they are wider than the full width of the window.
- Margins between chips
- Margin between each line
Material Design is an adaptable system of guidelines, components, and tools that support the best practices of user interface design. Backed by open-source code, Material Design streamlines collaboration between designers and developers, and helps teams quickly build beautiful products.
- Social
### Social
- GitHub
- YouTube
- Blog RSS
- Libraries
### Libraries
- Android
- Compose
- Flutter
- Web
- More Google sites
### More Google sites
- Google Design
- Archived versions
### Archived versions
- Material Design 1
- Material Design 2
- Privacy Policy
- Terms of Service
- Join research studies
- Feedback
