import { FileText } from "lucide-react";

export default function ResultCard({ standard, title, type }) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-line bg-white p-4 shadow-sm transition hover:border-saffron/40 dark:border-white/10 dark:bg-white/5">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-saffron/10">
        <FileText className="h-4.5 w-4.5 text-saffron" strokeWidth={1.75} />
      </div>
      <div>
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs font-medium text-ink dark:text-white">{standard}</span>
          {type && (
            <span className="rounded-full bg-canvas px-2 py-0.5 text-[11px] text-slatelight dark:bg-white/10">
              {type}
            </span>
          )}
        </div>
        <p className="mt-1 text-[14px] text-slate dark:text-slatelight">{title}</p>
      </div>
    </div>
  );
}
