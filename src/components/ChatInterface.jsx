import { useState, useRef, useEffect } from "react";
import { Send, AlertCircle, RotateCcw } from "lucide-react";
import MessageBubble from "./MessageBubble";
import ResultCard from "./ResultCard";
import LoadingSkeleton from "./LoadingSkeleton";

async function fetchAssistantReply(question) {
  const response = await fetch("https://thirty-teeth-do.loca.lt", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error("Failed to get a response from the assistant.");
  }

  const data = await response.json();

  return {
    reply: data.answer,
    results: (data.sources || []).map((s) => ({
      standard: s,
      title: "",
      type: "",
    })),
  };
}
export default function ChatInterface({ t }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [lastError, setLastError] = useState(null);
  const scrollRef = useRef(null);

  const starterPrompts = [t.starter1, t.starter2, t.starter3];

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isLoading, lastError]);

  async function handleSend(text) {
    const question = (text ?? input).trim();
    if (!question || isLoading) return;

    setLastError(null);
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setIsLoading(true);

    try {
      const { reply, results } = await fetchAssistantReply(question);
      setMessages((prev) => [...prev, { role: "assistant", text: reply, results }]);
    } catch (err) {
      setLastError(question);
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    handleSend();
  }

  return (
    <section className="mx-auto max-w-5xl px-6 pb-16">
      <div className="overflow-hidden rounded-2xl border border-line bg-white shadow-[0_8px_30px_rgba(27,42,74,0.08)] dark:border-white/10 dark:bg-ink dark:shadow-[0_8px_30px_rgba(0,0,0,0.4)]">
        {/* Message list */}
        <div ref={scrollRef} className="chat-scroll h-[440px] space-y-4 overflow-y-auto p-6">
          {messages.length === 0 && !lastError && (
            <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
              <p className="text-sm text-slatelight">{t.tryAsking}</p>
              <div className="flex flex-col gap-2">
                {starterPrompts.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => handleSend(prompt)}
                    className="rounded-full border border-line px-4 py-2 text-[13px] text-slate transition hover:scale-105 hover:border-saffron hover:text-ink dark:border-white/15 dark:text-slatelight dark:hover:border-saffron dark:hover:text-white"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, i) => (
            <div key={i} className="space-y-2">
              <MessageBubble role={m.role} text={m.text} />
              {m.results && (
                <div className="ml-1 space-y-2">
                  {m.results.map((r, j) => (
                    <ResultCard key={j} {...r} />
                  ))}
                </div>
              )}
            </div>
          ))}

          {isLoading && <LoadingSkeleton />}

          {lastError && !isLoading && (
            <div className="flex items-start gap-3 rounded-xl border border-saffron/30 bg-saffron/5 p-4 dark:bg-saffron/10">
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-saffron" />
              <div className="flex-1">
                <p className="text-[14px] text-ink dark:text-white">{t.errorMsg}</p>
                <button
                  onClick={() => handleSend(lastError)}
                  className="mt-2 flex items-center gap-1.5 text-[13px] font-medium text-saffron hover:underline"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  {t.retry}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Input bar */}
        <form onSubmit={handleSubmit} className="flex items-center gap-2 border-t border-line bg-canvas/50 p-4 dark:border-white/10 dark:bg-white/5">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t.placeholder}
            className="flex-1 rounded-full border border-line bg-white px-4 py-2.5 text-[14px] text-ink outline-none placeholder:text-slatelight focus:border-saffron dark:border-white/15 dark:bg-transparent dark:text-white dark:focus:border-saffron"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="flex items-center gap-1.5 rounded-full bg-gradient-to-r from-ink to-inkdark px-5 py-2.5 text-[14px] font-medium text-white shadow-md transition hover:scale-105 hover:shadow-lg disabled:opacity-40 dark:from-white dark:to-white dark:text-ink"
          >
            <Send className="h-4 w-4" />
            {t.send}
          </button>
        </form>
      </div>
    </section>
  );
}
