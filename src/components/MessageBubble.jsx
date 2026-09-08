export default function MessageBubble({ role, text }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={
          isUser
            ? "max-w-[80%] rounded-2xl rounded-br-sm bg-gradient-to-br from-ink to-inkdark px-4 py-2.5 text-[14px] leading-relaxed text-white shadow-sm dark:from-white dark:to-white dark:text-ink"
            : "max-w-[80%] rounded-2xl rounded-bl-sm border border-line bg-white px-4 py-2.5 text-[14px] leading-relaxed text-slate shadow-sm dark:border-white/10 dark:bg-white/5 dark:text-slatelight"
        }
      >
        {text}
      </div>
    </div>
  );
}
