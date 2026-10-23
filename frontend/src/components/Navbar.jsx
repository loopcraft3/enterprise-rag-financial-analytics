import { Menu } from "lucide-react";

function Navbar({ onMenuClick }) {
    return (
        <header className="h-16 border-b bg-white flex items-center justify-between px-4 md:px-6 shadow-sm">
            <div className="flex items-center gap-3">
                <button
                    onClick={onMenuClick}
                    className="md:hidden p-2 rounded-lg hover:bg-gray-100"
                >
                    <Menu size={22} />
                </button>

                <h1 className="text-lg md:text-2xl font-bold">
                    Custom RAG Assistant
                    <span className="text-sm text-neutral-500"> version=5.2.3</span>
                </h1>
            </div>

            <p className="hidden sm:block text-sm text-gray-500">
                AI Powered PDF Chat
            </p>
        </header>
    ); 
}

export default Navbar;