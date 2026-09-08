// A shimmering placeholder shown while waiting for the assistant's reply.
// Mimics the shape of a real reply (a text line + a couple of result cards)
// so the layout doesn't jump once the real content arrives.
export default function LoadingSkeleton() {
  return (
    <div className="space-y-3">
      {/* Fake assistant text bubble */}
      <div className="max-w-[80%] space-y-2 rounded-2xl rounded-bl-sm border border-line bg-white p-4 dark:border-white/10 dark:bg-white/5">
        <div className="h-3 w-full animate-pulse rounded bg-line dark:bg-white/10" />
        <div className="h-3 w-4/5 animate-pulse rounded bg-line dark:bg-white/10" />
        <div className="h-3 w-2/3 animate-pulse rounded bg-line dark:bg-white/10" />
      </div>

      {/* Fake result cards */}
      {[0, 1].map((i) => (
        <div
          key={i}
          className="flex items-start gap-3 rounded-xl border border-line bg-white p-4 dark:border-white/10 dark:bg-white/5"
        >
          <div className="h-9 w-9 shrink-0 animate-pulse rounded-lg bg-line dark:bg-white/10" />
          <div className="flex-1 space-y-2">
            <div className="h-3 w-1/3 animate-pulse rounded bg-line dark:bg-white/10" />
            <div className="h-3 w-3/4 animate-pulse rounded bg-line dark:bg-white/10" />
          </div>
        </div>
      ))}
    </div>
  );
}
