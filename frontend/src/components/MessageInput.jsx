import { useState, useRef, useEffect } from "react";
import { ArrowUp, Mic, Paperclip, Loader2 } from "lucide-react";

function MessageInput({ onSend, loading, listening, onMicClick, onAttach, uploading }) {
    const [question, setQuestion] = useState("");
    const textRef = useRef(null);
    const fileRef = useRef(null);

    // grow the box as the person types (up to ~6 lines)
    useEffect(() => {
        const el = textRef.current;
        if (!el) return;
        el.style.height = "auto";
        el.style.height = Math.min(el.scrollHeight, 150) + "px";
    }, [question]);

    const handleSubmit = () => {
        const text = question.trim();
        if (!text || loading) return;
        onSend(text);
        setQuestion("");
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const canSend = question.trim() && !loading;

    return (
        <div className="shrink-0 px-3 md:px-6 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-2">
            <div className="max-w-3xl mx-auto">
                <div className="glass rounded-[28px] p-2.5 transition focus-within:shadow-[0_0_0_4px_rgba(109,94,252,0.14),0_10px_40px_-12px_rgba(80,60,160,0.25)]">
                    <textarea
                        ref={textRef}
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask about your invoices, Form 16, balance sheets…"
                        rows={1}
                        className="w-full resize-none bg-transparent px-3 pt-2 pb-1 text-[15.5px] placeholder:text-muted/70 focus:outline-none"
                    />

                    <div className="flex items-center justify-between mt-1">
                        <div className="flex items-center gap-1.5">
                            <input
                                ref={fileRef}
                                type="file"
                                hidden
                                accept=".pdf"
                                onChange={(e) => {
                                    const f = e.target.files[0];
                                    if (f) onAttach(f);
                                    e.target.value = "";
                                }}
                            />
                            <button
                                onClick={() => fileRef.current.click()}
                                disabled={uploading}
                                className="h-9 px-3 rounded-full bg-white/70 border border-line text-[13px] flex items-center gap-1.5 cursor-pointer hover:bg-white transition disabled:opacity-60"
                            >
                                {uploading ? <Loader2 size={15} className="animate-spin" /> : <Paperclip size={15} />}
                                {uploading ? "Uploading" : "Attach PDF"}
                            </button>
                        </div>

                        <div className="flex items-center gap-2">
                            <button
                                onClick={onMicClick}
                                disabled={loading}
                                aria-label="Speak your question"
                                className={`h-9 w-9 rounded-full grid place-items-center cursor-pointer transition
                                    ${listening ? "bg-red-500 text-white animate-pulse" : "bg-white/70 border border-line hover:bg-white"}`}
                            >
                                <Mic size={16} />
                            </button>

                            <button
                                onClick={handleSubmit}
                                disabled={!canSend}
                                aria-label="Send"
                                className="h-9 w-9 rounded-full grid place-items-center text-white cursor-pointer transition
                                    bg-gradient-to-br from-accent to-accent-2 hover:scale-105 active:scale-95
                                    disabled:from-gray-300 disabled:to-gray-300 disabled:hover:scale-100 disabled:cursor-not-allowed"
                            >
                                {loading ? <Loader2 size={16} className="animate-spin" /> : <ArrowUp size={18} />}
                            </button>
                        </div>
                    </div>
                </div>

                <p className="text-center text-[11.5px] text-muted mt-2">
                    Hisaab can make mistakes. Check important figures. Not financial advice.
                </p>
            </div>
        </div>
    );
}

export default MessageInput;
