import { ShieldCheck, Sun, Moon, Languages } from "lucide-react";

export default function Navbar({ t, isDark, onToggleDark, lang, onToggleLang }) {
  return (
    <header className="sticky top-0 z-10 border-b border-line bg-white/80 backdrop-blur-md dark:border-white/10 dark:bg-inkdark/80">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-ink dark:bg-white">
            <ShieldCheck className="h-5 w-5 text-white dark:text-ink" strokeWidth={1.75} />
          </div>
          <div className="leading-tight">
            <p className="text-[15px] font-semibold text-ink dark:text-white">{t.brand}</p>
            <p className="text-xs text-slatelight">{t.brandSub}</p>
          </div>
        </div>

        <div className="flex items-center gap-5">
          <nav className="hidden items-center gap-6 text-sm text-slate dark:text-slatelight sm:flex">
            <a href="#" className="transition hover:text-ink dark:hover:text-white">{t.navCertification}</a>
            <a href="#" className="transition hover:text-ink dark:hover:text-white">{t.navClubs}</a>
            <a href="#" className="transition hover:text-ink dark:hover:text-white">{t.navHallmarking}</a>
            <a href="#" className="transition hover:text-ink dark:hover:text-white">{t.navHelp}</a>
          </nav>

          <div className="flex items-center gap-2">
            {/* Language toggle */}
            <button
              onClick={onToggleLang}
              aria-label="Switch language"
              className="flex h-8 items-center gap-1.5 rounded-full border border-line px-3 text-xs font-medium text-slate transition hover:scale-105 hover:border-ink hover:text-ink dark:border-white/20 dark:text-slatelight dark:hover:border-white dark:hover:text-white"
            >
              <Languages className="h-3.5 w-3.5" />
              {lang === "en" ? "हिं" : "EN"}
            </button>

            {/* Dark mode toggle */}
            <button
              onClick={onToggleDark}
              aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
              className="flex h-8 w-8 items-center justify-center rounded-full border border-line text-slate transition hover:scale-105 hover:border-ink hover:text-ink dark:border-white/20 dark:text-slatelight dark:hover:border-white dark:hover:text-white"
            >
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
