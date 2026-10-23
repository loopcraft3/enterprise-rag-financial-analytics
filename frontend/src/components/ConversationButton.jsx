import { useEffect, useRef, useState } from "react";
import { Mic, Square } from "lucide-react";
import { sendMessage } from "../services/chat";

function ConversationButton({ onNewMessage }) {
    const recognitionRef = useRef(null);

    const [conversationMode, setConversationMode] = useState(false);
    const [listening, setListening] = useState(false);
    const [speaking, setSpeaking] = useState(false);

    useEffect(() => {
        const SpeechRecognition =
            window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            alert("Speech Recognition is not supported in this browser.");
            return;
        }

        const recognition = new SpeechRecognition();

        recognition.lang = "en-US";
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
            setListening(true);
        };

        recognition.onend = () => {
            setListening(false);
        };

        recognition.onerror = (e) => {
            console.log(e.error);

            setListening(false);

            if (conversationMode && !speaking) {
                recognition.start();
            }
        };

        recognition.onresult = async (event) => {
            const question = event.results[0][0].transcript;

            onNewMessage({
                role: "user",
                content: question,
            });

            try {
                const response = await sendMessage(question);

                onNewMessage({
                    role: "assistant",
                    content: response.answer,
                });

                speak(response.answer);

            } catch (err) {
                console.log(err);
            }
        };

        recognitionRef.current = recognition;
    }, [conversationMode, speaking]);

    const speak = (text) => {
        speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);

        utterance.lang = "en-US";
        utterance.rate = 1;
        utterance.pitch = 1;

        utterance.onstart = () => {
            setSpeaking(true);
        };

        utterance.onend = () => {
            setSpeaking(false);

            if (conversationMode) {
                recognitionRef.current.start();
            }
        };

        speechSynthesis.speak(utterance);
    };

    const startConversation = () => {
        setConversationMode(true);
        recognitionRef.current.start();
    };

    const stopConversation = () => {
        setConversationMode(false);

        speechSynthesis.cancel();

        recognitionRef.current.stop();

        setListening(false);
        setSpeaking(false);
    };

    return (
        <button
            onClick={
                conversationMode
                    ? stopConversation
                    : startConversation
            }
            className={`px-4 py-2 rounded-xl text-white flex items-center gap-2
            ${
                conversationMode
                    ? "bg-red-600"
                    : "bg-green-600"
            }`}
        >
            {conversationMode ? (
                <>
                    <Square size={18} />
                    Stop Conversation
                </>
            ) : (
                <>
                    <Mic size={18} />
                    Conversation
                </>
            )}

            {listening && " 🎤"}
            {speaking && " 🔊"}
        </button>
    );
}

export default ConversationButton;