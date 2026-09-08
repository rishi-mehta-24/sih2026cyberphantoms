export default function Hero({ t }) {
  return (
    <section className="relative overflow-hidden px-6 pt-16 pb-10">
      {/* Soft decorative glow behind the heading — purely visual, no impact on layout */}
      <div className="pointer-events-none absolute left-1/2 top-0 h-72 w-[36rem] -translate-x-1/2 rounded-full bg-saffron/10 blur-3xl dark:bg-saffron/5" />

      <div className="relative mx-auto max-w-5xl">
        <span className="inline-flex items-center gap-1.5 rounded-full border border-saffron/30 bg-saffron/10 px-3 py-1 font-mono text-xs uppercase tracking-wide text-saffron">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-saffron" />
          {t.eyebrow}
        </span>

        <h1 className="font-heading mt-4 flex max-w-2xl items-center gap-3 text-4xl leading-tight text-ink dark:text-white sm:text-5xl">
          <IndianFlagIcon className="h-7 w-10 shrink-0 rounded-sm shadow-sm sm:h-9 sm:w-12" />
          {t.heading}
        </h1>

        <p className="mt-4 max-w-xl text-[15px] leading-relaxed text-slate dark:text-slatelight">
          {t.subheading}
        </p>
      </div>
    </section>
  );
}

// A small, accurate rendering of the Indian national flag as SVG — renders
// identically on every OS/browser, unlike the 🇮🇳 emoji which some Windows
// setups show as plain text ("IN") instead of an actual flag.
function IndianFlagIcon({ className }) {
  return (
    <svg viewBox="0 0 30 20" className={className} role="img" aria-label="Flag of India">
      <rect width="30" height="20" fill="#FFFFFF" />
      <rect width="30" height="6.67" fill="#FF9933" />
      <rect y="13.33" width="30" height="6.67" fill="#138808" />
      <circle cx="15" cy="10" r="2.5" fill="none" stroke="#000080" strokeWidth="0.3" />
      <circle cx="15" cy="10" r="0.35" fill="#000080" />
      {Array.from({ length: 24 }).map((_, i) => (
        <line
          key={i}
          x1="15"
          y1="10"
          x2={15 + 2.5 * Math.cos((i * 15 * Math.PI) / 180)}
          y2={10 + 2.5 * Math.sin((i * 15 * Math.PI) / 180)}
          stroke="#000080"
          strokeWidth="0.12"
        />
      ))}
    </svg>
  );
}
