import { motion } from "framer-motion";
import Message from "./Message";

function MessageList({ messages, lastRef }) {
    return (
        <div className="flex flex-col gap-8">
            {messages.map((message, index) => {
                const isLast = index === messages.length - 1;
                return (
                    <motion.div
                        key={index}
                        ref={isLast ? lastRef : null}
                        initial={{ opacity: 0, y: 14 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                        className="scroll-mt-4"
                    >
                        <Message message={message} />
                    </motion.div>
                );
            })}
        </div>
    );
}

export default MessageList;
