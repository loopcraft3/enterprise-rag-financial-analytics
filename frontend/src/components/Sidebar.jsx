
import { useRef } from "react";
import { X, Upload, Trash2, FileText } from "lucide-react";

function Sidebar({
    isOpen,
    onClose,
    documents,
    onUpload,
    onDelete,
}) {
    const fileInputRef = useRef();

    const handleFileChange = (e) => {
        const file = e.target.files[0];

        if (!file) return;

        onUpload(file);

        e.target.value = "";
    };

    return (
        <>
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-30 md:hidden"
                    onClick={onClose}
                />
            )}

            <aside
                className={`
        fixed md:static
        top-16 left-0
        h-[calc(100vh-4rem)]
        w-72
        bg-white
        border-r
        z-40
        transform
        transition-transform
        duration-300
        ${isOpen
                        ? "translate-x-0"
                        : "-translate-x-full md:translate-x-0"
                    }
      `}
            >
                <div className="p-5 flex flex-col h-full">
                    <div className="flex items-center justify-between mb-5">
                        <h2 className="text-xl font-semibold">
                            Documents
                        </h2>

                        <button
                            onClick={onClose}
                            className="md:hidden"
                        >
                            <X size={22} />
                        </button>
                    </div>

                    <button
                        onClick={() => fileInputRef.current.click()}
                        className="cursor-pointer w-full bg-blue-600 text-white rounded-lg py-2 flex justify-center items-center gap-2 hover:bg-blue-700"
                    >
                        <Upload size={18} />
                        Upload PDF (max50MB)
                    </button>

                    <input
                        ref={fileInputRef}
                        type="file"
                        hidden
                        accept=".pdf"
                        onChange={handleFileChange}
                    />

                    <div className="mt-6 flex-1 overflow-y-auto space-y-3">
                        {documents.length === 0 ? (
                            <div className="text-center text-gray-500 mt-10">
                                Except default docs "RAG pdf" <br></br>No documents uploaded, <br></br> <span className="text-red-600 text-sm">
                                    After uploading a PDF, please wait a few seconds for the backend RAG pipeline to complete before asking questions.
                                </span>
                            </div>
                        ) : (
                            documents.map((doc) => (
                                <div
                                    key={doc.filename}
                                    className="border rounded-lg p-3 flex justify-between items-center"
                                >
                                    <div className="flex gap-2 items-center overflow-hidden">
                                        <FileText size={18} />

                                        <span className="truncate text-sm">
                                            {doc.filename}
                                        </span>
                                    </div>

                                    <button
                                        onClick={() =>
                                            onDelete(doc.filename)
                                        }
                                        className="text-red-500 cursor-pointer hover:text-red-700"
                                    >
                                        <Trash2 size={18} />
                                    </button>

                                </div>

                            ))

                        )}
                        {documents.length > 0 && (
                            <div className="mt-4 rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                                Please click the <strong>Delete</strong> button only once and wait a few seconds while all related vectors are compleately removed from the vector database.
                            </div>
                        )}
                    </div>
                </div>
            </aside>
        </>
    );
}

export default Sidebar;