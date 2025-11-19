import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../../store/slices/authSlice';
import type { RootState } from '../../store';
import apiService from '../../services/api';
import ThemeToggle from '../ui/ThemeToggle';

export default function UserMenu() {
    const dispatch = useDispatch();
    const { user } = useSelector((state: RootState) => state.auth);

    const handleLogout = async () => {
        try {
            await apiService.logout();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            dispatch(logout());
            window.location.href = '/login';
        }
    };

    return (
        <header className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
            <div className="flex items-center gap-3">
                <img src="/logo.png" alt="InsightHub" className="h-10 w-10 object-contain" />
                <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                    InsightHub
                </h1>
            </div>
            <div className="flex items-center gap-4">
                <div className="text-right hidden sm:block">
                    <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {user?.username}
                    </div>
                    {user?.email && (
                        <div className="text-xs text-gray-500 dark:text-gray-400">{user.email}</div>
                    )}
                </div>
                <ThemeToggle />
                <button
                    onClick={handleLogout}
                    className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                    title="Logout"
                >
                    Logout
                </button>
            </div>
        </header>
    );
}
