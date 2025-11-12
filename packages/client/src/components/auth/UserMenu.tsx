import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../../store/slices/authSlice';
import { RootState } from '../../store';
import apiService from '../../services/api';

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
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
                    {user?.username?.[0]?.toUpperCase() || 'U'}
                </div>
                <div>
                    <div className="font-medium text-gray-900">{user?.username || 'User'}</div>
                    <div className="text-sm text-gray-500">{user?.email || ''}</div>
                </div>
            </div>
            <button
                onClick={handleLogout}
                className="px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            >
                Logout
            </button>
        </div>
    );
}
