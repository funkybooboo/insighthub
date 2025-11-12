import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { useSelector } from 'react-redux';
import LoginForm from './components/auth/LoginForm';
import SignupForm from './components/auth/SignupForm';
import ProtectedRoute from './components/auth/ProtectedRoute';
import ChatBot from './components/chat/ChatBot';
import ChatSidebar from './components/chat/ChatSidebar';
import type { RootState } from './store';

import UserMenu from './components/auth/UserMenu';

function MainApp() {
    return (
        <div className="h-screen flex flex-col">
            <UserMenu />
            <div className="flex-1 flex overflow-hidden">
                <ChatSidebar />
                <div className="flex-1 flex flex-col overflow-hidden">
                    <ChatBot />
                </div>
            </div>
        </div>
    );
}

function App() {
    const { isAuthenticated } = useSelector((state: RootState) => state.auth);

    return (
        <BrowserRouter>
            <Routes>
                <Route
                    path="/login"
                    element={isAuthenticated ? <Navigate to="/" replace /> : <LoginForm />}
                />
                <Route
                    path="/signup"
                    element={isAuthenticated ? <Navigate to="/" replace /> : <SignupForm />}
                />
                <Route
                    path="/"
                    element={
                        <ProtectedRoute>
                            <MainApp />
                        </ProtectedRoute>
                    }
                />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
