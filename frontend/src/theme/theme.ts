import { createTheme } from '@mui/material/styles';

// Color palette
const colors = {
  primary: {
    main: '#6366F1', // Indigo-500
    light: '#818CF8', // Indigo-400
    dark: '#4F46E5', // Indigo-600
    contrastText: '#FFFFFF',
  },
  secondary: {
    main: '#10B981', // Emerald-500
    light: '#34D399', // Emerald-400
    dark: '#059669', // Emerald-600
    contrastText: '#FFFFFF',
  },
  error: {
    main: '#EF4444', // Red-500
    light: '#F87171', // Red-400
    dark: '#DC2626', // Red-600
  },
  warning: {
    main: '#F59E0B', // Amber-500
    light: '#FBBF24', // Amber-400
    dark: '#D97706', // Amber-600
  },
  info: {
    main: '#3B82F6', // Blue-500
    light: '#60A5FA', // Blue-400
    dark: '#2563EB', // Blue-600
  },
  success: {
    main: '#10B981', // Green-500
    light: '#34D399', // Green-400
    dark: '#059669', // Green-600
  },
  background: {
    default: '#F9FAFB', // Gray-50
    paper: '#FFFFFF',
  },
  text: {
    primary: '#111827', // Gray-900
    secondary: '#4B5563', // Gray-600
    disabled: '#9CA3AF', // Gray-400
  },
  divider: '#E5E7EB', // Gray-200
};

// Typography
const typography = {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  h1: {
    fontSize: '2.5rem',
    fontWeight: 700,
    lineHeight: 1.2,
  },
  h2: {
    fontSize: '2rem',
    fontWeight: 600,
    lineHeight: 1.3,
  },
  h3: {
    fontSize: '1.75rem',
    fontWeight: 600,
    lineHeight: 1.3,
  },
  h4: {
    fontSize: '1.5rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h5: {
    fontSize: '1.25rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h6: {
    fontSize: '1.125rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  subtitle1: {
    fontSize: '1rem',
    fontWeight: 500,
    lineHeight: 1.5,
  },
  subtitle2: {
    fontSize: '0.875rem',
    fontWeight: 500,
    lineHeight: 1.5,
  },
  body1: {
    fontSize: '1rem',
    lineHeight: 1.6,
  },
  body2: {
    fontSize: '0.875rem',
    lineHeight: 1.6,
  },
  button: {
    textTransform: 'none',
    fontWeight: 500,
  },
  caption: {
    fontSize: '0.75rem',
    lineHeight: 1.5,
  },
  overline: {
    fontSize: '0.75rem',
    fontWeight: 600,
    lineHeight: 1.5,
    textTransform: 'uppercase',
  },
};

// Component overrides
const components = {
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        padding: '8px 16px',
        boxShadow: 'none',
        '&:hover': {
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
      },
      contained: {
        '&:hover': {
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
      },
      outlined: {
        borderWidth: '1.5px',
        '&:hover': {
          borderWidth: '1.5px',
        },
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 12,
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        '&:hover': {
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
      },
    },
  },
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: 8,
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: colors.primary.light,
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderWidth: '1.5px',
            borderColor: colors.primary.main,
          },
        },
      },
    },
  },
  MuiAppBar: {
    styleOverrides: {
      root: {
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
      },
    },
  },
  MuiDrawer: {
    styleOverrides: {
      paper: {
        borderRight: 'none',
        boxShadow: '1px 0 3px 0 rgba(0, 0, 0, 0.1)',
      },
    },
  },
  MuiListItemButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        margin: '4px 8px',
        '&.Mui-selected': {
          backgroundColor: 'rgba(99, 102, 241, 0.1)',
          '&:hover': {
            backgroundColor: 'rgba(99, 102, 241, 0.15)',
          },
        },
      },
    },
  },
};

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    ...colors,
  },
  typography,
  components,
  shape: {
    borderRadius: 8,
  },
  spacing: 4, // 4px
});

// Dark theme overrides
const darkTheme = createTheme({
  ...theme,
  palette: {
    mode: 'dark',
    primary: {
      ...colors.primary,
      main: colors.primary.light,
    },
    background: {
      default: '#111827', // Gray-900
      paper: '#1F2937', // Gray-800
    },
    text: {
      primary: '#F9FAFB', // Gray-50
      secondary: '#E5E7EB', // Gray-200
      disabled: '#9CA3AF', // Gray-400
    },
    divider: '#374151', // Gray-700
  },
  components: {
    ...components,
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1F2937', // Gray-800
          color: '#F9FAFB', // Gray-50
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#1F2937', // Gray-800
          color: '#F9FAFB', // Gray-50
        },
      },
    },
  },
});

export { theme, darkTheme };
