# ⚛️ EJEMPLOS DE CÓDIGO FRONTEND (REACT)

**Stack:** React 18 + TypeScript + React Router v6 + Axios
**Estilos:** TailwindCSS o Material-UI (a elección)

---

## [8] CONFIGURACIÓN DE SERVICIOS Y API

### 8.1 Configuración de Axios con Interceptores

```typescript
// frontend/src/services/api.ts

import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

// Crear instancia de Axios
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de Request - Agregar token automáticamente
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor de Response - Manejar refresh token automáticamente
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Si el error es 401 y no hemos reintentado
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');

        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        // Intentar renovar el access token
        const response = await axios.post(
          `${api.defaults.baseURL}/auth/refresh`,
          { refresh_token: refreshToken }
        );

        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);

        // Reintentar la petición original con el nuevo token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }

        return api(originalRequest);
      } catch (refreshError) {
        // Si falla el refresh, cerrar sesión
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

---

### 8.2 Servicio de Autenticación

```typescript
// frontend/src/services/authService.ts

import api from './api';
import {
  LoginRequest,
  LoginResponse,
  RegistroRequest,
  Usuario
} from '../types/auth.types';

export const authService = {
  /**
   * Login con email y password
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/login', data);

    // Guardar tokens y usuario en localStorage
    const { access_token, refresh_token, user } = response.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    localStorage.setItem('user', JSON.stringify(user));

    return response.data;
  },

  /**
   * Registro público
   */
  async registro(data: RegistroRequest): Promise<Usuario> {
    const response = await api.post<Usuario>('/auth/registro', data);
    return response.data;
  },

  /**
   * Obtener usuario actual
   */
  async getMe(): Promise<Usuario> {
    const response = await api.get<Usuario>('/auth/me');
    return response.data;
  },

  /**
   * Logout
   */
  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');

    try {
      if (refreshToken) {
        await api.post('/auth/logout', { refresh_token: refreshToken });
      }
    } finally {
      // Limpiar localStorage siempre
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  /**
   * Verificar si hay sesión activa
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    return !!token;
  },

  /**
   * Obtener usuario del localStorage
   */
  getCurrentUser(): Usuario | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;

    try {
      return JSON.parse(userStr) as Usuario;
    } catch {
      return null;
    }
  },

  /**
   * Obtener rol del usuario actual
   */
  getCurrentUserRole(): string | null {
    const user = this.getCurrentUser();
    return user?.rol || null;
  }
};
```

---

## [9] CONTEXT DE AUTENTICACIÓN

### 9.1 AuthContext con React Context API

```typescript
// frontend/src/context/AuthContext.tsx

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService } from '../services/authService';
import { Usuario, LoginRequest, RegistroRequest } from '../types/auth.types';

interface AuthContextType {
  user: Usuario | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  registro: (data: RegistroRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<Usuario | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Cargar usuario al montar el componente
  useEffect(() => {
    const initAuth = async () => {
      if (authService.isAuthenticated()) {
        try {
          const userData = await authService.getMe();
          setUser(userData);
        } catch (error) {
          console.error('Error al obtener usuario:', error);
          // Si falla, limpiar sesión
          await authService.logout();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (data: LoginRequest) => {
    const response = await authService.login(data);
    setUser(response.user);
  };

  const registro = async (data: RegistroRequest) => {
    await authService.registro(data);
    // No hacer login automático, usuario debe esperar aprobación
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const refreshUser = async () => {
    if (authService.isAuthenticated()) {
      const userData = await authService.getMe();
      setUser(userData);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    registro,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Hook personalizado para usar el contexto
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth debe ser usado dentro de AuthProvider');
  }
  return context;
};
```

---

## [10] GUARDS Y PROTECCIÓN DE RUTAS

### 10.1 PrivateRoute - Requiere autenticación

```typescript
// frontend/src/guards/PrivateRoute.tsx

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Spinner } from '../components/common/Spinner';

interface PrivateRouteProps {
  children: React.ReactElement;
}

export const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <Spinner />;
  }

  if (!isAuthenticated) {
    // Redirigir a login guardando la ubicación actual
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};
```

---

### 10.2 RoleGuard - Requiere rol específico

```typescript
// frontend/src/guards/RoleGuard.tsx

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Alert } from '../components/common/Alert';

interface RoleGuardProps {
  children: React.ReactElement;
  rolesPermitidos: string[];
  fallbackPath?: string;
}

export const RoleGuard: React.FC<RoleGuardProps> = ({
  children,
  rolesPermitidos,
  fallbackPath = '/dashboard'
}) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div>Cargando...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Verificar que el usuario tenga uno de los roles permitidos
  const tienePermiso = user.rol && rolesPermitidos.includes(user.rol);

  if (!tienePermiso) {
    return (
      <div className="p-4">
        <Alert type="error">
          No tienes permisos para acceder a esta sección.
          Se requiere uno de los siguientes roles: {rolesPermitidos.join(', ')}
        </Alert>
        <div className="mt-4">
          <Navigate to={fallbackPath} replace />
        </div>
      </div>
    );
  }

  return children;
};
```

---

### 10.3 PublicRoute - Solo para no autenticados

```typescript
// frontend/src/guards/PublicRoute.tsx

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface PublicRouteProps {
  children: React.ReactElement;
}

export const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Cargando...</div>;
  }

  if (isAuthenticated) {
    // Si ya está autenticado, redirigir a dashboard
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};
```

---

## [11] CONFIGURACIÓN DE RUTAS

### 11.1 AppRoutes con Guards

```typescript
// frontend/src/routes/AppRoutes.tsx

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { PrivateRoute } from '../guards/PrivateRoute';
import { PublicRoute } from '../guards/PublicRoute';
import { RoleGuard } from '../guards/RoleGuard';

// Páginas públicas
import LoginPage from '../pages/auth/LoginPage';
import RegistroPage from '../pages/auth/RegistroPage';
import RegistroExitosoPage from '../pages/auth/RegistroExitosoPage';

// Páginas privadas - Dashboard
import DashboardPage from '../pages/dashboard/DashboardPage';
import Layout from '../components/layout/Layout';

// Usuarios Sistema (solo admin)
import UsuariosPendientesPage from '../pages/usuarios-sistema/UsuariosPendientesPage';
import UsuariosListaPage from '../pages/usuarios-sistema/UsuariosListaPage';

// Pacientes
import PacientesListaPage from '../pages/pacientes/PacientesListaPage';
import PacienteDetallePage from '../pages/pacientes/PacienteDetallePage';
import PacienteCrearPage from '../pages/pacientes/PacienteCrearPage';

// Boxes
import BoxesListaPage from '../pages/boxes/BoxesListaPage';
import BoxCrearPage from '../pages/boxes/BoxCrearPage';

// Agenda
import AgendaCalendarioPage from '../pages/agenda/AgendaCalendarioPage';
import CitaCrearPage from '../pages/agenda/CitaCrearPage';

// Atenciones
import AtencionesListaPage from '../pages/atenciones/AtencionesListaPage';
import RegistrarAtencionPage from '../pages/atenciones/RegistrarAtencionPage';

// Reportes
import ReportesPage from '../pages/reportes/ReportesPage';

// Perfil
import PerfilPage from '../pages/perfil/PerfilPage';

export const AppRoutes: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* ==================== RUTAS PÚBLICAS ==================== */}
          <Route path="/login" element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          } />

          <Route path="/registro" element={
            <PublicRoute>
              <RegistroPage />
            </PublicRoute>
          } />

          <Route path="/registro-exitoso" element={<RegistroExitosoPage />} />

          {/* ==================== RUTAS PRIVADAS ==================== */}
          <Route path="/" element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }>
            {/* Dashboard */}
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />

            {/* Usuarios Sistema - SOLO ADMIN */}
            <Route path="usuarios-sistema">
              <Route path="pendientes" element={
                <RoleGuard rolesPermitidos={['admin']}>
                  <UsuariosPendientesPage />
                </RoleGuard>
              } />
              <Route path="lista" element={
                <RoleGuard rolesPermitidos={['admin']}>
                  <UsuariosListaPage />
                </RoleGuard>
              } />
            </Route>

            {/* Pacientes - TODOS (lectura), ADMIN+PROFESIONAL (crear) */}
            <Route path="pacientes">
              <Route index element={<PacientesListaPage />} />
              <Route path=":id" element={<PacienteDetallePage />} />
              <Route path="crear" element={
                <RoleGuard rolesPermitidos={['admin', 'profesional']}>
                  <PacienteCrearPage />
                </RoleGuard>
              } />
            </Route>

            {/* Boxes - TODOS (lectura), ADMIN (crear/editar) */}
            <Route path="boxes">
              <Route index element={<BoxesListaPage />} />
              <Route path="crear" element={
                <RoleGuard rolesPermitidos={['admin']}>
                  <BoxCrearPage />
                </RoleGuard>
              } />
            </Route>

            {/* Agenda */}
            <Route path="agenda">
              <Route path="calendario" element={<AgendaCalendarioPage />} />
              <Route path="crear-cita" element={
                <RoleGuard rolesPermitidos={['admin']}>
                  <CitaCrearPage />
                </RoleGuard>
              } />
            </Route>

            {/* Atenciones */}
            <Route path="atenciones">
              <Route index element={<AtencionesListaPage />} />
              <Route path="registrar/:citaId" element={
                <RoleGuard rolesPermitidos={['admin', 'profesional']}>
                  <RegistrarAtencionPage />
                </RoleGuard>
              } />
            </Route>

            {/* Reportes */}
            <Route path="reportes" element={<ReportesPage />} />

            {/* Perfil */}
            <Route path="perfil" element={<PerfilPage />} />
          </Route>

          {/* Ruta 404 */}
          <Route path="*" element={<div>Página no encontrada</div>} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};
```

---

## [12] EJEMPLOS DE PÁGINAS

### 12.1 LoginPage

```typescript
// frontend/src/pages/auth/LoginPage.tsx

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Alert } from '../../components/common/Alert';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Obtener la ruta previa si existe
  const from = (location.state as any)?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login({ email, password });
      navigate(from, { replace: true });
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Error al iniciar sesión';
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-6 text-center">Iniciar Sesión</h2>

        {error && <Alert type="error" className="mb-4">{error}</Alert>}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div className="mb-6">
            <label className="block text-gray-700 mb-2">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
          >
            {isLoading ? 'Iniciando...' : 'Ingresar'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <p className="text-gray-600">
            ¿No tienes cuenta?{' '}
            <a href="/registro" className="text-blue-600 hover:underline">
              Regístrate aquí
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
```

---

### 12.2 UsuariosPendientesPage (Solo Admin)

```typescript
// frontend/src/pages/usuarios-sistema/UsuariosPendientesPage.tsx

import React, { useEffect, useState } from 'react';
import api from '../../services/api';
import { UsuarioPendiente } from '../../types/auth.types';
import { Alert } from '../../components/common/Alert';

const UsuariosPendientesPage: React.FC = () => {
  const [usuarios, setUsuarios] = useState<UsuarioPendiente[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    cargarUsuarios();
  }, []);

  const cargarUsuarios = async () => {
    try {
      const response = await api.get('/auth/usuarios-pendientes');
      setUsuarios(response.data);
    } catch (err) {
      setError('Error al cargar usuarios pendientes');
    } finally {
      setIsLoading(false);
    }
  };

  const aprobarUsuario = async (usuarioId: string, rol: string) => {
    try {
      await api.post(`/auth/aprobar/${usuarioId}`, { rol });
      await cargarUsuarios();
      alert('Usuario aprobado exitosamente');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al aprobar usuario');
    }
  };

  if (isLoading) return <div>Cargando...</div>;
  if (error) return <Alert type="error">{error}</Alert>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Usuarios Pendientes de Aprobación</h1>

      {usuarios.length === 0 ? (
        <p>No hay usuarios pendientes.</p>
      ) : (
        <table className="w-full border">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2 border">Email</th>
              <th className="p-2 border">Nombre</th>
              <th className="p-2 border">Fecha Registro</th>
              <th className="p-2 border">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {usuarios.map((u) => (
              <tr key={u.id}>
                <td className="p-2 border">{u.email}</td>
                <td className="p-2 border">{u.nombre_completo}</td>
                <td className="p-2 border">{new Date(u.creado_en).toLocaleDateString()}</td>
                <td className="p-2 border">
                  <button
                    onClick={() => aprobarUsuario(u.id, 'profesional')}
                    className="bg-blue-500 text-white px-3 py-1 rounded mr-2"
                  >
                    Profesional
                  </button>
                  <button
                    onClick={() => aprobarUsuario(u.id, 'administrativo')}
                    className="bg-green-500 text-white px-3 py-1 rounded mr-2"
                  >
                    Administrativo
                  </button>
                  <button
                    onClick={() => aprobarUsuario(u.id, 'admin')}
                    className="bg-red-500 text-white px-3 py-1 rounded"
                  >
                    Admin
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default UsuariosPendientesPage;
```

---

✅ **Frontend con Guards y RBAC completado**
