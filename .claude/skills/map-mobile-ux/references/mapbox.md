# Mapbox — Map design for iOS

Fetched 2026-09-07. Extracts, not a rewrite: the wording is the source's. Read this file only when a rule in SKILL.md cites it and you need the surrounding argument.

© Mapbox; documentation quoted for design reference. This guide is the only Mapbox text about UI *over* a map (translucent surfaces, tint color, imprecise taps). Cartography and rendering cost live in the two Mapbox skills installed at the monorepo root `.claude/skills/`: `mapbox-cartography` (style, hierarchy, color, typography, zoom strategy) and `mapbox-web-performance-patterns` (its `references/mobile.md` is the phone-specific rendering advice). Load them instead of copying them here.

Sources:
- Map design for iOS (legacy Maps SDK guide): https://docs.mapbox.com/ios/legacy/maps/guides/map-design-for-ios/

## Map design for iOS

This page uses v6.4.1 of the Mapbox Maps SDK.
A newer version of the SDK is available. Learn about the latest version,
v11.30.0, in the Maps SDK
documentation .
Mapbox Studio allows you to create completely custom map styles. When designing your style, consider the context in which your application shows the style.
There are many considerations related to the mobile experience and iOS specifically that may not be obvious when designing your style in Mapbox Studio on the Web. A map is essentially a graphical user interface element, so many of same issues in user interface design also apply when designing a map style.
## Color ​
Make sure there is enough contrast in your application’s user interface when your map style is present. Standard user interface elements such as toolbars, sidebars, and sheets often overlap the map view with a translucent, blurred background, so make sure the contents of these elements stay legible with the map view underneath.
The user location annotation view, the attribution button, any buttons in callout views, and any items in the navigation bar are influenced by your application’s tint color, so choose a tint color that contrasts well with your map style. If you intend your style to be used in the dark, consider the impact that Night Shift may have on your style’s colors.
## Typography and graphics ​
Choose font and icon sizes appropriate to iOS devices. iPhones and iPads have smaller screens than the typical browser window in which you would use Mapbox Studio, especially when multitasking is enabled. Your user’s viewing distance may be shorter than on a desktop computer.
Some of your users may use the Larger Dynamic Type and Accessibility Text features to increase the size of all text on the device. You can use the runtime styling API to adjust your style’s font and icon sizes as needed.
Design sprite images and choose font weights that look crisp on both standard-resolution displays and Retina displays. This SDK supports the same resolutions as iOS. Standard-resolution displays are limited to older devices that your application may or may not support, depending on its minimum deployment target.
Icon and text labels should be legible regardless of the map’s orientation. By default, this SDK keeps the map legible as your users rotate or tilt the map using multitouch gestures.
If you do not intend your design to accommodate rotation and tilting, disable these gestures using the MGLMapView.rotateEnabled and MGLMapView.pitchEnabled properties, respectively, or the corresponding inspectables in Interface Builder.
## Interactivity ​
Pay attention to whether elements of your style appear to be interactive.
A text label may look like a tappable button merely due to matching your application’s tint color or the default blue tint color. You can make an icon or text label interactive by installing a gesture recognizer and performing feature querying (e.g., -[MGLMapView visibleFeaturesAtPoint:] ) to get details about the selected feature.
Make sure your users can easily distinguish any interactive elements from the surrounding map, such as pins, the user location annotation view, or a route line. Avoid relying on hover effects to highlight or emphasize interactive elements. Leave enough room between interactive elements to accommodate imprecise tapping gestures.
## Next steps ​
For more information about user interface design, consult Apple’s iOS Human Interface Guidelines . To learn more about designing maps for mobile devices, see the Maps for mobile section of Mapbox's Guide to map design .
