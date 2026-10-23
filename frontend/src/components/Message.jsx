import { useState } from "react";
import { Volume2, Square } from "lucide-react";


function Message({ message }) {

    const isUser = message.role === "user";

    const [isSpeaking, setIsSpeaking] = useState(false);

    const speakMessage = () => {
        speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(message.content);

        utterance.lang = "en-US";
        utterance.rate = 1;
        utterance.pitch = 1;
        utterance.volume = 1;

        speechSynthesis.speak(utterance);


        utterance.onstart = () => {
            setIsSpeaking(true);
        };

        utterance.onend = () => {
            setIsSpeaking(false);

            if (window.startConversationListening) {
                window.startConversationListening();
            }
        };

        utterance.onerror = () => {
            setIsSpeaking(false);
        };

        speechSynthesis.speak(utterance);
    };

    const stopSpeaking = () => {
        speechSynthesis.cancel();
        setIsSpeaking(false);
        window.startConversationListening = null;
    };

    return (
        <div
            className={`flex mb-6 ${isUser ? "justify-end" : "justify-start"
                }`}
        >
            <div
                className={`max-w-[85%] md:max-w-[70%] rounded-2xl px-4 py-3 shadow-sm
          ${isUser
                        ? "bg-blue-600 text-white"
                        : "bg-white border"
                    }
        `}
            >
                <div className="flex flex-col gap-2">

                    <p className="whitespace-pre-wrap break-words">
                        {message.content}
                    </p>

                    {!isUser && (
                        <button
                            onClick={isSpeaking ? stopSpeaking : speakMessage}
                            className="self-end flex items-center gap-2 text-blue-600 hover:text-blue-800"
                        >
                            {isSpeaking ? (
                                <>
                                    <Square size={18} />
                                    <span className="text-sm">Stop</span>
                                </>
                            ) : (
                                <>
                                    <Volume2 size={18} />
                                    <span className="text-sm">Listen</span>
                                </>
                            )}
                        </button>
                    )}

                </div>
            </div>
        </div>
    );
}

export default Message;