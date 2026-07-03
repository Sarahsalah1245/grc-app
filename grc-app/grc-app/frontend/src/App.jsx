import { BrowserRouter, Routes, Route, Navigate, NavLink, useNavigate } from 'react-router-dom';
import { isAuthenticated, clearToken } from './lib/api';
import Login from './pages/Login';
import Register from './pages/Register';
import RiskCalculator from './pages/RiskCalculator';
import SwotAnalysis from './pages/SwotAnalysis';
import CobitReference from './pages/CobitReference';

function ProtectedRoute({ children }) {
  if (!isAuthenticated()) return <Navigate to="/login" replace />;
  return children;
}

function Sidebar() {
  const navigate = useNavigate();
  const linkClass = ({ isActive }) => 'nav-link' + (isActive ? ' active' : '');

  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark" />
        GRC Intelligence
      </div>
      <NavLink to="/" className={linkClass} end>Risk Calculator</NavLink>
      <NavLink to="/swot" className={linkClass}>SWOT Analysis</NavLink>
      <NavLink to="/cobit" className={linkClass}>COBIT 2019 Reference</NavLink>
      <div style={{ marginTop: 'auto', paddingTop: 24 }}>
        <button className="ghost" onClick={() => { clearToken(); navigate('/login'); }}>
          Log Out
        </button>
      </div>
    </aside>
  );
}

function Layout({ children }) {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={
          <ProtectedRoute><Layout><RiskCalculator /></Layout></ProtectedRoute>
        } />
        <Route path="/swot" element={
          <ProtectedRoute><Layout><SwotAnalysis /></Layout></ProtectedRoute>
        } />
        <Route path="/cobit" element={
          <ProtectedRoute><Layout><CobitReference /></Layout></ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}
