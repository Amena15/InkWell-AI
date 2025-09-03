'use client';

import { Gauge, BookOpen, CheckCircle, AlertTriangle, Code } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: number;
  max: number;
  icon: React.ReactNode;
  color: string;
}

function MetricCard({ title, value, max, icon, color }: MetricCardProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">{title}</h3>
        <div className={`p-2 rounded-full ${color} bg-opacity-10`}>
          {icon}
        </div>
      </div>
      <div className="mb-2 flex items-center justify-between">
        <span className="text-3xl font-bold text-gray-900 dark:text-white">
          {value}/{max}
        </span>
        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
          {Math.round(percentage)}%
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
        <div 
          className={`h-2.5 rounded-full ${color}`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
}

interface MetricsPanelProps {
  markdown: string;
}

export function MetricsPanel({ markdown }: MetricsPanelProps) {
  // Calculate metrics based on markdown content
  const calculateMetrics = (content: string) => {
    const words = content.split(/\s+/).filter(Boolean).length;
    const lines = content.split('\n').filter(Boolean).length;
    const headers = (content.match(/^#+\s/gm) || []).length;
    const codeBlocks = (content.match(/```[\s\S]*?```/g) || []).length;
    const hasDescription = content.length > 0 ? 1 : 0;
    
    return {
      coverage: Math.min(100, Math.floor((headers / 5) * 100)),
      complexity: Math.min(10, Math.floor(words / 50) + codeBlocks * 2),
      structure: Math.min(10, Math.floor(headers * 0.5 + lines * 0.05)),
      completeness: Math.min(10, Math.floor((hasDescription + headers * 0.5 + codeBlocks * 0.5) * 2)),
    };
  };

  const metrics = calculateMetrics(markdown);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Documentation Quality Metrics</h2>
        <p className="text-gray-600 dark:text-gray-300">
          Track the quality and completeness of your documentation in real-time.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Coverage"
          value={metrics.coverage}
          max={100}
          icon={<Gauge className="w-5 h-5 text-blue-500" />}
          color="bg-blue-500"
        />
        <MetricCard
          title="Complexity"
          value={metrics.complexity}
          max={10}
          icon={<Code className="w-5 h-5 text-purple-500" />}
          color="bg-purple-500"
        />
        <MetricCard
          title="Structure"
          value={metrics.structure}
          max={10}
          icon={<BookOpen className="w-5 h-5 text-green-500" />}
          color="bg-green-500"
        />
        <MetricCard
          title="Completeness"
          value={metrics.completeness}
          max={10}
          icon={metrics.completeness >= 7 ? 
            <CheckCircle className="w-5 h-5 text-emerald-500" /> : 
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
          }
          color={metrics.completeness >= 7 ? "bg-emerald-500" : "bg-yellow-500"}
        />
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Documentation Tips</h3>
        <ul className="space-y-3">
          {metrics.headers < 3 && (
            <li className="flex items-start">
              <AlertTriangle className="w-5 h-5 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
              <span className="text-gray-700 dark:text-gray-300">
                Add more section headers to improve document structure.
              </span>
            </li>
          )}
          {metrics.words < 100 && (
            <li className="flex items-start">
              <AlertTriangle className="w-5 h-5 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
              <span className="text-gray-700 dark:text-gray-300">
                Consider adding more descriptive content to your documentation.
              </span>
            </li>
          )}
          {metrics.codeBlocks === 0 && (
            <li className="flex items-start">
              <AlertTriangle className="w-5 h-5 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
              <span className="text-gray-700 dark:text-gray-300">
                Add code examples to make your documentation more practical.
              </span>
            </li>
          )}
          {metrics.coverage > 70 && (
            <li className="flex items-start">
              <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
              <span className="text-gray-700 dark:text-gray-300">
                Great job! Your documentation has good coverage.
              </span>
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}
