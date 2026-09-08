# Nielsen Norman Group — bottom sheets and overlay dismissal

Fetched 2026-09-07. Extracts, not a rewrite: the wording is the source's. Read this file only when a rule in SKILL.md cites it and you need the surrounding argument.

© Nielsen Norman Group. Extracts for reference; usability research, independent of any design system. Google Maps appears as both the positive example (non-modal sheet, map stays operable) and the failure case (stacked sheets, one swipe closes the stack).

Sources:
- Bottom Sheets: Definition and UX Guidelines: https://www.nngroup.com/articles/bottom-sheet/
- Accidental Dismissal of Overlays: A Common Mobile Usability Problem: https://www.nngroup.com/articles/accidental-overlay-dismissal/

## Bottom Sheets: Definition and UX Guidelines

# Bottom Sheets: Definition and UX Guidelines
June 11, 2023 2023-06-11
Share
- Email article
- Share on LinkedIn
- Share on Twitter
Making contextual controls noticeable and easily accessible on mobile devices is a challenge. Small screens necessitate that we hide some information or controls until they are relevant. Bottom sheets are a type of partial overlay that is especially suited for mobile devices and that makes temporarily important information readily available but also dismissible.
## In This Article:
- Defining Bottom Sheets
- Modal and Nonmodal Bottom Sheets
- Usability Guidelines for Bottom Sheets
- Summary
## Defining Bottom Sheets
B ottom sheet: An overlay that is anchored to the bottom edge of a mobile device’s screen and that displays additional details or actions.
Bottom sheets are a form of progressive disclosure –- they are typically invoked by a user interaction and provide extra details. Since they intentionally obscure some of the screen, they aren’t suited for displaying always needed information or tools.
Rather, they are used to present extra information , contextual controls , or both. The advantage of a bottom sheet is that, unlike a separate page (which requires spatial reorientation for users and may also force them to hold information in their working memory ), it preserves some of the user’s current context.
Bottom sheets share a lot of similarities with dialogs and overlays (not surprisingly, since they are a type of overlay). What’s special, however, of bottom sheets compared with other overlays is that they preserve substantial visibility of the underlying information. Thus, bottom sheets are especially useful when users are likely to need to refer to the main, background information while interacting with the information or options presented in the sheet.
A common (but largely incorrect) rationale for using bottom sheets is that they improve reachability for users on mobile devices (i.e., it is often suggested that it is easier to tap items at the bottom of the screen). This is unfortunately not universally true — as users hold mobile devices in a variety of ways (one-handed, two-handed, and from a variety of different grip points), the bottom of the screen is often not the most easily reachable screen region (the middle of the screen represents the most easily tappable area for the wide variety of ways users hold mobile devices).
## Modal and Nonmodal Bottom Sheets
Bottom sheets can be modal or nonmodal .
The modal variety works similarly to classic modal popups –- they force users to interact with them (or dismiss them) before they can take any other actions. A modal bottom sheet blocks any interactions with the background content while it is visible. A translucent dark scrim is usually placed over the locked-out background content as a signal that it is currently unavailable.
Nonmodal bottom sheets don’t require an interaction –– they sit at the bottom of the screen, and allow the user to interact with the background content. They are appropriate for presenting detailed information or options in parallel with the main information on the screen.
Some bottom sheets are expandable. Users can tap or swipe the bottom sheet up to expand it into a full-screen (or sometimes near full-screen) modal. Typically, bottom sheets start off as nonmodal in their minimized state but become modal when expanded.
## Usability Guidelines for Bottom Sheets
In our studies, we observe users having similar struggles with bottom sheets as they do with other overlays ; these are usually caused by:
- Lack of a clear way to dismiss the bottom sheet
- Stacking several bottom sheets on top of each other
- Obscuring relevant background content
Our guidelines below are meant to address these issues.
### Allow the Use of Back for Dismissing the Bottom Sheet
One problem with bottom sheets, especially when they are expanded to full screen, is that they look like regular pages. As a result, some users may not realize they are in a bottom sheet and might expect to use normal navigation elements (such as the phone’s Back button or the Back gesture) to move away from that screen. Unfortunately, this mechanism is not supported by all bottom sheets.
Thus, if, along the user’s journey, a page spawns a bottom sheet or an overlay, this page will break the normal interaction pattern. Moving away from it may or may not be accessible through the Back button, and therefore the sheet may cause disorientation. You can prevent this issue by supporting the use of Back for dismissing the bottom sheet, thus allowing the users to seamlessly return to the previous view.
### Include a Close Button
Even though most bottom sheets can be dismissed by swiping down (or tapping) on the top grab handle, that element is easy to ignore. Moreover, some users are not aware of this functionality. Plus, the vertical swipe is also prone to swipe ambiguity: depending on where precisely it is initiated, the gesture may close the bottom sheet, may open up the notification drawer, or may display the phone’s control panel.
To make sure that users will be able to reliably dismiss the bottom sheet, include a visible a Close ( or X ) button on the screen. We recommend providing a clear Close button (usually styled as an X or the word Close ) at the top of bottom sheets rather than relying exclusively on the grab handle. An additional advantage of this button is that it facilitates screen-reader and keyboard access for users that cannot see or swipe on the screen.
### Do Not Stack Bottom Sheets
One of the biggest issues with bottom sheets occurs when an app stacks several such sheets on top of each other.
We have previously discussed some of the issues with stacked bottom sheets. Inevitably, users will have to keep track of where they currently are in the rapidly multiplying stack of overlays and will need to be able to discriminate between dismissing the last sheet on the stack and dismissing the whole stack, as in the example below.
We strongly recommend not using a bottom sheet to replace typical page-to-page user flows. A bottom sheet is a transient UI element that is not intended to be a stable place for users to return to, or spend significant time on. They are intended for interruptions or a fork in the road, rather than the expected “happy path” the user will usually take. For example, don’t use a sheet to display an ecommerce product-detail page: the user may navigate to related products, reviews, or detailed specifications from that sheet, and a bottom sheet will break longstanding conventions of how users can navigate from page to page.
### Use Bottom Sheets Only for Short Interactions
Finally, we don’t recommend using a bottom sheet when users will likely spend significant time reviewing the information (or options) displayed inside it. A sheet is inherently a transient UI element — it is meant to support quick interactions, and it should not be used for displaying complex content.
## Summary
Bottom sheets are a mobile-app UI pattern intended to present temporary contextual information while maintaining access to the main content. When used for a few options or some additional information, a bottom sheet can enable quick access to controls; however, they should not be used on top of other bottom sheets or for displaying lengthy content.
## Related Topics
- Design Patterns Design Patterns
- Mobile & Tablet
## Learn More:
- Cookie Permissions: 5 Common User Types Samhita Tankala · 3 min
Cookie Permissions: 5 Common User Types
Samhita Tankala · 3 min
- Cookie Permissions: 6 Design Guidelines Samhita Tankala · 5 min
Cookie Permissions: 6 Design Guidelines
Samhita Tankala · 5 min
- Accordions: 5 Scenarios to Avoid Them Huei-Hsin Wang · 3 min
Accordions: 5 Scenarios to Avoid Them
Huei-Hsin Wang · 3 min
## Related Articles:
- How Screen-Reader Users Type on and Control Mobile Devices Tanner Kohler · 13 min
How Screen-Reader Users Type on and Control Mobile Devices
Tanner Kohler · 13 min
- Conducting Mobile Accessibility Research with Screen-Reader Users Tanner Kohler · 14 min
Conducting Mobile Accessibility Research with Screen-Reader Users
Tanner Kohler · 14 min
- Challenges for Screen-Reader Users on Mobile Tanner Kohler · 12 min
Challenges for Screen-Reader Users on Mobile
Tanner Kohler · 12 min
- Hostile Patterns in Error Messages Kate Kaplan · 7 min
Hostile Patterns in Error Messages
Kate Kaplan · 7 min
- Infinite Scrolling: When to Use It, When to Avoid It Tim Neusesser · 9 min
Infinite Scrolling: When to Use It, When to Avoid It
Tim Neusesser · 9 min
- The Usability of Augmented Reality Sana Behnam and  Raluca Budiu · 14 min
The Usability of Augmented Reality
Sana Behnam and  Raluca Budiu · 14 min

## Accidental Dismissal of Overlays

# Accidental Dismissal of Overlays: A Common Mobile Usability Problem
September 18, 2022 2022-09-18
Share
- Email article
- Share on LinkedIn
- Share on Twitter
Overlays have become a ubiquitous UI element on mobile: beyond the annoying popups for cookie permissions, chat bubbles , coupons offerings, and marketing-subscription offers, you will also find them used for navigation menus , bottom sheets, product-detail pages, or in-app browsers.
While many mobile overlays take up only a section of the page (partial overlays), allowing some content to be visible in the background, others occupy the full screen and are practically indistinguishable from a regular page or view.
Depending on whether the user can interact with the background (that is, with the content beneath the overlay), overlays can be modal or nonmodal . In modal overlays , users cannot interact with the background, while in nonmodal overlays , they can do so.
One of the major problems with mobile overlays is that dismissing them can be done through one of the following overlay-dismissal methods:
- a dedicated button included in the overlay (usually a Close or a Back button)
- tapping outside the overlay area, in the case of modal overlays that do not take up the whole page
- swiping down on the overlay handle, in the case of bottom sheets
- the browser’s Back button (on the web)
- the horizontal swipe gesture used for Back on both iOS and Android (or the phone’s Back button for Android phones)
Because designers vary in which of these overlay-dismissal methods they’ll allow, users sometimes will pick the wrong method, with unexpected and costly consequences. Things are even more complicated when several overlays are stacked on top of each other — in those cases, an overlay-dismissal method may dismiss only the top overlay or the entire stack, with no easy way for users to predict which behavior they’ll get.
Let’s start with an example. In a recent usability study, we had 8 participants interact with a variety of mobile sites and applications that used overlays.  One of our study participants used Walmart’s mobile app to shop for a light fixture. When the participant selected a product from the product-listing page, the product description was shown in an overlay.
In that overlay, he further tapped on Customer reviews , which displayed another overlay on top of the first one. To go back to the product description, the participant tapped the Close icon at the top. Unfortunately, that action dismissed the stack of overlays, and the participant was taken back to the list of products, losing his selection. Through no fault of his own, the participant had picked the wrong overlay-dismissal method. In order to navigate back, he was supposed to use either the on-screen Back button or the horizontal swipe gesture.
## In This Article:
- Overlay-Dismissal Problems
- How to Prevent Overlay-Dismissal Problems
- Conclusion
- Acknowledgments
## Overlay-Dismissal Problems
This example illustrates several of the major problems commonly associated with overlays, which are:
- Users pick the wrong overlay-dismissal method.
- Users’ work is lost.
- Stacked overlays amplify confusion.
### Users Pick the Wrong Overlay-Dismissal Method
The participant in the Walmart example could have used any of the overlay-dismissal methods to get out of the Customer reviews overlay and back to the product-detail overlay: swiping down, swiping horizontally on the left edge of the screen, tapping out, or pressing one of two on-screen buttons: close (x) icon or the Back arrow. He had no way to predict which one would get him his desired result. He guessed the close (x) button, but (unbeknownst to him) the designers had chosen the Back arrow or the horizontal Back swipe for that functionality.
Another common scenario where users may use the wrong method is when overlays look like full pages. In that case, users may use the browser or phone’s Back button, or the horizontal swipe gesture to go back to the previous view. But, because the overlay is not technically a separate page and because the Back button (at least in its standard implementation) takes people back to the previous page (and not to the previous view ), the result is that users are thrown back farther than they expected. This outcome contributes to a sense disorientation and a lack of control.
In both the Walmart and the LinkedIn/GSK example, the “correct” button from the designers’ perspective (the on-screen Back button) was visible on the screen, but it had competition from two other buttons commonly used for navigating away from a view (the X icon, in the case of the Walmart user, and the phone’s Back button for the LinkedIn user).
It’s even more confusing when there are multiple buttons on a page that are labeled in the same way, yet do different things. For example, one Instagram user opened Lowes’s website in an in-app browser shown in an overlay. He visited a product page, which used a different overlay to display available customizations for that product. Both the browser overlay and the product-customization overlay had an x icon that was intended to close the respective overlay. But the user, wanting to go back to the product page, accidentally picked the wrong one and was taken back to the Instagram view instead.
If you provide the user with multiple ways of navigating away from the current view (the swipe gesture, the phone’s Back button, an on-screen Back button, one or more Close buttons) and some of these methods have different effects, there is no guarantee that users will use the right method. When they accidentally choose the wrong method, they’ll be confused and annoyed.
### The User’s Work Is Lost
### Stacked Overlays Amplify Confusion
A big part of the problems encountered by our Walmart and Instagram users was that there were several layers of overlays on top of each other. The users did not keep track of the many layers and accidentally dismissed the whole stack instead of just the last layer. This is a very frequent occurrence. It tends to happen often when in-app browsers function as overlays but can occur in other situations as well.
For example, another one of our participants used Google Maps to look for local restaurants. The list of restaurants was displayed in a bottom-sheet overlay on top of a map. That bottom sheet could be expanded to take up the whole page. However, when the participant selected one restaurant, its detail page was shown in yet another overlay on top of the first one. To go back to the list of restaurants, the participant used the swipe-down gesture (normally used to close a bottom sheet). But that resulted in closing all the sheets in the stack and taking the user back to the map view of the restaurants, which he did not recognize.
## How to Prevent Overlay-Dismissal Problems
### Use an Alternative Pattern
The easiest way to avoid overlay issues is to simply avoid using overlays where possible. Some content is best presented in an overlay, especially when you need to present information in-context. Google Maps’ listing page is a good example of a necessary overlay — the map needed to stay in-view as the user browsed restaurants. But in other cases, overlays are very much unnecessary — for example, Walmart’s product details could easily be in separate pages (as in the Revolve app below) and customer reviews could be either shown on a separate page (also like in the Revolve app) or collapsed in an expandable accordion (as in the Nordstrom app).
### Prefer Partial to Full-Page Overlays
This is an especially good idea when the overlay contains only relatively little content that does not require scrolling. In general, if users realize that they are dealing with an overlay rather than a regular page, they will be less likely to try to use the browser’s Back button to go back.
However, if your partial overlay requires users to scroll, you may be forcing users to do more work than necessary by not taking advantage of the full screen space. You also make it more likely that they will lose their spot on the page if they accidentally close the overlay.
### Do Not Use Stacks of Overlays
Even if you end up using the occasional overlay, stay away from overlays on top of overlays, since they increase the chance that the user will accidentally close the whole stack and lose their work.
### Include a Close Button for Dismissing the Overlay
Overlays that had a clear X button were less likely to be closed accidentally (provided that no other Close buttons were also shown on the screen). Consider including one of these buttons instead of assuming that users will use gestures like swipe down to close the overlay.
With bottom sheets, do not assume that users will know to swipe down in order to close the bottom sheet. Even though that gesture needs to be supported, you should also allow users to dismiss the overlay using a visible X button.
The Built-In Back Button Should Close the Overlay
Instead of taking the risk that user will accidentally use their browser or phone’s Back button or the horizontal swipe gesture to close an overlay, support the use of the built-in Back for dismissing the overlay.
Thus, you should allow users to use the browser or the phone’s Back button or gesture to act as undo and move back from the current view to the previous one.
## Conclusion
Overlays are a popular design element on mobile, used for displaying both UI components (e.g., navigation menus) and content. Unfortunately, they can lead to some serious usability issues: they can be dismissed accidentally, thus causing users to lose work and have to retrace their steps in the interface. Stacks of overlays are particularly likely to be closed by mistake.
We recommend that designers stay away from overlays whenever possible and instead attempt to use a different design component (like an accordion or a full page). If overlays must be used, create clear signifiers that allow users to differentiate them from regular pages, display only limited content inside the overlay. For all overlays (including bottom sheets), support the following two methods for dismissing the overlay: a clear Close button and the built-in (phone’s or browser’s) Back button or Back gesture.
## Acknowledgments
We thank Mayya Azarova, Megan Brown, and Lillian Yang for helping run the test sessions. We also thank Megan Brown for helping tag the qualitative data from the sessions.
## Related Topics
- Mobile & Tablet Mobile & Tablet
- Design Patterns
## Learn More:
- Images on Mobile Raluca Budiu · 4 min
Images on Mobile
Raluca Budiu · 4 min
- Passwordless Accounts Raluca Budiu · 5 min
Passwordless Accounts
Raluca Budiu · 5 min
- Accordions on Mobile Raluca Budiu · 4 min
Accordions on Mobile
## Related Articles:
- Multitasking on Microsoft’s Surface Duo Raluca Budiu · 11 min
Multitasking on Microsoft’s Surface Duo
Raluca Budiu · 11 min
- Design-Pattern Guidelines: Study Guide Samhita Tankala and  Alita Kendrick · 6 min
Design-Pattern Guidelines: Study Guide
Samhita Tankala and  Alita Kendrick · 6 min
- Size Guides and Product Measurements for International Shoppers Feifei Liu · 9 min
Size Guides and Product Measurements for International Shoppers
Feifei Liu · 9 min
- Small Pictures on Big Screens: Scaling Up from Mobile to Desktop Amy Schade · 6 min
Small Pictures on Big Screens: Scaling Up from Mobile to Desktop
Amy Schade · 6 min
- User-Feedback Requests: 5 Guidelines Anna Kaley · 10 min
User-Feedback Requests: 5 Guidelines
Anna Kaley · 10 min
- Designing Empty States in Complex Applications: 3 Guidelines Kate Kaplan · 7 min
Designing Empty States in Complex Applications: 3 Guidelines
Kate Kaplan · 7 min
