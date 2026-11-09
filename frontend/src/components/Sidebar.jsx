import { useRef } from "react";
import { X, Upload, Trash2, FileText, Loader2, ShieldCheck } from "lucide-react";

function Sidebar({ isOpen, onClose, documents, onUpload, onDelete, uploading, deletingFile }) {
    const fileInputRef = useRef();

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        onUpload(file);
        e.target.value = "";
    };

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
                    <div className="flex items-center justify-between mb-5">
                        <h2 className="text-[13px] font-semibold tracking-wide uppercase text-muted">
                            Documents
                        </h2>
                        <button onClick={onClose} aria-label="Close" className="md:hidden cursor-pointer">
                            <X size={20} />
                        </button>
                    </div>

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
                </div>
            </aside>
        </>
    );
}

export default Sidebar;
