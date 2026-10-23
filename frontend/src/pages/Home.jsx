import { useState, useEffect, useRef } from "react";

import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import ChatBox from "../components/ChatBox";
import MessageInput from "../components/MessageInput";


import {
  sendMessage,
  getDocuments,
  uploadPDF,
  deleteDocument,
} from "../api/ragApi";

function Home() {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [conversationMode, setConversationMode] = useState(false);
  const latestAnswer = useRef("");
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  const startListening = () => {

    if (!("webkitSpeechRecognition" in window)) {
      alert("Speech Recognition is not supported.");
      return;
    }

    if (!recognitionRef.current) {

      const recognition = new window.webkitSpeechRecognition();

      recognition.lang = "en-US";
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {
        setListening(true);
      };

      recognition.onresult = (event) => {

        const transcript =
          event.results[0][0].transcript;

        setListening(false);

        handleSend(transcript, true);
      };

      recognition.onend = () => {
        setListening(false);
      };

      recognition.onerror = () => {
        setListening(false);
      };

      recognitionRef.current = recognition;
    }

    try {
      recognitionRef.current.start();
    }
    catch (e) { }
  };

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
  useEffect(() => {

    if (conversationMode) {

      setTimeout(() => {
        startListening();
      }, 300);

    } else {

      speechSynthesis.cancel();

      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }

    }

  }, [conversationMode]);


  const handleUpload = async (file) => {
    try {
      await uploadPDF(file);
      await loadDocuments();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Upload failed");
    }
  };


  const handleDelete = async (filename) => {
    try {
      await deleteDocument(filename);
      await loadDocuments();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Delete failed");
    }
  };

  const handleSend = async (question, fromVoice = false) => {
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: question,
      },
    ]);

    setLoading(true);

    try {
      const response = await sendMessage(question, conversationId);
      setConversationId(response.conversation_id);
      latestAnswer.current = response.answer;

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.answer,
          sources: response.sources,
        },
      ]);

      if (conversationMode) {

        speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(response.answer);

        utterance.lang = "en-US";
        utterance.rate = 1;
        utterance.pitch = 1;

        utterance.onstart = () => {
          console.log("Assistant speaking...");
        };

        utterance.onend = () => {

          console.log("Assistant finished.");

          setTimeout(() => {

            if (conversationMode) {
              startListening();
            }

          }, 300);

        };

        speechSynthesis.speak(utterance);
      }

    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Navbar
        onMenuClick={() => setSidebarOpen(!sidebarOpen)}
      />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          documents={documents}
          onUpload={handleUpload}
          onDelete={handleDelete}
        />

        <div className="flex justify-end h-15 mt-147 p-3">
          <button
            onClick={() => setConversationMode(!conversationMode)}
            className={`px-4 py-2 rounded-lg text-white transition ${conversationMode
              ? "bg-green-600"
              : "bg-gray-600"
              }`}
          >
            {conversationMode
              ? "Conversation ON"
              : "Conversation OFF"}
          </button>
        </div>

        <main className="flex-1 flex flex-col">
          <ChatBox messages={messages}
            conversationMode={conversationMode}
          />
          {conversationMode && (
            <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/30">

              <div className="w-36 h-36 rounded-full bg-blue-600 animate-pulse flex items-center justify-center shadow-2xl">

                <div className="w-20 h-20 rounded-full bg-white flex items-center justify-center">
                  🎤
                </div>

              </div>

              <h2 className="mt-8 text-3xl font-bold text-white">
                Conversation Mode
              </h2>

              <p className="mt-2 text-blue-100">
                {listening
                  ? "Listening..."
                  : loading
                    ? "Thinking..."
                    : "Speaking..."}
              </p>

              <button
                onClick={() => setConversationMode(false)}
                className="mt-10 px-8 py-3 rounded-full bg-red-600 hover:bg-red-700 text-white font-semibold"
              >
                End Conversation
              </button>

            </div>
          )}

          <MessageInput
            onSend={handleSend}
            loading={loading}
            listening={listening}
            onMicClick={startListening}
            conversationMode={conversationMode}
          />
        </main>
      </div>
    </div>
  );
}

export default Home;