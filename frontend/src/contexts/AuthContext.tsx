import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Mock authentication service (replace with actual API calls)
const authService = {
  login: async (email: string, password: string): Promise<User> => {
    // Simulate API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          id: '1',
          name: 'John Doe',
          email,
          avatar: 'https://i.pravatar.cc/150?img=32',
          role: 'developer',
        });
      }, 1000);
    });
  },
  
  register: async (name: string, email: string, password: string): Promise<User> => {
    // Simulate API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          id: '1',
          name,
          email,
          role: 'developer',
        });
      }, 1000);
    });
  },
  
  logout: async (): Promise<void> => {
    // Simulate API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve();
      }, 500);
    });
  },
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  // Check for existing session on initial load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // In a real app, you would verify the session with your backend
        const token = localStorage.getItem('authToken');
        if (token) {
          // Verify token and fetch user data
          // const userData = await verifyToken(token);
          // setUser(userData);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('authToken');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const userData = await authService.login(email, password);
      setUser(userData);
      localStorage.setItem('authToken', 'dummy-token');
      enqueueSnackbar('Successfully logged in', { variant: 'success' });
      navigate('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      enqueueSnackbar('Login failed. Please check your credentials.', { variant: 'error' });
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string) => {
    try {
      setIsLoading(true);
      const userData = await authService.register(name, email, password);
      setUser(userData);
      localStorage.setItem('authToken', 'dummy-token');
      enqueueSnackbar('Registration successful!', { variant: 'success' });
      navigate('/dashboard');
    } catch (error) {
      console.error('Registration failed:', error);
      enqueueSnackbar('Registration failed. Please try again.', { variant: 'error' });
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);
      await authService.logout();
      setUser(null);
      localStorage.removeItem('authToken');
      enqueueSnackbar('Successfully logged out', { variant: 'info' });
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
      enqueueSnackbar('Logout failed. Please try again.', { variant: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  const updateUser = (userData: Partial<User>) => {
    if (user) {
      setUser({ ...user, ...userData });
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Higher Order Component for protected routes
export const withAuth = <P extends object>(
  WrappedComponent: React.ComponentType<P>
): React.FC<P> => {
  const WithAuth: React.FC<P> = (props) => {
    const { isAuthenticated, isLoading } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
      if (!isLoading && !isAuthenticated) {
        navigate('/login', { replace: true });
      }
    }, [isAuthenticated, isLoading, navigate]);

    if (isLoading) {
      return <div>Loading...</div>; // Or a loading spinner
    }

    if (!isAuthenticated) {
      return null;
    }

    return <WrappedComponent {...props} />;
  };

  return WithAuth;
};
