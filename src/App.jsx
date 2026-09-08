import { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import ChatInterface from "./components/ChatInterface";
import Footer from "./components/Footer";
import { translations } from "./translations";

export default function App() {
  const [isDark, setIsDark] = useState(() => localStorage.getItem("theme") === "dark");
  const [lang, setLang] = useState(() => localStorage.getItem("lang") || "en");

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDark);
    localStorage.setItem("theme", isDark ? "dark" : "light");
  }, [isDark]);

  useEffect(() => {
    localStorage.setItem("lang", lang);
  }, [lang]);

  const t = translations[lang];

  return (
    <div className="page-backdrop relative flex min-h-screen flex-col bg-canvas dark:bg-inkdark">
      <Navbar
        t={t}
        isDark={isDark}
        onToggleDark={() => setIsDark((d) => !d)}
        lang={lang}
        onToggleLang={() => setLang((l) => (l === "en" ? "hi" : "en"))}
      />
      <main className="relative z-10 flex-1">
        <Hero t={t} />
        <ChatInterface t={t} />
      </main>
      <Footer t={t} />
    </div>
  );
}
