import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Volume2, Square } from "lucide-react";

function Message({ message }) {
    const isUser = message.role === "user";

    const [isSpeaking, setIsSpeaking] = useState(false);

    const speakMessage = () => {
        speechSynthesis.cancel();

        // strip markdown symbols so they aren't read aloud
        const spokenText = message.content.replace(/[*_`#>|]/g, "");
        const utterance = new SpeechSynthesisUtterance(spokenText);

        utterance.lang = "en-US";
        utterance.rate = 1;
        utterance.pitch = 1;
        utterance.volume = 1;

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
        <div className={`flex mb-6 ${isUser ? "justify-end" : "justify-start"}`}>
            <div
                className={`max-w-[85%] md:max-w-[70%] rounded-2xl px-4 py-3 shadow-sm
          ${isUser ? "bg-blue-600 text-white" : "bg-white border"}
        `}
            >
                <div className="flex flex-col gap-2">
                    {isUser ? (
                        <p className="whitespace-pre-wrap break-words">
                            {message.content}
                        </p>
                    ) : (
                        <div
                            className="break-words
                [&_p]:mb-2 [&_p:last-child]:mb-0
                [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:list-decimal [&_ol]:pl-5
                [&_strong]:font-semibold
                [&_table]:border-collapse [&_th]:border [&_th]:px-2 [&_th]:py-1
                [&_td]:border [&_td]:px-2 [&_td]:py-1"
                        >
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {message.content}
                            </ReactMarkdown>
                        </div>
                    )}

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