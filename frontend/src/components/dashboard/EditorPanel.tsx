'use client';

import { useState, useEffect } from 'react';
import { useDebounce } from '@/hooks/useDebounce';

interface EditorPanelProps {
  markdown: string;
  onChange: (markdown: string) => void;
}

export function EditorPanel({ markdown, onChange }: EditorPanelProps) {
  const [value, setValue] = useState(markdown);
  const debouncedValue = useDebounce(value, 500);

  useEffect(() => {
    if (debouncedValue !== markdown) {
      onChange(debouncedValue);
    }
  }, [debouncedValue, markdown, onChange]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
  };

  return (
    <div className="flex-1 flex flex-col h-full">
      <div className="border-b border-gray-200 dark:border-gray-700 p-4">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white">Editor</h2>
      </div>
      <div className="flex-1 overflow-auto">
        <textarea
          className="w-full h-full p-4 font-mono text-sm text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 border-0 focus:ring-0 resize-none"
          value={value}
          onChange={handleChange}
          placeholder="Start writing your markdown here..."
        />
      </div>
      <div className="border-t border-gray-200 dark:border-gray-700 p-2 text-xs text-gray-500 dark:text-gray-400">
        {value.length} characters • {value.split(/\s+/).filter(Boolean).length} words
      </div>
    </div>
  );
}
