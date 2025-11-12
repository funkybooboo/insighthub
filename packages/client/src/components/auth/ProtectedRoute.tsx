import { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

interface ProtectedRouteProps {
    children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
    const { isAuthenticated, token } = useSelector((state: RootState) => state.auth);

    useEffect(() => {
        if (!isAuthenticated || !token) {
            window.location.href = '/login';
        }
    }, [isAuthenticated, token]);

    if (!isAuthenticated || !token) {
        return null;
    }

    return <>{children}</>;
}
