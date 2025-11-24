import { useDispatch } from 'react-redux';
import { logout as logoutAction } from '../store/slices/authSlice';
import type { AppDispatch } from '../store';

export const useAuth = () => {
    const dispatch = useDispatch<AppDispatch>();

    const logout = () => {
        dispatch(logoutAction());
    };

    return { logout };
};
