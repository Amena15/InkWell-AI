'use client';

import { useToast } from './use-toast';

export function Toaster() {
  const { toasts, dismissToast } = useToast();

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`p-4 rounded-md shadow-lg min-w-[300px] ${
            toast.type === 'error'
              ? 'bg-red-500 text-white'
              : toast.type === 'success'
              ? 'bg-green-500 text-white'
              : toast.type === 'warning'
              ? 'bg-yellow-500 text-white'
              : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'
          }`}
        >
          <div className="flex justify-between items-start">
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
              &times;
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
