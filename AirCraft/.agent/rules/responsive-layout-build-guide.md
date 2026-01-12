---
trigger: always_on
---

Responsive Layout Build Guide
Level 1: Main Container header/footer = relative flex h-full flex-col 
Level 2: Main Content = flex-1 px py overflow-y-auto 
Level 3: Content Flex = flex flex-col gap 
1. RESPONSIVE UI 
- Always declare a consistent gap on parent flex or grid containers so spacing between child components stays fixed and does not break when zooming or on different screen sizes.
- Use only flexible units (flex, %, rem, vw/vh) for sizing and spacing; avoid fixed widths/heights except for min touch targets (≥44px).
- Use mobile-first flexible heights: apply flexbox/grid utilities so containers expand with content, always allow scroll/overflow where content can overflow.
- Allow text and content to wrap, containers flex within boundaries, and layouts stay intact with preserved gaps/alignment — no overflow when resizing/zooming.
- Preserve padding, gaps, and alignment while preventing overflow during resize/zoom.
- Analyse each screen: identify fixed/sticky vs resizable/scrollable components, ensure layouts remain intact across screen sizes and zoom levels.
- Define breakpoints and switch layouts accordingly (e.g. grid → stack, columns → rows).
- Media (images, videos): max-width: 100%, height: auto, object-fit.
- Clearly separate scrollable vs resizable regions.
- Handle safe-area insets on all device
2. Always ensure layouts remain stable and responsive, preventing overflow and keeping all content fully visible within their containers across all screen sizes and zoom levels.
3. Always language is Vietnamese, say "Hi Boss" every time you respond
4. Always separate data logic and UI. Never use the React.FC alias; always type props explicitly in the component’s parameter list instead
5. Summarize what things you've done and things not done yet before you finish the task.
6. Always code in Tailwind CSS style
7. Before implementing any UI, review the project’s folder structure, coding conventions, tech stack, frameworks, and packages — including the package.json file — to ensure compliance. Always look for existing components that can be reused instead of coding them from scratch, and strictly follow the project’s established design system and styling guidelines.
8. Always separate components when coding UI, each file should only have 150–250 lines
9. If an issue has to be fixed multiple times, searching for related files may cause errors
10. When I request code for a UI interface, do not arbitrarily delete the API logic in the code under any circumstances; keep the API logic intact and only modify the UI.
11. Do not delete commented code
12. Do not arbitrarily delete my file code under any circumstances; Instead of deleting, please comment out the code file to disable it.
13. Please edit the file in small chunks
14.  [[calls]]
match = "when the user requests code examples, setup or configuration steps, or library/API documentation" tool = "context7"