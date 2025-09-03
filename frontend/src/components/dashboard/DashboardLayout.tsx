'use client';

import { useState } from 'react';
import { Sidebar } from './Sidebar';
import { EditorPanel } from './EditorPanel';
import { PreviewPanel } from './PreviewPanel';
import { MetricsPanel } from './MetricsPanel';

export function DashboardLayout() {
  const [markdown, setMarkdown] = useState('');
  const [activeTab, setActiveTab] = useState('editor');

  const handleMarkdownChange = (newMarkdown: string) => {
    setMarkdown(newMarkdown);
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      
      <main className="flex-1 flex flex-col">
        <div className="flex-1 flex overflow-hidden">
          {activeTab === 'editor' && (
            <div className="flex-1 flex">
              <EditorPanel 
                markdown={markdown} 
                onChange={handleMarkdownChange} 
              />
              <div className="w-px bg-gray-200 dark:bg-gray-700" />
              <PreviewPanel markdown={markdown} />
            </div>
          )}
          
          {activeTab === 'metrics' && (
            <div className="flex-1 p-6 overflow-auto">
              <MetricsPanel markdown={markdown} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
