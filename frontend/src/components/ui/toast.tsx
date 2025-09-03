'use client';

import * as React from 'react';
import { X } from 'lucide-react';
import { useToast, type Toast as ToastType } from '@/hooks/use-toast';

export function Toaster() {
  const { toasts, dismissToast } = useToast();

  if (toasts.length === 0) return null;

  const getToastStyles = (type: ToastType['type']) => {
    switch (type) {
      case 'error':
        return 'bg-red-500 text-white';
      case 'success':
        return 'bg-green-500 text-white';
      case 'warning':
        return 'bg-yellow-500 text-white';
      default:
        return 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700';
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`p-4 rounded-md shadow-lg min-w-[300px] flex items-start justify-between ${getToastStyles(toast.type)}`}
        >
          <div>
            {toast.title && (
              <div className="font-medium">{toast.title}</div>
            )}
            <div className="text-sm">{toast.message}</div>
          </div>
          <button
            onClick={() => dismissToast(toast.id)}
            className="ml-4 text-lg leading-none opacity-70 hover:opacity-100 transition-opacity"
            aria-label="Dismiss"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
}

export default Toaster;
