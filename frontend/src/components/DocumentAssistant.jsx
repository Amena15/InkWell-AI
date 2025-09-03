import React, { useState, useRef, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  FiUpload, 
  FiCode, 
  FiFileText, 
  FiCheckCircle, 
  FiAlertTriangle, 
  FiInfo,
  FiEye,
  FiEdit2,
  FiSave,
  FiDownload,
  FiRefreshCw,
  FiX,
  FiMaximize2,
  FiMinimize2
} from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'prism-react-renderer';
import { vs, vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { checkGrammar, getIssueMessage } from '../services/grammarService';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  CircularProgress, 
  Divider, 
  FormControl, 
  Grid, 
  IconButton, 
  InputLabel, 
  MenuItem, 
  Paper, 
  Select, 
  Snackbar, 
  Tab, 
  Tabs, 
  TextField, 
  Tooltip, 
  Typography, 
  useTheme,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  ToggleButtonGroup,
  ToggleButton,
  AppBar,
  Toolbar,
  useMediaQuery,
  CssBaseline,
  ThemeProvider,
  createTheme,
  alpha
} from '@mui/material';
import { ExpandLess, ExpandMore } from '@mui/icons-material';

// Custom theme for the markdown editor
const editorTheme = (mode) => createTheme({
  palette: {
    mode,
    ...(mode === 'light' ? {
      background: {
        default: '#f5f5f5',
        paper: '#ffffff',
      },
    } : {
      background: {
        default: '#121212',
        paper: '#1e1e1e',
      },
    }),
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 20px 0 rgba(0,0,0,0.1)',
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            boxShadow: '0 8px 30px 0 rgba(0,0,0,0.15)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
          padding: '8px 16px',
        },
      },
    },
  },
});

const DocumentAssistant = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [mode, setMode] = useState('light');
  const [previewMode, setPreviewMode] = useState('edit'); // 'edit', 'preview', 'split'
  const [fullscreen, setFullscreen] = useState(false);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [documentName, setDocumentName] = useState('untitled');
  const [documentType, setDocumentType] = useState('md');
  const editorRef = useRef(null);
  const previewRef = useRef(null);
  
  // Sync scroll between editor and preview in split view
  useEffect(() => {
    if (previewMode === 'split' && editorRef.current && previewRef.current) {
      const editor = editorRef.current;
      const preview = previewRef.current.querySelector('.markdown-body');
      
      if (!editor || !preview) return;
      
      const syncScroll = (source, target) => {
        if (!target) return;
        const percentage = source.scrollTop / (source.scrollHeight - source.clientHeight);
        target.scrollTop = (target.scrollHeight - target.clientHeight) * percentage;
      };
      
      const handleEditorScroll = () => syncScroll(editor, preview);
      const handlePreviewScroll = () => syncScroll(preview, editor);
      
      editor.addEventListener('scroll', handleEditorScroll);
      preview.addEventListener('scroll', handlePreviewScroll);
      
      return () => {
        editor.removeEventListener('scroll', handleEditorScroll);
        preview.removeEventListener('scroll', handlePreviewScroll);
      };
    }
  }, [previewMode]);
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Toggle preview mode with Ctrl+E (Cmd+E on Mac)
      if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        setPreviewMode(prev => {
          if (prev === 'edit') return 'preview';
          if (prev === 'preview') return 'split';
          return 'edit';
        });
      }
      // Save with Ctrl+S (Cmd+S on Mac)
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleSaveDocument();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
  
  const handleSaveDocument = () => {
    // TODO: Implement save functionality
    setSaveDialogOpen(true);
  };
  
  const handleExportDocument = (format) => {
    // TODO: Implement export functionality
    console.log(`Exporting as ${format}`);
  };
  
  const toggleFullscreen = () => {
    setFullscreen(!fullscreen);
  };
  
  const [file, setFile] = useState(null);
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [isLoading, setIsLoading] = useState(false);
  const [isCheckingGrammar, setIsCheckingGrammar] = useState(false);
  const [result, setResult] = useState(null);
  const [grammarIssues, setGrammarIssues] = useState([]);
  const [expandedIssue, setExpandedIssue] = useState(null);
  const [activeTab, setActiveTab] = useState('file');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  
  // Editor content
  const [markdown, setMarkdown] = useState(
    '# Welcome to InkWell AI\n\nStart writing your documentation here...\n\n## Features\n- Real-time markdown preview\n- Syntax highlighting\n- Document analysis\n- Export to multiple formats\n\n```python\ndef hello_world():\n    print(\"Hello, World!\")\n```'
  );
  
  // Handle file upload
  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setMarkdown(e.target.result);
        setSnackbar({
          open: true,
          message: `Loaded ${file.name}`,
          severity: 'success'
        });
      };
      reader.readAsText(file);
    }
  };
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/markdown': ['.md', '.markdown'],
      'text/plain': ['.txt'],
      'text/x-python': ['.py'],
      'application/javascript': ['.js', '.jsx'],
      'application/typescript': ['.ts', '.tsx']
    },
    maxFiles: 1
  });
  
  // Handle grammar check
  const handleCheckGrammar = async () => {
    if (!markdown.trim()) {
      setSnackbar({
        open: true,
        message: 'Please enter some text to check',
        severity: 'warning'
      });
      return;
    }
    
    setIsCheckingGrammar(true);
    try {
      const issues = await checkGrammar(markdown);
      setGrammarIssues(issues);
      setSnackbar({
        open: true,
        message: `Found ${issues.length} ${issues.length === 1 ? 'issue' : 'issues'}`,
        severity: issues.length > 0 ? 'warning' : 'success'
      });
    } catch (error) {
      console.error('Error checking grammar:', error);
      setSnackbar({
        open: true,
        message: 'Failed to check grammar. Please try again.',
        severity: 'error'
      });
    } finally {
      setIsCheckingGrammar(false);
    }
  };
  
  // Apply grammar suggestion
  const applySuggestion = (issue, suggestion) => {
    const lines = markdown.split('\n');
    const line = lines[issue.line - 1];
    const newLine = line.substring(0, issue.offset) + suggestion + line.substring(issue.offset + issue.length);
    const newMarkdown = [...lines];
    newMarkdown[issue.line - 1] = newLine;
    setMarkdown(newMarkdown.join('\n'));
    
    // Remove the fixed issue
    setGrammarIssues(prev => prev.filter(i => i !== issue));
  };
  
  // Toggle issue expansion
  const toggleExpandIssue = (index) => {
    setExpandedIssue(expandedIssue === index ? null : index);
  };
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  // Main render function
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      let response;
      const formData = new FormData();
      
      if (activeTab === 'file' && file) {
        formData.append('file', file);
        response = await fetch('/api/document/upload', {
          method: 'POST',
          body: formData,
        });
      } else if (activeTab === 'code' && code.trim()) {
        response = await fetch('/api/document/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            code,
            language,
          }),
        });
      } else {
        throw new Error(activeTab === 'file' ? 'Please select a file' : 'Please enter some code');
      }
      
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to process document');
      
      setResult(data.data);
    } catch (error) {
      console.error('Error:', error);
      alert(error.message || 'An error occurred while processing the document');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold text-center mb-8 text-indigo-700">
        Smart Documentation Assistant
      </h1>
      
      <div className="mb-6">
        <div className="flex border-b">
          <button
            className={`py-2 px-4 font-medium ${activeTab === 'file' ? 'border-b-2 border-indigo-600 text-indigo-700' : 'text-gray-500'}`}
            onClick={() => setActiveTab('file')}
          >
            <FiFileText className="inline mr-2" />
            Upload File
          </button>
          <button
            className={`py-2 px-4 font-medium ${activeTab === 'code' ? 'border-b-2 border-indigo-600 text-indigo-700' : 'text-gray-500'}`}
            onClick={() => setActiveTab('code')}
          >
            <FiCode className="inline mr-2" />
            Code Snippet
          </button>
        </div>
        
        <div className="mt-6">
          {activeTab === 'file' ? (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
                isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400'
              }`}
            >
              <input {...getInputProps()} />
              <FiUpload className="mx-auto text-4xl text-gray-400 mb-4" />
              <p className="text-lg text-gray-600">
                {isDragActive
                  ? 'Drop the file here'
                  : file
                  ? file.name
                  : 'Drag & drop a file here, or click to select'}
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Supported formats: .md, .txt, .py, .js, .ts, .html, .css, .json
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label htmlFor="language" className="block text-sm font-medium text-gray-700 mb-1">
                  Language
                </label>
                <select
                  id="language"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full p-2 border rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="html">HTML</option>
                  <option value="css">CSS</option>
                </select>
              </div>
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Paste your code here..."
                rows={10}
                className="w-full p-3 border rounded-md font-mono text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-center">
        <button
          onClick={handleCheckGrammar}
          disabled={isCheckingGrammar || (activeTab === 'file' && !file) || (activeTab === 'code' && !code.trim())}
          className={`px-6 py-3 rounded-full text-white font-medium ${
            isCheckingGrammar || (activeTab === 'file' && !file) || (activeTab === 'code' && !code.trim())
              ? 'bg-indigo-300 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700'
          } transition-colors`}
        >
          {isCheckingGrammar ? 'Checking...' : 'Check Grammar'}
        </button>
        <button
          onClick={handleSubmit}
          disabled={isLoading || (activeTab === 'file' && !file) || (activeTab === 'code' && !code.trim())}
          className={`px-6 py-3 rounded-full text-white font-medium ${
            isLoading || (activeTab === 'file' && !file) || (activeTab === 'code' && !code.trim())
              ? 'bg-indigo-300 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700'
          } transition-colors`}
        >
          {isLoading ? 'Processing...' : 'Generate Documentation'}
        </button>
      </div>

      {grammarIssues.length > 0 && renderGrammarIssues()}

      {result && (
        <div className="mt-8 p-6 bg-gray-50 rounded-lg">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Generated Documentation</h2>
          <div className="prose max-w-none">
            <h3 className="text-lg font-medium text-gray-700 mb-2">File: {result.file_path}</h3>
            <div className="bg-white p-4 rounded border border-gray-200">
              <pre className="whitespace-pre-wrap text-sm text-gray-800">
                {result.documentation}
              </pre>
            </div>
            <div className="mt-4 text-sm text-gray-600">
              <p>Language: {result.metadata.language}</p>
              <p>Size: {result.metadata.size} characters</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
