export const DOCUMENTATION_CONFIG = {
  // Code analysis settings
  analysis: {
    // File extensions to analyze
    fileExtensions: ['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.go', '.rb'],
    
    // Ignore patterns (e.g., node_modules, build directories)
    ignorePatterns: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/.next/**',
      '**/out/**',
      '**/*.d.ts',
      '**/*.min.js',
      '**/*.bundle.js',
    ],
    
    // Minimum documentation quality score (0-1)
    minQualityScore: 0.7,
  },
  
  // Documentation rules
  rules: {
    requireFunctionDocs: true,
    requireParamDocs: true,
    requireReturnDocs: true,
    requireTypeInfo: true,
    requireExamples: false,
    requireDescriptions: true,
    
    // Documentation style preferences
    style: {
      preferJSDoc: true,
      preferTypeScript: true,
      requireParamTypes: true,
      requireReturnTypes: true,
    },
    
    // Severity levels for different types of issues
    severity: {
      missingDocumentation: 'warning',
      incompleteDocumentation: 'warning',
      incorrectDocumentation: 'error',
      deprecatedUsage: 'error',
      todoComments: 'info',
    },
  },
  
  // Language-specific settings
  languages: {
    javascript: {
      // JavaScript-specific settings
      requireTypeInfo: false,
    },
    typescript: {
      // TypeScript-specific settings
      requireTypeInfo: true,
    },
    python: {
      // Python-specific settings
      requireTypeInfo: false,
      docstringStyle: 'google', // 'google', 'numpy', or 'sphinx'
    },
  },
  
  // Notification settings
  notifications: {
    enabled: true,
    realtimeMonitoring: true,
    desktopNotifications: false,
    emailNotifications: false,
    
    // Notification thresholds
    thresholds: {
      warning: 5,    // Number of warnings before notification
      error: 1,      // Number of errors before notification
      critical: 1,   // Number of critical issues before notification
    },
    
    // Notification channels
    channels: {
      inApp: true,
      email: false,
      slack: false,
      webhook: false,
    },
  },
  
  // Integration settings
  integrations: {
    versionControl: {
      github: false,
      gitlab: false,
      bitbucket: false,
    },
    ciCd: {
      githubActions: false,
      gitlabCI: false,
      jenkins: false,
    },
    documentation: {
      readthedocs: false,
      docusaurus: false,
      gitbook: false,
    },
  },
  
  // Auto-fix settings
  autoFix: {
    enabled: false,
    safeChangesOnly: true,
    backupBeforeFix: true,
    
    // What types of issues can be auto-fixed
    fixableIssues: [
      'missing-param-tag',
      'missing-return-tag',
      'missing-description',
      'missing-type',
    ],
  },
  
  // Cache settings
  cache: {
    enabled: true,
    ttl: 3600, // 1 hour in seconds
    directory: '.documentation-cache',
  },
  
  // Logging settings
  logging: {
    level: 'info', // 'error', 'warn', 'info', 'debug', 'trace'
    format: 'text', // 'text' or 'json'
    file: 'documentation-issues.log',
    maxSize: '10MB',
    maxFiles: 5,
  },
} as const;

export type DocumentationConfig = typeof DOCUMENTATION_CONFIG;
export type SeverityLevel = 'error' | 'warning' | 'info' | 'off';
export type LanguageId = keyof typeof DOCUMENTATION_CONFIG.languages;
