import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { styled, useTheme, Theme, CSSObject } from '@mui/material/styles';
import {
  Box,
  Drawer as MuiDrawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  Tooltip,
  Typography,
  Divider,
  useMediaQuery,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Code as CodeIcon,
  Description as DocumentationIcon,
  Settings as SettingsIcon,
  ExpandLess,
  ExpandMore,
  ChevronLeft,
  ChevronRight,
  MenuBook as GuidesIcon,
  Api as ApiIcon,
  History as HistoryIcon,
  Star as StarIcon,
  Folder as ProjectIcon,
  Group as TeamIcon,
  HelpOutline as HelpIcon,
} from '@mui/icons-material';
import { useTheme as useThemeContext } from '../../contexts/ThemeContext';

const drawerWidth = 280;

const openedMixin = (theme: Theme): CSSObject => ({
  width: drawerWidth,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: 'hidden',
  boxShadow: '1px 0 3px 0 rgba(0, 0, 0, 0.1)',
});

const closedMixin = (theme: Theme): CSSObject => ({
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  overflowX: 'hidden',
  width: `calc(${theme.spacing(7)} + 1px)`,
  [theme.breakpoints.up('sm')]: {
    width: `calc(${theme.spacing(8)} + 1px)`,
  },
  boxShadow: '1px 0 3px 0 rgba(0, 0, 0, 0.1)',
});

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
}));

const Drawer = styled(MuiDrawer, { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme, open }) => ({
    width: drawerWidth,
    flexShrink: 0,
    whiteSpace: 'nowrap',
    boxSizing: 'border-box',
    ...(open && {
      ...openedMixin(theme),
      '& .MuiDrawer-paper': openedMixin(theme),
    }),
    ...(!open && {
      ...closedMixin(theme),
      '& .MuiDrawer-paper': closedMixin(theme),
    }),
  })
);

interface MenuItem {
  title: string;
  icon: React.ReactNode;
  path: string;
  children?: MenuItem[];
}

const mainMenuItems: MenuItem[] = [
  { title: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { 
    title: 'Documentation', 
    icon: <DocumentationIcon />, 
    path: '/documentation',
    children: [
      { title: 'API Reference', icon: <ApiIcon />, path: '/documentation/api' },
      { title: 'Guides', icon: <GuidesIcon />, path: '/documentation/guides' },
      { title: 'Tutorials', icon: <CodeIcon />, path: '/documentation/tutorials' },
    ]
  },
  { title: 'Projects', icon: <ProjectIcon />, path: '/projects' },
  { title: 'Team', icon: <TeamIcon />, path: '/team' },
  { title: 'History', icon: <HistoryIcon />, path: '/history' },
  { title: 'Favorites', icon: <StarIcon />, path: '/favorites' },
];

const secondaryMenuItems: MenuItem[] = [
  { title: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  { title: 'Help & Support', icon: <HelpIcon />, path: '/help' },
];

interface SidebarProps {
  open: boolean;
  handleDrawerClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ open, handleDrawerClose }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { isDark } = useThemeContext();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [expandedItems, setExpandedItems] = useState<{ [key: string]: boolean }>({});
  const [selectedItem, setSelectedItem] = useState<string>(location.pathname);

  // Update selected item when route changes
  useEffect(() => {
    setSelectedItem(location.pathname);
  }, [location.pathname]);

  const handleItemClick = (item: MenuItem) => {
    if (item.children) {
      setExpandedItems(prev => ({
        ...prev,
        [item.path]: !prev[item.path]
      }));
    } else {
      navigate(item.path);
      if (isMobile) {
        handleDrawerClose();
      }
    }
  };

  const renderMenuItem = (item: MenuItem, depth = 0) => {
    const isSelected = selectedItem.startsWith(item.path) && (depth === 0 || selectedItem === item.path);
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems[item.path] || false;

    return (
      <React.Fragment key={item.path}>
        <ListItem 
          disablePadding 
          sx={{ 
            display: 'block',
            pl: depth * 2,
          }}
        >
          <Tooltip 
            title={!open ? item.title : ''} 
            placement="right"
            arrow
          >
            <ListItemButton
              onClick={() => handleItemClick(item)}
              selected={isSelected}
              sx={{
                minHeight: 48,
                justifyContent: open ? 'initial' : 'center',
                px: 2.5,
                borderRadius: 1,
                mx: 1,
                my: 0.5,
                '&.Mui-selected': {
                  backgroundColor: theme.palette.primary.light,
                  color: theme.palette.primary.contrastText,
                  '&:hover': {
                    backgroundColor: theme.palette.primary.main,
                  },
                  '& .MuiListItemIcon-root': {
                    color: theme.palette.primary.contrastText,
                  },
                },
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: open ? 2 : 'auto',
                  justifyContent: 'center',
                  color: isSelected ? theme.palette.primary.contrastText : 'inherit',
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.title} 
                primaryTypographyProps={{
                  variant: 'body2',
                  fontWeight: isSelected ? 600 : 400,
                }}
                sx={{ 
                  opacity: open ? 1 : 0,
                  ml: depth * 1.5,
                }} 
              />
              {hasChildren && open && (
                isExpanded ? <ExpandLess /> : <ExpandMore />
              )}
            </ListItemButton>
          </Tooltip>
        </ListItem>
        
        {hasChildren && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children?.map((child) => renderMenuItem(child, depth + 1))}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  return (
    <Drawer 
      variant={isMobile ? 'temporary' : 'permanent'} 
      open={open} 
      onClose={handleDrawerClose}
      ModalProps={{
        keepMounted: true, // Better open performance on mobile.
      }}
    >
      <DrawerHeader>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center',
          width: '100%',
          px: 1,
          visibility: open ? 'visible' : 'hidden',
        }}>
          <CodeIcon sx={{ fontSize: 28, mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" noWrap sx={{ fontWeight: 600 }}>
            InkWell AI
          </Typography>
        </Box>
        <IconButton onClick={handleDrawerClose} size="small">
          {theme.direction === 'rtl' ? <ChevronRight /> : <ChevronLeft />}
        </IconButton>
      </DrawerHeader>
      
      <Box sx={{ overflow: 'auto', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <List sx={{ flexGrow: 1 }}>
          {mainMenuItems.map((item) => renderMenuItem(item))}
        </List>
        
        <Divider sx={{ my: 1 }} />
        
        <List>
          {secondaryMenuItems.map((item) => renderMenuItem(item))}
        </List>
        
        {!open && (
          <Box sx={{ textAlign: 'center', py: 2, px: 1 }}>
            <Typography variant="caption" color="text.secondary">
              v1.0.0
            </Typography>
          </Box>
        )}
      </Box>
    </Drawer>
  );
};

export default Sidebar;
