export default function Footer({ t }) {
  return (
    <footer className="border-t border-line py-6 dark:border-white/10">
      <p className="mx-auto max-w-5xl px-6 text-xs text-slatelight">
        {t.footer}
      </p>
    </footer>
  );
}
