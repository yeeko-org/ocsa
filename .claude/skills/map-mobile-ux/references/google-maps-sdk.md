# Google Maps Platform — design rationale hidden in SDK documentation

Fetched 2026-09-07. Extracts, not a rewrite: the wording is the source's. Read this file only when a rule in SKILL.md cites it and you need the surrounding argument.

Google developer documentation content is licensed under CC BY 4.0; code samples under Apache 2.0. Google publishes no UX guide for maps: the rationale lives in these API pages (padding, control placement, gesture handling, clustering). Mapbox GL JS equivalents: `map.setPadding` / the `padding` option of `fitBounds`, `easeTo`, `flyTo`; `cooperativeGestures`; `cluster*` source options.

Sources:
- Maps SDK for Android, configure the map (map padding): https://developers.google.com/maps/documentation/android-sdk/configure-map
- Maps SDK for Android, UI controls and gestures: https://developers.google.com/maps/documentation/android-sdk/controls
- Maps JavaScript API, controls: https://developers.google.com/maps/documentation/javascript/controls
- Maps JavaScript API, interaction and gestureHandling: https://developers.google.com/maps/documentation/javascript/interaction
- Maps JavaScript API, marker clustering: https://developers.google.com/maps/documentation/javascript/marker-clustering
- Maps SDK for Android utility, marker clustering: https://developers.google.com/maps/documentation/android-sdk/utility/marker-clustering

## Maps SDK for Android — configure the map

### Set up map padding
This video shows an example of map padding.
A Google map is designed to fill the entire region defined by its container
element, typically a MapView or SupportMapFragment . Several aspects of how
the map appears and behaves are defined by the dimensions of its container:
- The camera's target will reflect the center of the padded region.
- Map controls are positioned relative to the edges of the
map.
- Legal information, such as copyright statements or the Google logo appear
along the bottom edge of the map.
You can add padding around the edges of the map using the GoogleMap . setPadding() method. The map will
continue to fill the entire container, but text and control positioning, map
gestures, and camera movements will behave as if it has been placed in a
smaller space. This results in the following changes:
- Camera movements using API calls or button presses (e.g., compass, my
location, zoom buttons) are relative to the padded region.
- The getCameraPosition method returns the center of the padded region.
- The Projection and getVisibleRegion methods return the padded region.
- UI controls are offset from the edge of the container by the specified
number of pixels.
Padding can be helpful when designing UIs that overlap some portion of the
map. In the following image, the map is padded along the top and
right edges. Visible map controls and legal text will be displayed along the
edges of the padded region, shown in green, while the map will continue to
fill the entire container, shown in blue. In this example, you could float a
menu over the right side of the map without obscuring map controls.
## Maps SDK for Android — controls and gestures

### Lite mode for minimal user interaction
If you want a light-weight map with minimal user interaction, consider using a
lite-mode map. Lite mode offers a bitmap image of a map at a specified
location and zoom level. In lite mode, users cannot pan or zoom the map and
gestures do not work. For details, see the guide to lite mode .
### UI controls
The Maps API offers built-in UI controls that are similar to those
found in the Google Maps application on your Android phone. You can toggle
the visibility of these controls using the UiSettings class
which can be obtained from a GoogleMap with the GoogleMap.getUiSettings method. Changes made on this class are immediately reflected on the map. To
see an example of these features, look at the UI Settings demo activity in the sample application .
You can also configure most of these options when the map is created either
via XML attributes or using the GoogleMapOptions class. See Configuring initial state for more details.
Each UI control has a pre-determined position relative to the edge of the map.
You can move the controls away from the top, bottom, left or right edge by
adding padding to the GoogleMap object.
### Zoom controls
The Maps API provides built-in zoom controls that appear in the bottom
right hand corner of the map. These are disabled by default, but can be
enabled by calling UiSettings.setZoomControlsEnabled(true) .
### Compass
The Maps API provides a compass graphic which appears in the top left
corner of the map under certain circumstances. The compass will only ever
appear when the camera is oriented such that it has a non-zero bearing or
non-zero tilt. When the user clicks on the compass, the camera animates back
to a position with bearing and tilt of zero (the default orientation)
and the compass fades away shortly afterwards. You can disable the compass
appearing altogether by calling UiSettings.setCompassEnabled(boolean) .
However, you cannot force the compass to always be shown.
### My Location button
The My Location button appears in the top right corner of the screen only when the My Location layer is enabled. For details, see the guide to location data .
### Level picker
By default, a level picker (floor picker) appears near the center right-hand
edge of the screen when the user is viewing an indoor map . When two or
more indoor maps are visible the level picker will apply to the building that is
currently in focus, which is typically the one nearest the center of the screen.
Each building has a default level which will be selected when the picker is
first displayed. Users can choose a different level by selecting it from the
picker.
You can disable or enable the level picker control by calling GoogleMap.getUiSettings().setIndoorLevelPickerEnabled(boolean) .
This is useful if you want to replace the default level picker with your own.
### Map toolbar
By default, a toolbar appears at the bottom right of the map when a user taps a
marker. The toolbar gives the user quick access to the Google Maps mobile app.
You can enable and disable the toolbar by calling UiSettings.setMapToolbarEnabled(boolean) .
In a lite-mode map, the toolbar persists independently of the user's
actions. In a fully-interactive map, the toolbar slides in when the user taps a
marker and slides out again when the marker is no longer in focus.
The toolbar displays icons that provide access to a map view or directions
request in the Google Maps mobile app. When a user taps an icon on the toolbar,
the API builds an intent to launch the corresponding activity
in the Google Maps mobile app.
The toolbar is visible at bottom right of the map in the above screenshot.
Zero, one or both of the intent icons will appear on the map, depending on the
content of the map and provided that the Google Maps mobile app supports the
resulting intent.
### Map gestures
A map created with the Maps SDK for Android supports the same gestures as
the Google Maps application. However, there might be situations where you want
to disable certain gestures in order to preserve the state of the map. Zoom,
pan, tilt and bearing can also be set programmatically - see Camera and View for more details.  Note that disabling gestures
does not affect whether you can change the camera position programmatically.
Like the UI controls, you can enable/disable gestures with the UiSettings class which can be obtained from a GoogleMap by calling GoogleMap.getUiSettings .  Changes made on this class are
immediately reflected on the map. To see an example of these features, look
at the UI Settings demo activity in the sample application (see here for how to install it).
You can also configure these options when the map is created either via XML
Attributes or using the GoogleMapOptions class.
See Configuring the map for more details.
### Zoom gestures
The map responds to a variety of gestures that can change the zoom level of
the camera:
- Double tap to increase the zoom level by 1 (zoom in).
- Two finger tap to decrease the zoom level by 1 (zoom out).
- Two finger pinch/stretch
- One finger zooming by double tapping but not releasing on the second tap,
and then sliding the finger up to zoom out, or down to zoom in.
You can disable zoom gestures by calling UiSettings.setZoomGesturesEnabled(boolean) . This will not affect whether a
user can use the zoom controls to zoom in and out.
### Scroll (pan) gestures
A user can scroll (pan) around the map by dragging the map with their finger.
You can disable scrolling by calling UiSettings.setScrollGesturesEnabled(boolean) .
### Tilt gestures
A user can tilt the map by placing two fingers on the map and moving them down
or up together to increase or decrease the tilt angle respectively. You can
disable tilt gestures by calling UiSettings.setTiltGesturesEnabled(boolean) .
### Rotate gestures
A user can rotate the map by placing two fingers on the map and applying a
rotate motion. You can disable rotation by calling UiSettings.setRotateGesturesEnabled(boolean) .
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License , and code samples are licensed under the Apache 2.0 License . For details, see the Google Developers Site Policies . Java is a registered trademark of Oracle and/or its affiliates.

## Maps JavaScript API — controls

### Controls Overview
The maps displayed through the Maps JavaScript API contain UI
  elements to allow user interaction with the map. These elements are known as controls and you can include variations of these controls in your
  application. Alternatively, you can do nothing and let the
  Maps JavaScript API handle all control behavior.
The following map shows the default set of controls displayed by the
  Maps JavaScript API:
Clockwise from top left: Map Type, Fullscreen, Camera, Street View,
Keyboard shortcuts.
Below is a list of the full set of controls you can use in your maps:
- The Map Type control is available in a drop-down
    or horizontal button bar style, allowing the user to choose a map type
    ( ROADMAP , SATELLITE , HYBRID , or TERRAIN ). This control appears by default in the top left
    corner of the map.
- The Fullscreen control offers the option to open
    the map in fullscreen mode. This control is enabled by default on desktop and
    mobile devices. Note: iOS doesn't support the fullscreen
    feature. The fullscreen control is therefore not visible on iOS devices.
- The Camera control features both zoom
    and pan controls.
- The Street View control contains a Pegman icon
    which can be dragged onto the map to enable Street View. This control
    appears by default near the bottom right of the map.
- The Rotate control provides a combination of
    tilt and rotate options for maps containing 3D imagery. This
    control appears by default near the bottom right of the map. See 3D overview for more
    information.
- The Scale control displays a map scale element.
    This control is disabled by default.
- The Keyboard shortcuts control displays a list
    of keyboard shortcuts for interacting with the map.
You don't access or modify these map controls directly. Instead, you
  modify the map's MapOptions fields which affect the visibility and presentation of controls. You can adjust control
  presentation upon instantiating your map (with appropriate MapOptions ) or modify a
  map dynamically by calling setOptions() to change the map's options.
Not all of these controls are enabled by default. To learn about default UI
  behavior (and how to modify such behavior), see The
  Default UI below.
### The Default UI
By default, all the controls disappear if the map is too small (200x200px).
  You can override this behavior by explicitly setting the control to be
  visible. See Adding Controls to the
  Map .
The behavior and appearance of the controls is the same across mobile and
  desktop devices, except for the fullscreen control (see the behavior
  described in the list of controls ).
Additionally, keyboard handling is on by default on all devices.
### Control Options
Several controls are configurable, allowing you to alter their behavior or
  change their appearance. The Map Type control , for
  example, may appear as a horizontal bar or a drop-down menu.
These controls are modified by altering appropriate control options fields within the MapOptions object upon creation of the map.
For example, options for altering the Map Type control are indicated in the mapTypeControlOptions field. The Map Type control may appear in
  one of the following style options:
- google.maps.MapTypeControlStyle.HORIZONTAL_BAR displays the
    array of controls as buttons in a horizontal bar as is shown on Google
    Maps.
- google.maps.MapTypeControlStyle.DROPDOWN_MENU displays a
    single button control allowing you to select the map type using a drop-down
    menu.
- google.maps.MapTypeControlStyle.DEFAULT displays the
    default behavior, which depends on screen size and may change in future
    versions of the API.
Note that if you do modify any control options, you should explicitly enable
  the control as well by setting the appropriate MapOptions value
  to true . For example, to set a Map Type control
  to exhibit the DROPDOWN_MENU style, use the following code within
  the MapOptions object:
    ... mapTypeControl : true , mapTypeControlOptions : { style : google . maps . MapTypeControlStyle . DROPDOWN_MENU } ...
The following example demonstrates how to change the default position and
  style of controls.
    innerMap . setOptions ({ mapTypeControl : true , mapTypeControlOptions : { style : MapTypeControlStyle.DROPDOWN_MENU , mapTypeIds : [ MapTypeId . ROADMAP , MapTypeId . TERRAIN ], position : ControlPosition.TOP_CENTER , }, }); index . ts
    innerMap . setOptions ({ mapTypeControl : true , mapTypeControlOptions : { style : MapTypeControlStyle . DROPDOWN_MENU , mapTypeIds : [ MapTypeId . ROADMAP , MapTypeId . TERRAIN ], position : ControlPosition . TOP_CENTER , }, }); index . js
Controls are typically configured upon creation of the map. However,
  you may alter the presentation of controls dynamically by
  calling the Map 's setOptions() method,
  passing it new control options.
### Modify Controls
You specify a control's presentation when you create your map
  through fields within the map's MapOptions object. These
  fields are denoted below:
- cameraControl enables/disables the camera control that
    lets the user zoom and pan the map.
    This control is visible by default on all maps.
    The cameraControlOptions field additionally specifies the CameraControlOptions to use for this control.
- mapTypeControl enables/disables the Map Type control
    that lets the user toggle between map types (such as Map and Satellite).
    By default, this control is visible and appears in the top left
    corner of the map. The mapTypeControlOptions field
    additionally specifies the MapTypeControlOptions to use for this control.
- streetViewControl enables/disables the Pegman control
    that lets the user activate a Street View panorama.
    By default, this control is visible and appears near the bottom right
     of the map. The streetViewControlOptions field
    additionally specifies the StreetViewControlOptions to use for this control.
- rotateControl enables/disables the appearance of a
    Rotate control for controlling the orientation of 3D imagery. By
    default, the control's presence is determined by the presence or absence
    of 3D imagery for the given map type at the current zoom and
    location. You may alter the control's behavior by setting the map's rotateControlOptions to specify the RotateControlOptions to use. The control will only appear on 3D base maps.
- scaleControl enables/disables the Scale control that
    provides a map scale. By default, this control is not visible. When
    enabled, it will always appear in the bottom right corner of the map. The scaleControlOptions additionally specifies the ScaleControlOptions to use for this control.
- fullscreenControl enables/disables the control that opens
    the map in fullscreen mode. By default, this control is enabled by default
    on desktop and Android devices.
    When enabled, the control appears near the top right of the map. The fullscreenControlOptions additionally specifies the FullscreenControlOptions to use for this control.
Note that you may specify options for controls you initially disable.
### Control Positioning
Most of the control options contain a position property
  (of type ControlPosition ) which indicates where on the map to
  place the control. Positioning of these controls is not absolute. Instead,
  the API will lay out the controls intelligently by flowing them around
  existing map elements, or other controls, within given constraints (such as
  the map size).
There are two flavors of control positions: legacy and logical. Usage of logical values is recommended in order to be able to automatically support both left-to-right (LTR) and
  right-to-left (RTL) layout contexts. See the reference guide .
The following tables show the supported control positions in LTR and RTL
  contexts.
### LTR positions
### RTL positions
Click the labels to toggle the map between LTR and RTL modes.
Note that these positions may coincide with positions of UI elements
  whose placements you may not modify (such as copyrights and the Google logo).
  In those cases, the controls will flow according to the logic noted for
  each position and appear as close as possible to their indicated
  position. No guarantees can be made that controls may not overlap given
  complicated layouts, though the API will attempt to arrange them intelligently.
The following example shows a basic map with all controls enabled, in
  different positions.
### Custom Controls
As well as modifying the style and position of existing API controls, you
  can create your own controls to handle interaction with the user. Controls
  are stationary widgets which float on top of a map at absolute positions, as
  opposed to overlays , which move with the underlying map. More
  fundamentally, a control is a <div> element which
  has an absolute position on the map, displays some UI to the user, and
  handles interaction with either the user or the map, usually through an event
  handler.
To create your own custom control, few rules are necessary. However, the
  following guidelines can act as best practice:
- Define appropriate CSS for the control element(s) to display.
- Handle interaction with the user or the map through event handlers for
    either map property changes or user events (for example, 'click' events).
- Create a <div> element to hold the control and add
    this element to the Map 's controls property.
Each of these concerns is discussed below.
### Draw Custom Controls
How you draw your control is up to you. Generally, we recommend that you
  place all of your control presentation within a single <div> element so that you can manipulate your control as
  one unit. We will use this design pattern in the samples shown below.
Designing attractive controls requires some knowledge of CSS and DOM
  structure. The following code examples show adding a custom control using
  both declarative HTML and programmatic methods.
#### Declarative CSS
The following CSS styles provide an appearance that's consistent with
  the default controls. Use these styles with both of the examples below:
    . streetview-toggle-button { align-items : center ; background : white ; border : none ; border-radius : 2 px ; box-shadow : 0 1 px 4 px -1 px rgba ( 0 , 0 , 0 , 0.3 ); color : rgb ( 86 , 86 , 86 ); cursor : pointer ; display : flex ; font-family : Roboto , Arial , sans-serif ; font-size : 18 px ; font-weight : 400 ; height : 40 px ; justify-content : center ; margin : 10 px 0 ; padding : 0 17 px ; } . streetview-toggle-button : hover { background : #f4f4f4 ; color : #000 ; }
#### Declarative HTML
These code snippets show how to create a custom control declaratively.
  In the HTML, a DIV with the ID container is used to position
  the control; this is nested within the gmp-map element and
  the button is added to the DIV. The slot attribute is set to control-inline-start-block-start to position the control in the
  top left corner of the map.
    <gmp-map
  center="41.027748173921374, -92.41852445367961"
  zoom="13"
  map-id="DEMO_MAP_ID">
  <div id="container" slot="control-inline-start-block-start">
    <input type="button"
    id="streetview-toggle-button"
    class="button"
    value="Click this button" />
  </div>
</gmp-map>
In the JavaScript, getElementById() is used to find the DIV and button, an event
  listener is added to the button, and the button is appended to the DIV.
#### Programmatic JavaScript
This code snippet demonstrates programmatically creating a button control.
  The CSS styles are defined above.
### Handle Events from Custom Controls
For a control to be useful, it must actually do something. What the control
  does is up to you. The control may respond to user input, or it may respond
  to changes in the Map 's state.
For responding to user input, use addEventListener() , which handles supported DOM events . The
  following code snippet adds a listener for the browser's 'click' event. Note that this event is received from the DOM, not from the map.
### Make Custom Controls Accessible
To ensure that controls receive keyboard events and appear correctly to screen readers:
- Always use native HTML elements for buttons, form elements, and labels. Only use a DIV
    element as a container to hold native controls; never repurpose a DIV as an interactive UI
    element.
- Use the label element, title attribute, or aria-label attribute where appropriate, to provide information about a UI element.
### Position Custom Controls
Use the slot attribute to position custom controls, specifying the needed control position.
  For information on these positions, see Control Positioning above.
Each ControlPosition stores an MVCArray of the
  controls displayed in that position. As a result, when controls are added or
  removed from the position, the API will update the controls accordingly.
The following code creates a new custom control (its constructor is not
  shown) and adds it to the map in the BLOCK_START_INLINE_END position
  (top-right in LTR context).
To set position for a custom control declaratively, set the slot attribute in the
  HTML:
    <gmp-map center="30.72851568848909, -81.54675994068873" zoom="12">
  <div slot="control-block-start-inline-end">
    <!-- Control HTML -->
### A Custom Control Example
The following control is simple (though not particularly useful) and
  combines the patterns shown above. This control responds to DOM 'click' events by centering the map at a certain default
  location:
### Add State to Controls
Controls may also store state. The following example is similar to that
  shown before, but the control contains an additional "Set Home" button which
  sets the control to exhibit a new home location. We do so by creating a home_ property within the control to store this state and
  provide getters and setters for that state.
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License , and code samples are licensed under the Apache 2.0 License . For details, see the Google Developers Site Policies . Java is a registered trademark of Oracle and/or its affiliates.

## Maps JavaScript API — interaction (gestureHandling)

### Overview
The usage of a map on a web page may require specific options to control the way users interact with the map to zoom and pan. These options, such as gestureHandling , minZoom , maxZoom and restriction , are defined within the MapOptions interface .
### Default Behavior
The following map demonstrates the default behavior for map interactions with a map instantiated with only the zoom and center options defined.
The code for this map is below.
### Controlling Gesture Handling
When a user scrolls a page that contains a map, the scrolling action can
unintentionally cause the map to zoom. This behavior can be controlled using the gestureHandling map option.
### gestureHandling: cooperative
The map below uses the gestureHandling option set
to cooperative , allowing the user to scroll the page normally, without zooming
or panning the map. Users can zoom the map by clicking the zoom controls. They
can also zoom and pan by using two-finger movements on the map for touchscreen
devices.
View Sample
### gestureHandling: auto
The map at the top of the page without the gestureHandling option has the same
behavior as the preceding map with gestureHandling set to cooperative because all of the maps on this page are within an <iframe> . The default gestureHandling value auto switches between greedy and cooperative based upon whether the map is
contained within an <iframe> .
### gestureHandling: greedy
A map with gestureHandling set to greedy is
below. This map reacts to all touch gestures and scroll events unlike cooperative .
### gestureHandling: none
The gestureHandling option can also be set to none to disable gestures on the map.
### Disabling Pan and Zoom
To entirely disable the ability to pan and zoom the map, two options, gestureHandling and zoomControl , must be included.
The map below demonstrates the combination of gestureHandling and zoomControl in the code above.
### Restricting Map Bounds and Zoom
It may be desirable to allow gestures and zoom controls but restrict the map to
a particular bounds or a minimum and maximum zoom. To accomplish this you may
set the restriction , minZoom ,
and maxZoom options. The following code and map
demonstrate these options.
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License , and code samples are licensed under the Apache 2.0 License . For details, see the Google Developers Site Policies . Java is a registered trademark of Oracle and/or its affiliates.

## Maps JavaScript API — marker clustering

### Overview
This tutorial shows you how to use marker clusters to display a large number of markers on a map.
  You can use the @googlemaps/markerclusterer library in combination with the Maps JavaScript API to combine
  markers of close proximity into clusters, and simplify the display of markers
  on the map.
To see how marker clustering works, view the map below. The number on a cluster indicates how many markers it contains. Notice that as you zoom into any
of the cluster locations, the number on the cluster decreases, and you begin to see the individual
  <head>
    <title>Marker Clustering</title>
    <link rel="stylesheet" type="text/css" href="./style.css" />
    <script type="module" src="./index.js"></script>
  </head>
  <body>
    <div id="map"></div>
    <!-- prettier-ignore -->
        ({key: "AIzaSyB41DRUbKWJHPxaFjMAwdrzWzbVKartNGg", v: "weekly"});</script>
  </body>
</html> index.html As a simple illustration, this tutorial adds a set of markers to the map using the locations array. You can use other sources to get markers for your map.
The number on a cluster indicates how many markers it contains. Notice that as you zoom into any
markers on the map. Zooming out of the map consolidates the markers into clusters again.
The sample below shows the entire code you need to create this map.
    /* * Always set the map height explicitly to define the size of the div element * that contains the map. */ # map { height : 100 % ; } /* * Optional: Makes the sample page fill the window. */ html , body { height : 100 % ; margin : 0 ; padding : 0 ; } style . css
    <html>
</html> index.html
As a simple illustration, this tutorial adds a set of markers to the map using the locations array. You can use other sources to get markers for your map.
For more information, read the guide to creating markers .
## Maps SDK for Android utility — marker clustering

### Introduction
This video discusses the use of marker clustering when
  your data requires a large number of data points on the map.
The marker clustering utility helps you manage multiple markers at different
  zoom levels. To be precise, the 'markers' are actually 'items' at this point,
  and only become 'Markers' when they're rendered. But for the sake of clarity,
  this document will name them 'markers' throughout.
When a user views the map at a high zoom level, the individual
  markers show on the map. When the user zooms out, the markers gather
  together into clusters, to make viewing the map easier. The marker clustering
  utility is part of the Maps SDK for Android Utility Library . If you haven't yet set up the library,
  follow the setup guide before reading the rest of this page.
To use the marker clustering utility, you will need to add markers as objects to the . The passes the markers to the ,
  which transforms them into a set of clusters. The takes care of the rendering, by adding and removing clusters and individual
  markers. The and are
  pluggable and can be customized.
The utility library ships with a demo app providing sample implementations
  of the marker clustering utility. For help with running the demo app, see the setup guide . The demo
  app includes the following marker clustering samples:
- : A simple activity demonstrating
    marker clustering.
- : Clustering with 2 000
    markers.
- : Creating a custom design
    for clustered markers.
