import ChatBot from './components/chat/ChatBot';
import ChatSidebar from './components/chat/ChatSidebar';

function App() {
    return (
        <div className="h-screen flex">
            {/* Left Sidebar - Chat History */}
            <ChatSidebar />

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col overflow-hidden">
                <ChatBot />
            </div>
        </div>
    );
}

export default App;
