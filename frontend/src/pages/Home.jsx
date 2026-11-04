import { useState, useEffect, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle, CheckCircle2 } from "lucide-react";

import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import ChatBox from "../components/ChatBox";
import MessageInput from "../components/MessageInput";

import { sendMessage, getDocuments, uploadPDF, deleteDocument } from "../api/ragApi";

function Home() {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [conversationMode, setConversationMode] = useState(false);
  const [listening, setListening] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deletingFile, setDeletingFile] = useState(null);
  const [toast, setToast] = useState(null);

  const recognitionRef = useRef(null);
  const handleSendRef = useRef(null);
  const conversationModeRef = useRef(false);

  const showToast = (type, text) => {
    setToast({ type, text });
    setTimeout(() => setToast(null), 4500);
  };

  /* ---------- voice ---------- */

  const startListening = () => {
    if (!("webkitSpeechRecognition" in window)) {
      showToast("error", "Voice input is not supported in this browser. Try Chrome.");
      return;
    }

    if (!recognitionRef.current) {
      const recognition = new window.webkitSpeechRecognition();
      recognition.lang = "en-US";
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => setListening(true);
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setListening(false);
        handleSendRef.current?.(transcript, true);
      };
      recognition.onend = () => setListening(false);
      recognition.onerror = () => setListening(false);

      recognitionRef.current = recognition;
    }

    try {
      recognitionRef.current.start();
    } catch {
      /* already listening */
    }
  };

  useEffect(() => {
    conversationModeRef.current = conversationMode;

    if (conversationMode) {
      const t = setTimeout(startListening, 300);
      return () => clearTimeout(t);
    }

    speechSynthesis.cancel();
    recognitionRef.current?.stop();
  }, [conversationMode]);

  /* ---------- documents ---------- */

  const loadDocuments = async () => {
    try {
      const response = await getDocuments();
      setDocuments(response.documents);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleUpload = async (file) => {
    setUploading(true);
    try {
      await uploadPDF(file);
      await loadDocuments();
      showToast("ok", `${file.name} is ready. You can ask questions now.`);
    } catch (error) {
      console.error(error);
      const detail = error.response?.data?.detail;
      showToast("error", typeof detail === "string" ? detail : "Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (filename) => {
    setDeletingFile(filename);
    try {
      await deleteDocument(filename);
      await loadDocuments();
      showToast("ok", `${filename} was removed.`);
    } catch (error) {
      console.error(error);
      const detail = error.response?.data?.detail;
      showToast("error", typeof detail === "string" ? detail : "Delete failed. Please try again.");
    } finally {
      setDeletingFile(null);
    }
  };

  /* ---------- chat ---------- */

  const handleSend = async (question) => {
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const response = await sendMessage(question, conversationId);
      setConversationId(response.conversation_id);

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.answer, sources: response.sources },
      ]);

      if (conversationModeRef.current) {
        speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(response.answer.replace(/[*_`#>|]/g, ""));
        utterance.lang = "en-US";
        utterance.onend = () => {
          setTimeout(() => {
            if (conversationModeRef.current) startListening();
          }, 300);
        };
        speechSynthesis.speak(utterance);
      }
    } catch (error) {
      console.error(error);
      // Show the server's own message (for example the "too many questions" limit)
      const detail = error.response?.data?.detail;
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            typeof detail === "string"
              ? detail
              : "Something went wrong. If the server was asleep, please try again in a few seconds.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSendRef.current = handleSend;
  });

  const newChat = () => {
    speechSynthesis.cancel();
    setMessages([]);
    setConversationId(null);
  };

  return (
    <div className="h-dvh flex flex-col overflow-hidden">
      <div className="aurora" />

      <Navbar
        onMenuClick={() => setSidebarOpen(true)}
        onNewChat={newChat}
        conversationMode={conversationMode}
        onToggleConversation={() => setConversationMode((v) => !v)}
      />

      <div className="flex flex-1 min-h-0">
        <Sidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          documents={documents}
          onUpload={handleUpload}
          onDelete={handleDelete}
          uploading={uploading}
          deletingFile={deletingFile}
        />

        <main className="flex-1 min-w-0 flex flex-col min-h-0">
          <ChatBox messages={messages} loading={loading} onSuggest={handleSend} />

          <MessageInput
            onSend={handleSend}
            loading={loading}
            listening={listening}
            onMicClick={startListening}
            onAttach={handleUpload}
            uploading={uploading}
          />
        </main>
      </div>

      {/* Voice chat overlay */}
      <AnimatePresence>
        {conversationMode && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-white/70 backdrop-blur-xl"
          >
            <div
              className={`orb h-40 w-40 ${listening ? "orb-think" : ""}`}
            />
            <h2 className="mt-10 font-display text-4xl">Voice chat</h2>
            <p className="mt-2 text-muted">
              {listening ? "Listening…" : loading ? "Thinking…" : "Speaking…"}
            </p>
            <button
              onClick={() => setConversationMode(false)}
              className="mt-10 h-12 px-8 rounded-full bg-ink text-white font-medium cursor-pointer hover:bg-black transition"
            >
              End voice chat
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: -16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            className="fixed top-4 left-1/2 -translate-x-1/2 z-[60] glass rounded-full pl-4 pr-5 py-2.5 flex items-center gap-2 text-sm max-w-[92vw]"
          >
            {toast.type === "ok" ? (
              <CheckCircle2 size={17} className="text-emerald-600 shrink-0" />
            ) : (
              <AlertCircle size={17} className="text-red-600 shrink-0" />
            )}
            <span className="truncate">{toast.text}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default Home;
