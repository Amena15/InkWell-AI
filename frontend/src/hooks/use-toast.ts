'use client';

import * as React from 'react';

export type ToastType = 'default' | 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  title: string;
  message: string;
  type: ToastType;
  duration?: number;
}

type ToastOptions = Omit<Toast, 'id'>;

type ToastContextType = {
  toasts: Toast[];
  toast: (options: ToastOptions) => string;
  dismissToast: (id: string) => void;
};

const ToastContext = React.createContext<ToastContextType | undefined>(undefined);

interface ToastProviderProps {
  children: React.ReactNode;
}

type TimeoutMap = Record<string, NodeJS.Timeout>;

export function ToastProvider({ children }: ToastProviderProps) {
  const [toasts, setToasts] = React.useState<Toast[]>([]);
  const timeoutsRef = React.useRef<TimeoutMap>({});

  const toast = React.useCallback((options: ToastOptions) => {
    const id = Math.random().toString(36).substring(2, 9);
    const { title, message, type, duration = 5000 } = options;
    
    setToasts(prevToasts => [
      ...prevToasts,
      { id, title, message, type, duration },
    ]);

    if (duration > 0) {
      if (timeoutsRef.current[id]) {
        clearTimeout(timeoutsRef.current[id]);
      }
      
      timeoutsRef.current[id] = setTimeout(() => {
        setToasts(prevToasts => prevToasts.filter(t => t.id !== id));
        delete timeoutsRef.current[id];
      }, duration);
    }

    return id;
  }, []);

  const dismissToast = React.useCallback((id: string) => {
    setToasts(prevToasts => {
      const newToasts = prevToasts.filter(t => t.id !== id);
      if (newToasts.length !== prevToasts.length && timeoutsRef.current[id]) {
        clearTimeout(timeoutsRef.current[id]);
        delete timeoutsRef.current[id];
      }
      return newToasts;
    });
  }, []);

  const value = React.useMemo(() => ({
    toasts,
    toast,
    dismissToast,
  }), [toasts, toast, dismissToast]);

  return React.createElement(
    ToastContext.Provider,
    { value },
    children
  );
}

export function useToast() {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}
