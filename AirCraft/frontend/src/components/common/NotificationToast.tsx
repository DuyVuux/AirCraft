import React, { useEffect, useState, useRef } from 'react';
import { Alert, Box, Collapse, IconButton } from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { useNotification, Notification } from '../../contexts/NotificationContext';
import { TransitionGroup } from 'react-transition-group';

export default function NotificationToast() {
    const { notifications } = useNotification();
    const [toasts, setToasts] = useState<Notification[]>([]);
    const lastLatestIdRef = useRef<string | null>(null);

    useEffect(() => {
        if (notifications.length === 0) return;

        const latestId = notifications[0].id;
        if (latestId === lastLatestIdRef.current) return;

        // Find all new notifications since last check
        const newItems: Notification[] = [];
        for (const n of notifications) {
            if (n.id === lastLatestIdRef.current) break;
            // Also check timestamp to avoid showing stale ones on reload
            if (Date.now() - n.timestamp > 2000) break;
            newItems.push(n);
        }

        if (newItems.length > 0) {
            setToasts(prev => {
                // Add new items to the end (bottom)
                const combined = [...prev, ...newItems.reverse()];
                // Keep max 5 items
                if (combined.length > 5) {
                    return combined.slice(combined.length - 5);
                }
                return combined;
            });
            lastLatestIdRef.current = latestId;
        }
    }, [notifications]);

    const removeToast = (id: string) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    };

    return (
        <Box
            sx={{
                position: 'fixed',
                bottom: 90,
                right: 24,
                zIndex: 2000,
                display: 'flex',
                flexDirection: 'column',
                gap: 1,
                maxWidth: 400,
                width: '100%',
                pointerEvents: 'none', // Allow clicking through empty space
            }}
        >
            <TransitionGroup>
                {toasts.map(toast => (
                    <Collapse key={toast.id}>
                        <ToastItem notification={toast} onDismiss={() => removeToast(toast.id)} />
                    </Collapse>
                ))}
            </TransitionGroup>
        </Box>
    );
}

function ToastItem({ notification, onDismiss }: { notification: Notification, onDismiss: () => void }) {
    useEffect(() => {
        const timer = setTimeout(onDismiss, 4000);
        return () => clearTimeout(timer);
    }, [onDismiss]);

    return (
        <Alert
            severity={notification.type}
            variant="filled"
            action={
                <IconButton
                    aria-label="close"
                    color="inherit"
                    size="small"
                    onClick={onDismiss}
                >
                    <CloseIcon fontSize="inherit" />
                </IconButton>
            }
            sx={{
                width: '100%',
                boxShadow: 3,
                pointerEvents: 'auto', // Re-enable clicks
                mb: 1 // Margin bottom for spacing
            }}
        >
            {notification.message}
        </Alert>
    );
}
