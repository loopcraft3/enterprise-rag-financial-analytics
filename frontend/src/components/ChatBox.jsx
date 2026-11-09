import { useEffect, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Upload, Loader2 } from "lucide-react";
import MessageList from "./MessageList";
import Thinking from "./Thinking";

const SUGGESTIONS = [
    "Summarise this document",
    "What is the total amount payable?",
    "Who is the supplier and what is the GSTIN?",
    "What is the net profit for the year?",
];

function ChatBox({ messages, loading, onSuggest, hasDocuments, onUpload, uploading }) {
    const lastRef = useRef(null);
    const thinkingRef = useRef(null);
    const fileRef = useRef(null);

    // New message (question or answer): bring ITS TOP to the top of the screen,
    // so the person starts reading the answer from its first line.
    useEffect(() => {
        if (messages.length === 0) return;
        const t = setTimeout(() => {
            lastRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 60);
        return () => clearTimeout(t);
    }, [messages.length]);

    return (
        <div className="flex-1 overflow-y-auto">
            <div className="max-w-3xl mx-auto px-4 md:px-6 pt-4 min-h-full flex flex-col">
                {messages.length === 0 ? (
                    <div className="flex-1 flex flex-col items-center justify-center text-center pb-10">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                            className="orb h-28 w-28 md:h-36 md:w-36"
                        />

                        <motion.h1
                            initial={{ opacity: 0, y: 16 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.15, duration: 0.6 }}
                            className="font-display text-[40px] leading-[1.05] md:text-6xl mt-8 tracking-tight"
                        >
                            Ask your documents
                            <br />
                            <span className="italic text-accent">anything.</span>
                        </motion.h1>

                        <motion.p
                            initial={{ opacity: 0, y: 12 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3, duration: 0.6 }}
                            className="mt-4 text-muted max-w-md text-[15px] leading-relaxed"
                        >
                            Hisaab reads your GST invoices, Form 16 and balance sheets, and answers with the page it
                            found it on.
                        </motion.p>

                        {hasDocuments ? (
                            <motion.div
                                initial={{ opacity: 0, y: 12 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.45, duration: 0.6 }}
                                className="mt-8 flex flex-wrap justify-center gap-2 max-w-xl"
                            >
                                {SUGGESTIONS.map((s) => (
                                    <button
                                        key={s}
                                        onClick={() => onSuggest(s)}
                                        className="glass rounded-full px-4 py-2 text-[13.5px] cursor-pointer hover:bg-white hover:-translate-y-0.5 transition"
                                    >
                                        {s}
                                    </button>
                                ))}
                            </motion.div>
                        ) : (
                            <motion.div
                                initial={{ opacity: 0, y: 12 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.45, duration: 0.6 }}
                                className="mt-8 flex flex-col items-center"
                            >
                                <input
                                    ref={fileRef}
                                    type="file"
                                    hidden
                                    accept=".pdf"
                                    onChange={(e) => {
                                        const f = e.target.files[0];
                                        if (f) onUpload(f);
                                        e.target.value = "";
                                    }}
                                />
                                <button
                                    onClick={() => fileRef.current.click()}
                                    disabled={uploading}
                                    className="h-12 px-7 rounded-full bg-ink text-white text-[15px] font-medium flex items-center gap-2 cursor-pointer
                                        hover:bg-black hover:-translate-y-0.5 transition disabled:opacity-60 disabled:cursor-wait"
                                >
                                    {uploading ? <Loader2 size={18} className="animate-spin" /> : <Upload size={18} />}
                                    {uploading ? "Reading your PDF…" : "Upload a PDF to start"}
                                </button>
                                <p className="text-xs text-muted mt-3">
                                    PDF only · up to 5 MB · private to this chat
                                </p>
                            </motion.div>
                        )}
                    </div>
                ) : (
                    <>
                        <MessageList messages={messages} lastRef={lastRef} />

                        <AnimatePresence>
                            {loading && (
                                <div ref={thinkingRef} className="mt-8">
                                    <Thinking />
                                </div>
                            )}
                        </AnimatePresence>

                        {/* extra space so the newest answer can scroll up to the top of the screen */}
                        <div className="h-[70vh] shrink-0" />
                    </>
                )}
            </div>
        </div>
    );
}

export default ChatBox;
