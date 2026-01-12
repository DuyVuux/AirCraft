import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

export type NotificationType = 'success' | 'error' | 'info' | 'warning';

export interface Notification {
    id: string;
    type: NotificationType;
    message: string;
    timestamp: number;
    read: boolean;
}

interface NotificationContextType {
    notifications: Notification[];
    unreadCount: number;
    addNotification: (type: NotificationType, message: string) => void;
    markAsRead: (id: string) => void;
    markAllAsRead: () => void;
    clearHistory: () => void;
    removeNotification: (id: string) => void;
}

const NotificationContext = createContext<NotificationContextType | null>(null);

export const useNotification = () => {
    const context = useContext(NotificationContext);
    if (!context) {
        throw new Error('useNotification must be used within a NotificationProvider');
    }
    return context;
};

export const NotificationProvider = ({ children }: { children: ReactNode }) => {
    const [notifications, setNotifications] = useState<Notification[]>([]);

    const addNotification = useCallback((type: NotificationType, message: string) => {
        const newNotification: Notification = {
            id: Math.random().toString(36).substring(2, 9),
            type,
            message,
            timestamp: Date.now(),
            read: false,
        };
        setNotifications((prev) => [newNotification, ...prev]);
    }, []);

    const markAsRead = useCallback((id: string) => {
        setNotifications((prev) =>
            prev.map((n) => (n.id === id ? { ...n, read: true } : n))
        );
    }, []);

    const markAllAsRead = useCallback(() => {
        setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    }, []);

    const clearHistory = useCallback(() => {
        setNotifications([]);
    }, []);

    const removeNotification = useCallback((id: string) => {
        setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, []);

    const unreadCount = notifications.filter((n) => !n.read).length;

    return (
        <NotificationContext.Provider
            value={{
                notifications,
                unreadCount,
                addNotification,
                markAsRead,
                markAllAsRead,
                clearHistory,
                removeNotification,
            }}
        >
            {children}
        </NotificationContext.Provider>
    );
};
