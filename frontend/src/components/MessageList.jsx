import Message from "./Message";

function MessageList({ messages }) {
    return (
        <div className="flex flex-col gap-2">
            {messages.map((message, index) => (
                <Message
                    key={index}
                    message={message}
                />
            ))}
        </div>
    );
}

export default MessageList;