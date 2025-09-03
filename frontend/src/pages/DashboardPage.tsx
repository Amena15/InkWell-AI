import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Box, 
  Grid, 
  Typography, 
  Card, 
  CardContent, 
  CardActionArea, 
  CardMedia, 
  Button, 
  TextField, 
  InputAdornment, 
  Skeleton,
  useTheme,
  useMediaQuery,
  Paper,
  Divider,
  Chip,
  Avatar,
  Stack,
  IconButton,
  Tooltip,
} from '@mui/material';
import { 
  Code as CodeIcon, 
  Search as SearchIcon, 
  Add as AddIcon, 
  Folder as FolderIcon, 
  History as HistoryIcon, 
  Star as StarIcon, 
  MoreVert as MoreVertIcon,
  FileUpload as FileUploadIcon,
  Description as DocumentIcon,
  Api as ApiIcon,
  Book as BookIcon,
  School as TutorialIcon,
  Dashboard as DashboardIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Sort as SortIcon,
} from '@mui/icons-material';
import { useTheme as useThemeContext } from '@mui/material/styles';
import { styled } from '@mui/material/styles';
import { useAuth } from '../contexts/AuthContext';

// Styled Components
const StatCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.2s, box-shadow 0.2s',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[6],
  },
}));

const StatCardContent = styled(CardContent)(({ theme }) => ({
  flexGrow: 1,
  display: 'flex',
  flexDirection: 'column',
  padding: theme.spacing(3),
}));

const StatValue = styled(Typography)(({ theme }) => ({
  fontSize: '2.5rem',
  fontWeight: 700,
  lineHeight: 1.2,
  margin: `${theme.spacing(1)} 0`,
  background: theme.palette.mode === 'dark' 
    ? 'linear-gradient(45deg, #6366F1, #8B5CF6)' 
    : 'linear-gradient(45deg, #4F46E5, #7C3AED)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
}));

const QuickActionButton = styled(Button)(({ theme }) => ({
  height: '100%',
  padding: theme.spacing(3, 2),
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  textAlign: 'center',
  borderRadius: theme.shape.borderRadius,
  transition: 'all 0.2s',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: theme.shadows[4],
  },
}));

const RecentDocCard = styled(Card)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
  transition: 'transform 0.2s, box-shadow 0.2s',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: theme.shadows[4],
  },
}));

const RecentDocContent = styled(CardContent)(({ theme }) => ({
  flexGrow: 1,
  display: 'flex',
  flexDirection: 'column',
  padding: theme.spacing(2),
}));

// Mock data
const stats = [
  { id: 1, title: 'Total Documents', value: '1,248', icon: <DocumentIcon fontSize="large" />, color: 'primary' },
  { id: 2, title: 'API Endpoints', value: '342', icon: <ApiIcon fontSize="large" />, color: 'secondary' },
  { id: 3, title: 'Guides', value: '156', icon: <BookIcon fontSize="large" />, color: 'success' },
  { id: 4, title: 'Tutorials', value: '89', icon: <TutorialIcon fontSize="large" />, color: 'warning' },
];

const quickActions = [
  { id: 1, title: 'New Document', icon: <AddIcon fontSize="large" />, color: 'primary', path: '/documentation/new' },
  { id: 2, title: 'Upload File', icon: <FileUploadIcon fontSize="large" />, color: 'secondary', path: '/documentation/upload' },
  { id: 3, title: 'API Reference', icon: <CodeIcon fontSize="large" />, color: 'info', path: '/documentation/api' },
  { id: 4, title: 'View History', icon: <HistoryIcon fontSize="large" />, color: 'warning', path: '/history' },
];

const recentDocs = [
  { 
    id: 1, 
    title: 'Getting Started with API', 
    type: 'Guide', 
    updated: '2 hours ago',
    category: 'API',
    icon: <BookIcon />,
    color: '#4F46E5',
  },
  { 
    id: 2, 
    title: 'User Authentication', 
    type: 'Tutorial', 
    updated: '1 day ago',
    category: 'Security',
    icon: <TutorialIcon />,
    color: '#10B981',
  },
  { 
    id: 3, 
    title: 'API v2 Reference', 
    type: 'API', 
    updated: '3 days ago',
    category: 'Documentation',
    icon: <ApiIcon />,
    color: '#8B5CF6',
  },
  { 
    id: 4, 
    title: 'Migration Guide', 
    type: 'Guide', 
    updated: '1 week ago',
    category: 'Updates',
    icon: <BookIcon />,
    color: '#F59E0B',
  },
];

const activityLogs = [
  { id: 1, user: 'John Doe', action: 'updated', document: 'API Reference', time: '5 minutes ago', avatar: 'J' },
  { id: 2, user: 'Jane Smith', action: 'commented on', document: 'User Guide', time: '1 hour ago', avatar: 'JS' },
  { id: 3, user: 'Alex Johnson', action: 'created', document: 'New Tutorial', time: '3 hours ago', avatar: 'AJ' },
  { id: 4, user: 'Sarah Wilson', action: 'reviewed', document: 'API Documentation', time: '1 day ago', avatar: 'SW' },
];

const DashboardPage: React.FC = () => {
  const theme = useTheme();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const muiTheme = useThemeContext();

  // Simulate loading
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const handleQuickAction = (path: string) => {
    navigate(path);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const renderSkeleton = () => (
    <Grid container spacing={3}>
      {[1, 2, 3, 4].map((item) => (
        <Grid item xs={12} sm={6} md={3} key={item}>
          <Skeleton variant="rectangular" height={150} sx={{ borderRadius: 2 }} />
        </Grid>
      ))}
    </Grid>
  );

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="text" width={200} height={40} sx={{ mb: 3 }} />
        {renderSkeleton()}
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Welcome back, {user?.name || 'User'}! 👋
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Here's what's happening with your documentation today
            </Typography>
          </Box>
          <Box>
            <Button 
              variant="contained" 
              color="primary" 
              startIcon={<AddIcon />}
              onClick={() => navigate('/documentation/new')}
              size={isMobile ? 'medium' : 'large'}
            >
              New Document
            </Button>
          </Box>
        </Box>

        {/* Search Bar */}
        <Box component="form" onSubmit={handleSearch} sx={{ mt: 3, mb: 4 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search documentation..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
              sx: { 
                borderRadius: 50, 
                bgcolor: 'background.paper',
                '& .MuiOutlinedInput-notchedOutline': {
                  borderWidth: '1px',
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'primary.main',
                },
              },
            }}
          />
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat) => (
          <Grid item xs={12} sm={6} md={3} key={stat.id}>
            <StatCard>
              <StatCardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      {stat.title}
                    </Typography>
                    <StatValue>{stat.value}</StatValue>
                  </Box>
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: '12px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: `${stat.color}.light`,
                      color: `${stat.color}.main`,
                    }}
                  >
                    {stat.icon}
                  </Box>
                </Box>
                <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                  <Typography variant="caption" color="success.main" sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box component="span" sx={{ color: 'success.main', mr: 0.5 }}>▲</Box>
                    12% from last month
                  </Typography>
                </Box>
              </StatCardContent>
            </StatCard>
          </Grid>
        ))}
      </Grid>

      {/* Quick Actions */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          {quickActions.map((action) => (
            <Grid item xs={6} sm={3} key={action.id}>
              <Paper
                component={CardActionArea}
                onClick={() => handleQuickAction(action.path)}
                sx={{
                  height: '100%',
                  borderRadius: 2,
                  p: 2,
                  textAlign: 'center',
                  transition: 'all 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: muiTheme.shadows[6],
                  },
                }}
              >
                <Box
                  sx={{
                    width: 56,
                    height: 56,
                    borderRadius: '50%',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: `${action.color}.light`,
                    color: `${action.color}.main`,
                    mb: 1.5,
                  }}
                >
                  {action.icon}
                </Box>
                <Typography variant="subtitle2">{action.title}</Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>

      <Grid container spacing={3}>
        {/* Recent Documents */}
        <Grid item xs={12} md={8}>
          <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Recent Documents</Typography>
            <Box>
              <Tooltip title="Refresh">
                <IconButton size="small" sx={{ mr: 1 }}>
                  <RefreshIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Filter">
                <IconButton size="small" sx={{ mr: 1 }}>
                  <FilterIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Sort">
                <IconButton size="small">
                  <SortIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
          
          <Grid container spacing={2}>
            {recentDocs.map((doc) => (
              <Grid item xs={12} key={doc.id}>
                <RecentDocCard>
                  <RecentDocContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box
                        sx={{
                          width: 40,
                          height: 40,
                          borderRadius: '8px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          bgcolor: `${doc.color}20`,
                          color: doc.color,
                          mr: 2,
                        }}
                      >
                        {doc.icon}
                      </Box>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle1" component="div">
                          {doc.title}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                          <Chip 
                            label={doc.type} 
                            size="small" 
                            sx={{ 
                              height: 20, 
                              mr: 1, 
                              fontSize: '0.675rem',
                              bgcolor: 'action.selected',
                            }} 
                          />
                          <Typography variant="caption" color="text.secondary">
                            {doc.updated} • {doc.category}
                          </Typography>
                        </Box>
                      </Box>
                      <IconButton size="small" sx={{ ml: 1 }}>
                        <MoreVertIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  </RecentDocContent>
                </RecentDocCard>
              </Grid>
            ))}
          </Grid>
          
          <Box sx={{ mt: 2, textAlign: 'right' }}>
            <Button 
              color="primary" 
              endIcon={<ChevronRightIcon />}
              onClick={() => navigate('/documents')}
            >
              View all documents
            </Button>
          </Box>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Recent Activity</Typography>
            <Button size="small" onClick={() => navigate('/activity')}>
              View All
            </Button>
          </Box>
          
          <Paper sx={{ p: 2, borderRadius: 2 }}>
            <List disablePadding>
              {activityLogs.map((log, index) => (
                <React.Fragment key={log.id}>
                  <ListItem 
                    disableGutters 
                    sx={{ 
                      py: 1.5,
                      px: 1,
                      borderRadius: 1,
                      '&:hover': {
                        bgcolor: 'action.hover',
                      },
                    }}
                  >
                    <ListItemAvatar>
                      <Avatar sx={{ width: 36, height: 36, bgcolor: 'primary.main' }}>
                        {log.avatar}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <React.Fragment>
                          <Typography component="span" variant="subtitle2" color="text.primary">
                            {log.user}
                          </Typography>
                          {' '}{log.action}{' '}
                          <Typography component="span" variant="subtitle2" color="primary">
                            {log.document}
                          </Typography>
                        </React.Fragment>
                      }
                      secondary={
                        <Typography variant="caption" color="text.secondary">
                          {log.time}
                        </Typography>
                      }
                      secondaryTypographyProps={{ component: 'div' }}
                      sx={{ my: 0 }}
                    />
                  </ListItem>
                  {index < activityLogs.length - 1 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
          
          {/* Quick Links */}
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              QUICK LINKS
            </Typography>
            <List disablePadding>
              <ListItem button sx={{ px: 1, py: 1.5, borderRadius: 1 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <DescriptionIcon fontSize="small" color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary={
                    <Typography variant="body2" color="text.primary">
                      API Documentation Guide
                    </Typography>
                  } 
                />
                <ChevronRightIcon fontSize="small" color="action" />
              </ListItem>
              <ListItem button sx={{ px: 1, py: 1.5, borderRadius: 1 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <SchoolIcon fontSize="small" color="secondary" />
                </ListItemIcon>
                <ListItemText 
                  primary={
                    <Typography variant="body2" color="text.primary">
                      Getting Started Tutorial
                    </Typography>
                  } 
                />
                <ChevronRightIcon fontSize="small" color="action" />
              </ListItem>
              <ListItem button sx={{ px: 1, py: 1.5, borderRadius: 1 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <CodeIcon fontSize="small" color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary={
                    <Typography variant="body2" color="text.primary">
                      API Reference
                    </Typography>
                  } 
                />
                <ChevronRightIcon fontSize="small" color="action" />
              </ListItem>
            </List>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
