import React from 'react';
import NotificationToast from './NotificationToast';
import NotificationHistory from './NotificationHistory';

export default function NotificationContainer() {
    return (
        <>
            <NotificationToast />
            <NotificationHistory />
        </>
    );
}
