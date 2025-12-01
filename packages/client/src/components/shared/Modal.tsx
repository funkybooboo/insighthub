import React from 'react';
import { FaTimes } from 'react-icons/fa';

interface ModalProps {
    show: boolean;
    onClose: () => void;
    title: string;
    children: React.ReactNode;
    footer?: React.ReactNode;
    topRight?: React.ReactNode;
}

const Modal: React.FC<ModalProps> = ({ show, onClose, title, children, footer, topRight }) => {
    if (!show) {
        return null;
    }

    return (
        <div className="fixed inset-0 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-6xl mx-4 max-h-[90vh] flex flex-col">

                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                        {title}
                    </h2>

                    {/* Right side: unsaved indicator + close */}
                    <div className="flex items-center space-x-3">
                        {topRight && <div>{topRight}</div>}

                        <button
                            onClick={onClose}
                            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                        >
                            <FaTimes className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="overflow-y-auto flex-grow">
                    {children}
                </div>

                {/* Footer */}
                {footer && <div className="mt-6">{footer}</div>}
            </div>
        </div>
    );
};

export default Modal;
