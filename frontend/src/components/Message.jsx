import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Volume2, Square, Copy, Check, FileText } from "lucide-react";

const mdComponents = {
    table: ({ children }) => (
        <div className="table-wrap">
            <table>{children}</table>
        </div>
    ),
};

function uniqueSources(sources = []) {
    const seen = new Set();
    return sources.filter((s) => {
        const key = `${s.source}|${s.page}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });
}

function Message({ message }) {
    const isUser = message.role === "user";
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [copied, setCopied] = useState(false);

    const speakMessage = () => {
        speechSynthesis.cancel();
        // strip markdown symbols so they are not read aloud
        const spokenText = message.content.replace(/[*_`#>|]/g, "");
        const utterance = new SpeechSynthesisUtterance(spokenText);
        utterance.lang = "en-US";
        utterance.onstart = () => setIsSpeaking(true);
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => setIsSpeaking(false);
        speechSynthesis.speak(utterance);
    };

    const stopSpeaking = () => {
        speechSynthesis.cancel();
        setIsSpeaking(false);
    };

    const copy = async () => {
        try {
            await navigator.clipboard.writeText(message.content);
            setCopied(true);
            setTimeout(() => setCopied(false), 1500);
        } catch {
            /* clipboard blocked: ignore */
        }
    };

    if (isUser) {
        return (
            <div className="flex justify-end">
                <div className="max-w-[88%] md:max-w-[75%] rounded-3xl rounded-br-lg bg-ink text-white px-5 py-3 text-[15.5px] leading-relaxed whitespace-pre-wrap break-words shadow-lg shadow-ink/10">
                    {message.content}
                </div>
            </div>
        );
    }

    const sources = uniqueSources(message.sources);

    return (
        <div className="flex items-start gap-3">
            <div className="orb h-8 w-8 shrink-0 mt-0.5" style={{ animation: "none" }} />

            <div className="min-w-0 flex-1">
                <div className="prose-hisaab">
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
                        {message.content}
                    </ReactMarkdown>
                </div>

                {sources.length > 0 && (
                    <div className="mt-4 flex flex-wrap items-center gap-2">
                        <span className="text-xs text-muted mr-1">Sources</span>
                        {sources.map((s) => (
                            <span
                                key={`${s.source}-${s.page}`}
                                className="inline-flex items-center gap-1.5 rounded-full bg-white/80 border border-line px-3 py-1 text-xs"
                            >
                                <FileText size={12} className="text-accent" />
                                <span className="max-w-[180px] truncate">{s.source}</span>
                                {s.page != null && <span className="text-muted">· p.{s.page}</span>}
                            </span>
                        ))}
                    </div>
                )}

                <div className="mt-3 flex items-center gap-1 text-muted">
                    <button
                        onClick={isSpeaking ? stopSpeaking : speakMessage}
                        className="h-8 px-2.5 rounded-full flex items-center gap-1.5 text-xs hover:bg-white/80 cursor-pointer transition"
                    >
                        {isSpeaking ? <Square size={14} /> : <Volume2 size={14} />}
                        {isSpeaking ? "Stop" : "Listen"}
                    </button>
                    <button
                        onClick={copy}
                        className="h-8 px-2.5 rounded-full flex items-center gap-1.5 text-xs hover:bg-white/80 cursor-pointer transition"
                    >
                        {copied ? <Check size={14} /> : <Copy size={14} />}
                        {copied ? "Copied" : "Copy"}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Message;
