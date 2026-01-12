import React, { useState } from 'react';
import {
    Fab,
    Badge,
    Popover,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Typography,
    IconButton,
    Box,
    Divider,
    Button
} from '@mui/material';
import {
    Notifications as NotificationsIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    Info as InfoIcon,
    Warning as WarningIcon,
    Close as CloseIcon,
    DoneAll as DoneAllIcon,
    DeleteSweep as DeleteSweepIcon
} from '@mui/icons-material';
import { useNotification, NotificationType } from '../../contexts/NotificationContext';
import { format } from 'date-fns';

const TYPE_ICONS: Record<NotificationType, React.ReactElement> = {
    success: <CheckCircleIcon color="success" />,
    error: <ErrorIcon color="error" />,
    info: <InfoIcon color="info" />,
    warning: <WarningIcon color="warning" />
};

export default function NotificationHistory() {
    const { notifications, unreadCount, markAllAsRead, clearHistory } = useNotification();
    const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);

    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
        // Optional: Mark all as read when closing
        // markAllAsRead(); 
    };

    const handleMarkAllRead = () => {
        markAllAsRead();
    };

    const handleClearHistory = () => {
        if (window.confirm('Xóa toàn bộ lịch sử thông báo?')) {
            clearHistory();
        }
    };

    const open = Boolean(anchorEl);
    const id = open ? 'notification-popover' : undefined;

    return (
        <>
            <Fab
                color="primary"
                aria-label="notifications"
                onClick={handleClick}
                sx={{
                    position: 'fixed',
                    bottom: 24,
                    right: 24,
                    zIndex: 1000
                }}
            >
                <Badge badgeContent={unreadCount} color="error">
                    <NotificationsIcon />
                </Badge>
            </Fab>

            <Popover
                id={id}
                open={open}
                anchorEl={anchorEl}
                onClose={handleClose}
                anchorOrigin={{
                    vertical: 'top',
                    horizontal: 'right',
                }}
                transformOrigin={{
                    vertical: 'bottom',
                    horizontal: 'right',
                }}
                PaperProps={{
                    sx: { width: 360, maxHeight: 500, display: 'flex', flexDirection: 'column' }
                }}
            >
                <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #eee' }}>
                    <Typography variant="h6">Thông báo</Typography>
                    <Box>
                        <IconButton size="small" title="Đánh dấu đã đọc" onClick={handleMarkAllRead} disabled={unreadCount === 0}>
                            <DoneAllIcon fontSize="small" />
                        </IconButton>
                        <IconButton size="small" title="Xóa lịch sử" onClick={handleClearHistory} disabled={notifications.length === 0}>
                            <DeleteSweepIcon fontSize="small" />
                        </IconButton>
                        <IconButton size="small" onClick={handleClose}>
                            <CloseIcon fontSize="small" />
                        </IconButton>
                    </Box>
                </Box>

                <List sx={{ flexGrow: 1, overflow: 'auto', p: 0 }}>
                    {notifications.length === 0 ? (
                        <Box sx={{ p: 4, textAlign: 'center', color: 'text.secondary' }}>
                            <Typography>Không có thông báo nào</Typography>
                        </Box>
                    ) : (
                        notifications.map((notification) => (
                            <React.Fragment key={notification.id}>
                                <ListItem
                                    alignItems="flex-start"
                                    sx={{
                                        bgcolor: notification.read ? 'transparent' : 'action.hover',
                                        transition: 'background-color 0.3s'
                                    }}
                                >
                                    <ListItemIcon sx={{ minWidth: 40, mt: 0.5 }}>
                                        {TYPE_ICONS[notification.type]}
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={notification.message}
                                        secondary={
                                            <Typography variant="caption" color="text.secondary">
                                                {format(notification.timestamp, 'HH:mm:ss dd/MM/yyyy')}
                                            </Typography>
                                        }
                                        primaryTypographyProps={{
                                            variant: 'body2',
                                            fontWeight: notification.read ? 'normal' : 'bold'
                                        }}
                                    />
                                </ListItem>
                                <Divider component="li" />
                            </React.Fragment>
                        ))
                    )}
                </List>
            </Popover>
        </>
    );
}
