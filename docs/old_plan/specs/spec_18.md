# Spec 18 – Design the HTML/CSS layout

This specification provides a minimalistic white‑themed interface reminiscent of Google Search.  The front‑end uses plain HTML, CSS and vanilla JavaScript.

## HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knowledge Search</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="container">
        <form id="search-form">
            <input id="query" type="text" placeholder="Ask a question…" required />
            <button type="submit">Search</button>
        </form>
        <section id="answer-section">
            <div id="answer"></div>
            <div id="citations"></div>
        </section>
        <section id="resources-section">
            <h3>Internal Documents</h3>
            <ul id="internal-links"></ul>
            <h3>External Resources</h3>
            <ul id="external-links"></ul>
        </section>
        <section id="youtube-section">
            <h3>Related Videos</h3>
            <div id="youtube-thumbnails"></div>
        </section>
        <section id="questions-section">
            <h3>People also ask</h3>
            <ul id="related-questions"></ul>
        </section>
        <aside id="pinned-notes">
            <h3>Pinned</h3>
            <ul id="pinned-list"></ul>
        </aside>
        <button id="download-md" disabled>Download as Markdown</button>
    </div>
    <script src="script.js"></script>
</body>
</html>
```

## CSS Styling

Create `style.css` with a clean design:

```css
body {
    font-family: Arial, sans-serif;
    background-color: #ffffff;
    color: #333;
    margin: 0;
    padding: 0;
}

#container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
}

#search-form {
    display: flex;
    justify-content: center;
    margin-bottom: 1rem;
}

#query {
    flex: 1;
    padding: 0.5rem;
    font-size: 1.2rem;
}

#answer-section {
    margin-top: 1rem;
}

/* Additional styles for lists, thumbnails, pinned notes, etc. */
```

## Accessibility and Responsiveness

Use semantic HTML elements (form, sections, headings) and ensure that buttons have accessible labels.  Design the layout to collapse gracefully on smaller screens using responsive CSS (flexbox, media queries).  Provide focus states for interactive elements.
