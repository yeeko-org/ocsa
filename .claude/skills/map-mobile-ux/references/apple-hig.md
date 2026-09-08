# Apple Human Interface Guidelines — Maps and Sheets

Fetched 2026-09-07. Extracts, not a rewrite: the wording is the source's. Read this file only when a rule in SKILL.md cites it and you need the surrounding argument.

© Apple Inc. Quoted under fair use for design reference; not redistributable as a document. Apple's vocabulary: *detents* (preset heights) and *grabber* (drag handle).

Sources:
- Maps: https://developer.apple.com/design/human-interface-guidelines/maps
- Sheets: https://developer.apple.com/design/human-interface-guidelines/sheets
- Maps, JSON endpoint the text was extracted from (the HTML page renders client-side): https://developer.apple.com/tutorials/data/design/human-interface-guidelines/maps.json

## Maps

A map uses a familiar interface that supports much of the same functionality as the system-provided Maps app, such as zooming, panning, and rotation. A map can also include annotations and overlays and show routing information, and you can configure it to use a standard graphical view, a satellite image-based view, or a view that’s a hybrid of both.
## Best practices
In general, make your map interactive. People expect to be able to zoom, pan, and otherwise interact with maps in familiar ways. Noninteractive elements that obscure the map can interfere with people’s expectations for how maps behave.
Pick a map emphasis style that suits the needs of your app. There are two emphasis styles to choose from:
-
The default style presents a version of the map with fully saturated colors, and is a good option for most standard map applications without a lot of custom elements. This style is also useful for keeping visual alignment between your map and the Maps app, in situations when people might switch between them.
The muted style, by contrast, presents a desaturated version of the map. This style is great if you have a lot of information-rich content that you want to stand out against the map.
Default style
Muted style
For developer guidance, see .
Help people find places in your map. Consider offering a search feature combined with a way to filter locations by category. The search field for a shopping mall map, for example, might include filters that make it easy to find common store types, like clothing, housewares, electronics, jewelry, and toys.
Clearly identify elements that people select. When someone selects a specific area or other element on the map, use distinct styling like an outline and color variation to call attention to the selection.
Cluster overlapping points of interest to improve map legibility. A cluster uses a single pin to represent multiple points of interest within close proximity. As people zoom in on a map, clusters expand to progressively reveal individual points of interest.
Points of interest in a cluster
Individual points of interest when zoomed in
Help people see the Apple logo and legal link. It’s fine when parts of your interface temporarily cover the logo and link, but don’t cover these elements all the time. Follow these guidelines to help keep the Apple logo and legal link visible:
Use adequate padding to separate the logo and link from the map boundaries and your custom controls. For example, it works well to use 7 points of padding on the sides of the elements and 10 points above and below them.
Avoid causing the logo and link to move with your interface. It’s best when the Apple logo and legal link appear to be fixed to the map.
If your custom interface can move relative to the map, use the lowest position of the custom element to determine the placement of the logo and link. For example, if your app lets people pull up a custom card from the bottom of the screen, place the Apple logo and legal link 10 points above the lowest resting position of the card.
The Apple logo and legal link aren’t shown on maps that are smaller than 200x100 pixels.
## Custom information
Use annotations that match the visual style of your app. Annotations identify custom points of interest on your map. The default annotation marker has a red tint and a white pin icon. You can change the tint to match the color scheme of your app. You can also change the icon to a string or image, like a logo. An icon string can contain any characters, including Unicode characters, but keep it to two to three characters in length for readability. For developer guidance, see .
If you want to display custom information that’s related to standard map features, consider making them independently selectable. When you support selectable map features, the system treats Apple-provided features (including points of interest, territories, and physical features) independently from other annotations that you add. You can configure custom appearances and information to represent these features when people select them. For developer guidance, see .
Use overlays to define map areas with a specific relationship to your content.
Above roads, the default level, places the overlay above roads but below buildings, trees, and other features. This is great for situations where you want people to have an idea of what’s below the overlay, while still clearly understanding that it’s a defined space.
Above labels places the overlay above both roads and labels, hiding everything beneath it. This is useful for content that you want to be fully abstracted from the features of the map, or when you want to hide areas of the map that aren’t relevant.
For developer guidance, see  and .
Make sure there’s enough contrast between custom controls and the map. Insufficient contrast makes controls hard to see and can cause them to blend in with the map. Consider using a thin stroke or light drop shadow to help a custom control stand out, or applying blend modes to the map area to increase its contrast with the controls atop it.
## Place cards
Place cards display rich place information in your app or website, such as operating hours, phone numbers, addresses, and more. This enables you to provide structured and up-to-date information for places that you specify, and add depth to search results.
## Displaying place cards in a map
You can present a place card that appears directly in your map anytime someone selects a place. This is a great way to provide place information in a map with multiple places that you specify, like a map of bookstores that an author plans to visit on their book signing tour. For developer guidance, see , , and .
You can also display place cards for other places on a map, such as points of interest, territories, and physical features, to provide valuable context to people about nearby places. For developer guidance, see , , and .
In websites, you can embed a custom map that displays a place card by default for a single place that you specify. For developer guidance, see .
The system defines several place card styles, which specify the size, appearance, and information included in a place card.
The automatic style lets the system determine the place card style based on the size of your map view.
The callout style displays a place card in a popover style next to the selected place. You can further specify the style of a callout — the full callout style displays a large, detailed place card, and the compact callout style displays a space-saving, more concise place card. If you don’t specify a callout style, the system defaults to the automatic callout style, which determines the callout style based on your map’s view size.
The caption style displays an “Open in Apple Maps” link.
The sheet style displays a place card in a .
For developer guidance, see , , and .
Full callout style place cards appear differently depending on a person’s device. The system presents the full callout style place card in a popover style in iPadOS and macOS, and as a  in iOS.
Consider your map presentation when choosing a style. The full callout style place card offers people the richest experience, presenting them with the most information about a place directly in your map. However, be sure to choose a place card style that fits in the context of your map. For example, if your app displays a small map with many annotations, consider using the compact callout style for a space-saving presentation that shows place information while maintaining the context of the other places that you specify in your map.
Make sure your place card looks great on different devices and window sizes. If you choose to specify a style, ensure that the content in your place card remains viewable on different devices and as window sizes change. For full callout style place cards, you can set a minimum width to prevent text from overflowing on smaller devices.
Avoid duplicating information. Consider what information you already display in your app or website when you choose a place card style. For example, the full callout style place card might display information that your app already shows. In this case, the compact callout or caption style might be a better complement.
Keep the location on your map visible when displaying a place card. This helps people maintain a sense of where the location is on your map while getting detailed place information. You can set an offset distance for your place card and point it to the selected location. For developer guidance, see , , and .
## Adding place cards outside of a map
You can also display place information outside of a map in your app or website. For example, you might want to display a list of places rather than a map, like in search results or a store locator, and present a place card when people select one. For developer guidance, see , , and .
If you don’t display a place card directly within a map view, you must include a map in the place card. For developer guidance, see  and .
Use location-related cues in surrounding content to help communicate that people can open a place card. For example, you can display place names and addresses alongside a button for more details to help indicate that people can interact with it to get place information. For a space-efficient design, you can include a map pin icon with a place name to help communicate that people can open a place card.
## Indoor maps
Apps connected with specific venues like shopping malls and stadiums can design custom interactive maps that help people locate and navigate to indoor points of interest. Indoor maps can include overlays that highlight specific areas, such as rooms, kiosks, and other locations. They can also include text labels, icons, and routes.
Adjust map detail based on the zoom level. Too much detail can cause a map to appear cluttered. Show large areas like rooms and buildings at all zoom levels. Then, progressively add more detailed features and labels as the map is zoomed in. An airport map might show only terminals and gates when zoomed out, but reveal individual stores and restrooms when zoomed in.
Use distinctive styling to differentiate the features of your map. Using color along with icons can help distinguish different types of areas, stores, and services, and make it easy for people to quickly find what they’re looking for.
Offer a floor picker if your venue includes multiple levels. A floor picker lets people quickly jump between floors. If you implement this feature, keep floor numbers concise for simplicity. In most cases, a list of floor numbers — rather than floor names — is sufficient.
Include surrounding areas to provide context. Adjacent streets, playgrounds, and other nearby locations can all help orient people when they use your map. If these areas are noninteractive, use dimming and a distinct color to make them appear supplemental.
Consider supporting navigation between your venue and nearby transit points. Make it easy to enter and exit your venue by offering routing to and from nearby bus stops, train stations, parking lots, garages, and other transit locations. You might also offer a way for people to quickly switch over to Apple Maps for additional navigation options.
Limit scrolling outside of your venue. This can help people avoid getting lost when they swipe too hard on your map. When possible, keep at least part of your indoor map visible onscreen at all times. To help people stay oriented, you may need to adjust the amount of scrolling you permit based on the zoom level.
Design an indoor map that feels like a natural extension of your app. Don’t try to replicate the appearance of Apple Maps. Instead, make sure area overlays, icons, and text match the visual style of your app. For guidance, see .
## Platform considerations
No additional considerations for iOS, iPadOS, macOS, tvOS, or visionOS.
## watchOS
On Apple Watch, maps are static snapshots of geographic locations. Place a map in your interface at design time and show the appropriate region at runtime. The displayed region isn’t interactive; tapping it opens the Maps app on Apple Watch. You can add up to five annotations to a map to highlight points of interest or other relevant information. For developer guidance, see .
Fit the map interface element to the screen. The entire element needs to be visible on the Apple Watch display without requiring scrolling.
Show the smallest region that encompasses the points of interest. The content within a map interface element doesn’t scroll, so all key content must be visible within the displayed region.
## Resources
## Developer documentation
## Videos
## Change log
Date
Changes
December 18, 2024
Added guidance for place cards and included additional artwork.
September 12, 2023
Added artwork.
September 23, 2022
Added guidelines for presenting custom information, refined best practices, and consolidated guidance into one page.
A map displays outdoor or indoor geographical data in your app or on your website.

## Sheets

A sheet is useful for requesting specific information from people or presenting a simple task that they can complete before returning to the parent view. For example, a sheet might let people supply information needed to complete an action, such as attaching a file or choosing a location to save it.
## Anatomy
In macOS, tvOS, visionOS, and watchOS, a sheet is always modal. A modal sheet presents a targeted experience that prevents people from interacting with the parent view until they dismiss the sheet (for more on modal presentation, see ).
In iOS and iPadOS, a sheet can be either modal or nonmodal. When a nonmodal sheet is onscreen, people use its functionality to affect the parent view without dismissing the sheet. For example, Notes on iPhone and iPad uses a nonmodal sheet to let people format various text selections as they edit a note.
The Notes format sheet lets people apply formatting to selected text in the editing view.
Because the sheet is nonmodal, people can make additional text selections without dismissing the sheet.
There are several common buttons that help people navigate through and dismiss sheets.
-
The Cancel (or Close) button dismisses a sheet without saving any changes. This type of button is common in most sheets.
The Done button dismisses a sheet after completing a task or explicitly saving changes.
The Back button lets people navigate to a previous step in a multi-step flow or to a parent view in a hierarchy. It isn’t intended to dismiss a sheet.
The placement of these buttons varies between platforms; see .
## Best practices
Display only one sheet at a time from the main interface. When people close a sheet, they expect to return to the parent view or window. If closing a sheet takes people back to another sheet, they can lose track of where they are in your app. If something people do within a sheet results in another sheet appearing, close the first sheet before displaying the new one. If necessary, you can display the first sheet again after people dismiss the second one.
Use a nonmodal view when you want to present supplementary items that affect the main task in the parent view. To give people access to information and actions they need while continuing to interact with the main window, consider using a  in visionOS or a  in macOS; in iOS and iPadOS, you can use a nonmodal sheet for this workflow. For guidance, see .
Provide an alternative to the Done button. If you provide a Done button, always pair it with a Cancel button to give people a clear way to dismiss the sheet without confirming or saving their changes, or a Back button to move to a previous step in the sheet. Relying solely on the Done button implies that completing the task is the only way to exit the sheet, which can feel restrictive or misleading.
Avoid showing all three buttons — Cancel, Done, and Back — together.
## Platform considerations
No additional considerations for tvOS.
## iOS, iPadOS
In iOS and iPadOS, for sheets with a single view, the Cancel button belongs on the leading edge of the top toolbar. When present, the Done button belongs on the trailing edge.
For sheets with a multi-step flow, the placement of buttons can vary across steps.
On the first step, where there isn’t a Back button, the Cancel button belongs on the leading edge. When present, the Done button belongs on the trailing edge, in an inactive state to indicate that the task isn’t complete yet.
On subsequent steps, the Back button replaces the Cancel button to let people navigate back.
On the final confirmation step, the Done button becomes active to let people acknowledge completion of the task and dismiss the sheet.
A resizable sheet expands when people scroll its contents or drag the grabber, which is a small horizontal indicator that can appear at the top edge of a sheet. Sheets resize according to their detents, which are particular heights at which a sheet naturally rests. Designed for iPhone, detents specify particular heights at which a sheet naturally rests. The system defines two detents: large is the height of a fully expanded sheet and medium is about half of the fully expanded height. Sheets can have one or more custom detent values.
Large detent
Medium detent
Sheets automatically support the large detent. Adding the medium detent allows the sheet to rest at both heights, whereas specifying only medium prevents the sheet from expanding to full height. For developer guidance, see .
In an iPhone app, consider supporting the medium detent to allow progressive disclosure of the sheet’s content. For example, a share sheet displays the most relevant items within the medium detent, where they’re visible without resizing. To view more items, people can scroll or expand the sheet. In contrast, you might not want to support the medium detent if a sheet’s content is more useful when it displays at full height. For example, the compose sheets in Messages and Mail display only at full height to give people enough room to create content.
Include a grabber in a resizable sheet. A grabber shows people that they can drag the sheet to resize it; they can also tap it to cycle through the detents. In addition to providing a visual indicator of resizability, a grabber also works with VoiceOver so people can resize the sheet without seeing the screen. For developer guidance, see .
Support swiping to dismiss a sheet. People expect to swipe vertically to dismiss a sheet instead of tapping a dismiss button. If people have unsaved changes in the sheet when they begin swiping to dismiss it, use an action sheet to let them confirm their action.
Prefer using the page or form sheet presentation styles in an iPadOS app. Each style uses a default size for the sheet, centering its content on top of a dimmed background view and providing a consistent experience. For developer guidance, see .
## macOS
In macOS, a sheet is a cardlike view with rounded corners that floats on top of its parent window. The parent window is dimmed while the sheet is onscreen, signaling that people can’t interact with it until they dismiss the sheet. However, people expect to interact with other app windows before dismissing a sheet.
Present a sheet in a reasonable default size. People don’t generally expect to resize sheets, so it’s important to use a size that’s appropriate for the content you display. In some cases, however, people appreciate a resizable sheet — such as when they need to expand the contents for a clearer view — so it’s a good idea to support resizing.
Let people interact with other app windows without first dismissing a sheet. When a sheet opens, you bring its parent window to the front — if the parent window is a document window, you also bring forward its modeless document-related panels. When people want to interact with other windows in your app, make sure they can bring those windows forward even if they haven’t dismissed the sheet yet.
Use a panel instead of a sheet if people need to repeatedly provide input and observe results. A find and replace panel, for example, might let people initiate replacements individually, so they can observe the result of each search for correctness. For guidance, see .
## visionOS
While a sheet is visible in a visionOS app, it floats in front of its parent window, dimming it, and becoming the target of people’s interactions with the app.
Avoid displaying a sheet that emerges from the bottom edge of a window. To help people view the sheet, prefer centering it in their .
Present a sheet in a default size that helps people retain their context. Avoid displaying a sheet that covers most or all of its window, but consider letting people resize the sheet if they want.
## watchOS
In watchOS, a sheet is a full-screen view that slides over your app’s current content. The sheet is semitransparent to help maintain the current context, but the system applies a material to the background that blurs and desaturates the covered content.
Use a sheet only when your modal task requires a custom title or custom content presentation. If you need to give people important information or present a set of choices, consider using an  or .
Keep sheet interactions brief and occasional. Use a sheet only as a temporary interruption to the current workflow, and only to facilitate an important task. Avoid using a sheet to help people navigate your app’s content.
If you change the default label, prefer using SF Symbols to represent the action. Avoid using a label that might mislead people into thinking that the sheet is part of a hierarchical navigation interface. Also, if the text in the top-leading corner looks like a page or app title, people won’t know how to dismiss the sheet. For guidance, see .
## Resources
## Related
## Developer documentation
 — SwiftUI
 — UIKit
 — AppKit
## Change log
Date
Changes
March 24, 2026
Updated guidance for button placement.
March 29, 2024
Added guidance to use form or page sheet styles in iPadOS apps.
December 5, 2023
Recommended using a split view to offer supplementary items in a visionOS app.
June 21, 2023
Updated to include guidance for visionOS.
June 5, 2023
Updated guidance for using sheets in watchOS.
A sheet helps people perform a scoped task that’s closely related to their current context.
