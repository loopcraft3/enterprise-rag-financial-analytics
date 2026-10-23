// import { useState, useRef } from "react";
// import { SendHorizontal, Mic } from "lucide-react";

// function MessageInput({ onSend, loading, conversationMode }) {
//     const [question, setQuestion] = useState("");
//     const [listening, setListening] = useState(false);


//     const recognitionRef = useRef(null);



//     const handleSubmit = () => {
//         const text = question.trim();

//         if (!text || loading) return;

//         onSend(text);
//         setQuestion("");
//     };

//     const handleKeyDown = (e) => {
//         if (e.key === "Enter" && !e.shiftKey) {
//             e.preventDefault();
//             handleSubmit();
//         }
//     };
//     const startListening = () => {

//         if (!recognitionRef.current) {

//             if (!("webkitSpeechRecognition" in window)) {
//                 alert("Speech Recognition is not supported.");
//                 return;
//             }

//             recognitionRef.current = new window.webkitSpeechRecognition();

//             recognitionRef.current.lang = "en-US";
//             recognitionRef.current.continuous = false;
//             recognitionRef.current.interimResults = false;

//             recognitionRef.current.onstart = () => {
//                 setListening(true);
//             };

//             recognitionRef.current.onresult = (event) => {

//                 const transcript =
//                     event.results[0][0].transcript;

//                 setQuestion(transcript);

//                 onSend(transcript, true);
//             };

//             recognitionRef.current.onend = () => {
//                 setListening(false);
//             };

//             recognitionRef.current.onerror = () => {
//                 setListening(false);
//             };
//         }

//         try {
//             recognitionRef.current.start();
//         } catch (e) { }
//     };

//     return (
//         <div className="border-t bg-white p-4">
//             <div className="max-w-4xl mx-auto flex items-end gap-3">
//                 <textarea
//                     value={question}
//                     onChange={(e) => setQuestion(e.target.value)}
//                     onKeyDown={handleKeyDown}
//                     placeholder="Upload and Ask questions about your documents only!..."
//                     rows={1}
//                     disabled={loading}
//                     className="flex-1 resize-none rounded-xl border p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
//                 />

//                 <button
//                     onClick={startListening}
//                     disabled={loading || listening}
//                     className={`h-12 w-12 rounded-xl flex items-center justify-center text-white transition ${listening
//                         ? "bg-red-600"
//                         : "bg-green-600 hover:bg-green-700"
//                         }`}
//                 >
//                     <Mic size={20} />
//                 </button>

//                 <button
//                     onClick={handleSubmit}
//                     disabled={loading || !question.trim()}
//                     className="h-12 w-12 rounded-xl bg-blue-600 text-white flex items-center justify-center hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
//                 >
//                     <SendHorizontal size={20} />
//                 </button>

//             </div>
//         </div>
//     );
// }

// export default MessageInput;


import { useState } from "react";
import { SendHorizontal, Mic } from "lucide-react";

function MessageInput({ onSend, loading, listening, onMicClick }) {
    const [question, setQuestion] = useState("");





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


    return (
        <div className=" bg-white p-4">
            <div className="text-sm display flex ml-30 text-neutral-400 top-0.5">
                Custom RAG Assistant can make mistakes. Check important info.
            </div>
            <div className="max-w-4xl mx-auto flex items-end gap-3">
                <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Upload and Ask questions about your documents only!..."
                    rows={1}
                    disabled={loading}
                    className="flex-1 resize-none rounded-xl border p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />


                <button
                    onClick={onMicClick}
                    disabled={loading}
                    className={`h-12 w-12 rounded-xl flex items-center justify-center text-white transition ${listening
                        ? "bg-red-600"
                        : "bg-green-600 hover:bg-green-700"
                        }`}
                >
                    <Mic size={20} />
                </button>


                <button
                    onClick={handleSubmit}
                    disabled={loading || !question.trim()}
                    className="h-12 w-12 rounded-xl bg-blue-600 text-white flex items-center justify-center hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
                >
                    <SendHorizontal size={20} />
                </button>


            </div>

        </div>
    );
}

export default MessageInput;