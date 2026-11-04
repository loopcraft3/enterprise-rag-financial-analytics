import { Menu, Plus, Mic } from "lucide-react";

function Navbar({ onMenuClick, onNewChat, conversationMode, onToggleConversation }) {
    return (
        <header className="shrink-0 h-16 px-4 md:px-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
                <button
                    onClick={onMenuClick}
                    aria-label="Open documents"
                    className="md:hidden h-10 w-10 grid place-items-center rounded-full glass cursor-pointer"
                >
                    <Menu size={19} />
                </button>

                <div className="flex items-baseline gap-2">
                    <span className="font-display text-[28px] leading-none tracking-tight">
                        Hisaab
                    </span>
                    <span className="hidden sm:inline text-[13px] text-muted">
                        ask your financial documents
                    </span>
                </div>
            </div>

            <div className="flex items-center gap-2">
                <button
                    onClick={onToggleConversation}
                    className={`h-10 px-4 rounded-full text-sm font-medium flex items-center gap-2 cursor-pointer transition
                        ${conversationMode ? "bg-ink text-white" : "glass hover:bg-white"}`}
                >
                    <Mic size={16} />
                    <span className="hidden sm:inline">Voice chat</span>
                </button>

                <button
                    onClick={onNewChat}
                    className="h-10 px-4 rounded-full bg-ink text-white text-sm font-medium flex items-center gap-2 cursor-pointer hover:bg-black transition"
                >
                    <Plus size={16} />
                    <span className="hidden sm:inline">New chat</span>
                </button>
            </div>
        </header>
    );
}

export default Navbar;
