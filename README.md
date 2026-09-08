# BIS Standards Assistant — Frontend

A starter React app for the SIH problem statement "AI-powered Intelligent
Assistant for Indian Standards and BIS Services." It includes a working chat
UI with placeholder responses — swap one function to connect it to your
team's real backend.

## 1. Install requirements (one-time)

- Install [Node.js](https://nodejs.org) (LTS version) if you don't have it.
- Install [VS Code](https://code.visualstudio.com) if you don't have it.

## 2. Run the project

Open a terminal in this folder and run:

```bash
npm install
npm run dev
```

Then open the URL it prints (usually `http://localhost:5173`) in your browser.

## 3. Project structure

```
src/
  App.jsx                 -> assembles the page (Navbar + Hero + Chat + Footer)
  index.css                -> global styles, Tailwind setup
  components/
    Navbar.jsx              -> top header
    Hero.jsx                -> intro heading/text
    ChatInterface.jsx        -> the main chat UI (the core feature)
    MessageBubble.jsx        -> a single chat message (user or assistant)
    ResultCard.jsx           -> a card showing one matched standard/scheme
    Footer.jsx                -> bottom credit line
```

## 4. Connecting to the real backend

Open `src/components/ChatInterface.jsx` and find the function
`fetchAssistantReply`. Right now it returns fake placeholder data after a
short delay. Once your backend/AI teammate gives you a real API endpoint,
replace the inside of that function with something like:

```javascript
async function fetchAssistantReply(question) {
  const response = await fetch("https://your-backend-url.com/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  const data = await response.json();
  // Make sure data looks like: { reply: "...", results: [{ standard, title, type }] }
  return data;
}
```

Nothing else in the app needs to change — every other component just
displays whatever this function returns.

## 5. Where to make changes for common tasks

- **Change colors/fonts** → `tailwind.config.js`
- **Change the heading/intro text** → `src/components/Hero.jsx`
- **Add a new page/section** → create a new file in `src/components/`, then
  import and use it inside `src/App.jsx`
- **Change starter example questions** → `STARTER_PROMPTS` array at the top of
  `ChatInterface.jsx`

## 6. Team workflow

Each person should create their own branch before making changes:

```bash
git checkout -b your-name-feature
git add .
git commit -m "describe what you changed"
git push origin your-name-feature
```

Then open a Pull Request on GitHub to merge into `main`.
