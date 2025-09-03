import React, { useState, useEffect } from 'react';
import { styled } from '@mui/material/styles';
import { Box, CssBaseline, Toolbar, useMediaQuery, useTheme } from '@mui/material';
import { Outlet, useLocation } from 'react-router-dom';
import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material/styles';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { useThemeContext } from '../../contexts/ThemeContext';
import AppBar from './AppBar';
import Sidebar from './Sidebar';
import { theme as customTheme, darkTheme } from '../../../theme/theme';

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })<{
  open?: boolean;
  isMobile?: boolean;
}>(({ theme, open, isMobile }) => ({
  flexGrow: 1,
  padding: isMobile ? theme.spacing(1) : theme.spacing(3),
  transition: theme.transitions.create('margin', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  marginLeft: 0,
  ...(open && !isMobile && {
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: 0,
  }),
  width: '100%',
  height: '100vh',
  overflow: 'auto',
  backgroundColor: theme.palette.background.default,
}));

const MainLayout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const theme = useTheme();
  const { isDark } = useThemeContext();
  const location = useLocation();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Close mobile menu when route changes
  useEffect(() => {
    if (mobileOpen && isMobile) {
      handleDrawerClose();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location]);

  const handleDrawerOpen = () => {
    setMobileOpen(true);
    setIsClosing(false);
  };

  const handleDrawerClose = () => {
    setIsClosing(true);
    setTimeout(() => {
      setMobileOpen(false);
    }, 200); // Match this with your transition duration
  };

  // Apply theme based on dark mode preference
  const themeToUse = createTheme({
    ...(isDark ? darkTheme : customTheme),
    palette: {
      ...(isDark ? darkTheme.palette : customTheme.palette),
      mode: isDark ? 'dark' : 'light',
    },
  });

  return (
    <MuiThemeProvider theme={themeToUse}>
      <StyledThemeProvider theme={themeToUse}>
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          <CssBaseline />
          
          {/* App Bar */}
          <AppBar 
            open={mobileOpen} 
            handleDrawerOpen={handleDrawerOpen} 
          />
          
          {/* Sidebar */}
          <Sidebar 
            open={mobileOpen} 
            handleDrawerClose={handleDrawerClose} 
          />
          
          {/* Main Content */}
          <Main 
            open={mobileOpen} 
            isMobile={isMobile}
            sx={{
              pt: { xs: 8, sm: 10 },
              pb: { xs: 2, sm: 3 },
              px: { xs: 2, sm: 3 },
            }}
          >
            <Toolbar /> {/* This Toolbar helps with proper spacing below the AppBar */}
            <Box
              sx={{
                maxWidth: '100%',
                width: '100%',
                mx: 'auto',
                ...(isMobile ? {} : { maxWidth: 'calc(100% - 280px)' }),
              }}
            >
              <Outlet />
            </Box>
          </Main>
        </Box>
      </StyledThemeProvider>
    </MuiThemeProvider>
  );
};

export default MainLayout;
