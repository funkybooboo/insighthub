import ChatBot from './components/chat/ChatBot';

function App() {
    return (
        <div className="h-screen flex flex-col">
            <div className="flex-1 overflow-auto">
                <ChatBot />
            </div>
        </div>
    );
}

export default App;
