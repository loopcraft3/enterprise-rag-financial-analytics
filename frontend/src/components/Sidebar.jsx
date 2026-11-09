import { useRef, useState } from "react";
import { X, Upload, Trash2, FileText, Loader2, ShieldCheck, MessageSquare, History } from "lucide-react";

function when(ts) {
    const d = new Date(ts);
    const now = new Date();
    const sameDay = d.toDateString() === now.toDateString();
    if (sameDay) return d.toLocaleTimeString("en-IN", { hour: "numeric", minute: "2-digit" });

    const y = new Date();
    y.setDate(now.getDate() - 1);
    if (d.toDateString() === y.toDateString()) return "Yesterday";

    return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

function Sidebar({
    isOpen,
    onClose,
    documents,
    onUpload,
    onDelete,
    uploading,
    deletingFile,
    history = [],
    activeChatId,
    onOpenChat,
    onDeleteChat,
    onClearHistory,
}) {
    const fileInputRef = useRef();
    const [tab, setTab] = useState("docs");

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        onUpload(file);
        e.target.value = "";
    };

    const tabClass = (name) =>
        `flex-1 h-9 rounded-full text-[13px] font-medium flex items-center justify-center gap-1.5 cursor-pointer transition
        ${tab === name ? "bg-ink text-white" : "text-muted hover:text-ink"}`;

    return (
        <>
            <div
                onClick={onClose}
                className={`fixed inset-0 z-30 bg-ink/30 backdrop-blur-sm md:hidden transition-opacity duration-300
                    ${isOpen ? "opacity-100" : "opacity-0 pointer-events-none"}`}
            />

            <aside
                className={`fixed md:static inset-y-0 left-0 z-40 w-[300px] md:w-[290px] shrink-0
                    p-3 md:p-0 md:pl-4 md:pb-4
                    transition-transform duration-300 ease-out
                    ${isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}`}
            >
                <div className="glass rounded-3xl h-full flex flex-col p-5">
                    <div className="flex items-center gap-2 mb-5">
                        <div className="flex-1 flex gap-1 p-1 rounded-full bg-white/60 border border-line" role="tablist">
                            <button role="tab" aria-selected={tab === "docs"} onClick={() => setTab("docs")} className={tabClass("docs")}>
                                <FileText size={14} />
                                Documents
                            </button>
                            <button role="tab" aria-selected={tab === "history"} onClick={() => setTab("history")} className={tabClass("history")}>
                                <History size={14} />
                                History
                                {history.length > 0 && (
                                    <span className={`text-[11px] ${tab === "history" ? "text-white/70" : "text-muted"}`}>
                                        {history.length}
                                    </span>
                                )}
                            </button>
                        </div>
                        <button onClick={onClose} aria-label="Close" className="md:hidden cursor-pointer">
                            <X size={20} />
                        </button>
                    </div>

                    {tab === "docs" ? (
                        <>
                            <button
                                onClick={() => fileInputRef.current.click()}
                                disabled={uploading}
                                className="w-full rounded-2xl py-3 flex justify-center items-center gap-2 text-sm font-medium cursor-pointer
                                    bg-ink text-white hover:bg-black transition disabled:opacity-60 disabled:cursor-wait"
                            >
                                {uploading ? (
                                    <>
                                        <Loader2 size={17} className="animate-spin" />
                                        Reading your PDF…
                                    </>
                                ) : (
                                    <>
                                        <Upload size={17} />
                                        Upload a PDF
                                    </>
                                )}
                            </button>
                            <p className="text-xs text-muted text-center mt-2">PDF only · up to 5 MB</p>

                            <input
                                ref={fileInputRef}
                                type="file"
                                hidden
                                accept=".pdf"
                                onChange={handleFileChange}
                            />

                            <div className="mt-6 flex-1 overflow-y-auto space-y-2 -mr-2 pr-2">
                                {documents.length === 0 ? (
                                    <div className="text-center text-sm text-muted mt-10 px-2">
                                        No documents yet.
                                        <br />
                                        Upload a PDF to begin.
                                    </div>
                                ) : (
                                    documents.map((doc) => (
                                        <div
                                            key={doc.filename}
                                            className="group rounded-2xl bg-white/70 border border-line px-3 py-3 flex items-center justify-between gap-2"
                                        >
                                            <div className="flex gap-3 items-center overflow-hidden">
                                                <span className="h-9 w-9 shrink-0 rounded-xl bg-accent/10 text-accent grid place-items-center">
                                                    <FileText size={17} />
                                                </span>
                                                <span className="truncate text-sm" title={doc.filename}>
                                                    {doc.filename}
                                                </span>
                                            </div>

                                            <button
                                                onClick={() => onDelete(doc.filename)}
                                                disabled={deletingFile === doc.filename}
                                                aria-label={`Delete ${doc.filename}`}
                                                className="shrink-0 text-muted hover:text-red-600 cursor-pointer disabled:cursor-wait"
                                            >
                                                {deletingFile === doc.filename ? (
                                                    <Loader2 size={17} className="animate-spin" />
                                                ) : (
                                                    <Trash2 size={17} />
                                                )}
                                            </button>
                                        </div>
                                    ))
                                )}
                            </div>

                            <div className="mt-4 flex gap-2 text-xs text-muted leading-relaxed">
                                <ShieldCheck size={16} className="shrink-0 mt-0.5" />
                                <span>
                                    Your files are private to this chat. Answers come only from the documents listed here.
                                    Starting a new chat clears them, and they are deleted automatically after a few hours.
                                </span>
                            </div>
                        </>
                    ) : (
                        <>
                            <div className="flex-1 overflow-y-auto space-y-2 -mr-2 pr-2">
                                {history.length === 0 ? (
                                    <div className="text-center text-sm text-muted mt-10 px-2">
                                        No saved chats yet.
                                        <br />
                                        Your chats will show up here.
                                    </div>
                                ) : (
                                    history.map((chat) => {
                                        const active = chat.id === activeChatId;
                                        return (
                                            <div
                                                key={chat.id}
                                                className={`group rounded-2xl border px-3 py-2.5 flex items-center justify-between gap-2 transition
                                                    ${active ? "bg-white border-accent/40" : "bg-white/70 border-line hover:bg-white"}`}
                                            >
                                                <button
                                                    onClick={() => onOpenChat(chat.id)}
                                                    className="flex gap-3 items-center overflow-hidden text-left flex-1 min-w-0 cursor-pointer"
                                                    title={chat.title}
                                                >
                                                    <span className="h-9 w-9 shrink-0 rounded-xl bg-accent/10 text-accent grid place-items-center">
                                                        <MessageSquare size={16} />
                                                    </span>
                                                    <span className="min-w-0">
                                                        <span className="block truncate text-sm">{chat.title}</span>
                                                        <span className="block text-[11.5px] text-muted">{when(chat.updatedAt)}</span>
                                                    </span>
                                                </button>

                                                <button
                                                    onClick={() => onDeleteChat(chat.id)}
                                                    aria-label={`Delete chat ${chat.title}`}
                                                    className="shrink-0 text-muted hover:text-red-600 cursor-pointer"
                                                >
                                                    <Trash2 size={16} />
                                                </button>
                                            </div>
                                        );
                                    })
                                )}
                            </div>

                            {history.length > 0 && (
                                <button
                                    onClick={onClearHistory}
                                    className="mt-3 text-xs text-muted hover:text-red-600 cursor-pointer self-center"
                                >
                                    Clear all history
                                </button>
                            )}

                            <div className="mt-4 flex gap-2 text-xs text-muted leading-relaxed">
                                <ShieldCheck size={16} className="shrink-0 mt-0.5" />
                                <span>
                                    Saved only in this browser. Nothing is stored on our server. The PDFs are never saved, so
                                    upload them again to ask new questions.
                                </span>
                            </div>
                        </>
                    )}
                </div>
            </aside>
        </>
    );
}

export default Sidebar;
