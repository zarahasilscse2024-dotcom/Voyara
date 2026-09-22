import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import VoyaraIntro from './components/VoyaraIntro';
import { AuthProvider, useAuth } from './context/AuthContext';
import Home from './pages/HomeV2';
import Explore from './pages/Explore';
import Auth, { ForgotPassword } from './pages/AuthV3';
import { Details, Favorites, Compare, Safety, Recommendations, Booking } from './pages/SimplePages';
import { Profile, Bookings } from './pages/Account';
import { OperatorDashboard, OperatorPackageForm, AdminDashboard } from './pages/Management';
import './index.css';

function Protected({ children }) { const { user, loading } = useAuth(); if (loading) return <div className="empty">Loading Voyara...</div>; return user ? children : <Navigate to="/login" replace />; }
function Role({ role, children }) { const { user, loading } = useAuth(); if (loading) return <div className="empty">Loading Voyara...</div>; return user?.role === role ? children : <Navigate to="/login" replace />; }

export default function App() { return <AuthProvider><BrowserRouter><Layout><Routes>
	<Route path="/" element={<VoyaraIntro><Home /></VoyaraIntro>} />
+  <Route path="/explore" element={<Explore />} />
+  <Route path="/login" element={<Auth />} />
+  <Route path="/register" element={<Auth register />} />
+  <Route path="/forgot-password" element={<ForgotPassword />} />
+  <Route path="/package/:id" element={<Details />} />
+  <Route path="/book/:id" element={<Protected><Booking /></Protected>} />
+  <Route path="/compare" element={<Compare />} />
+  <Route path="/safety" element={<Safety />} />
+  <Route path="/recommendations" element={<Protected><Recommendations /></Protected>} />
+  <Route path="/favorites" element={<Protected><Favorites /></Protected>} />
+  <Route path="/profile" element={<Protected><Profile /></Protected>} />
+  <Route path="/bookings" element={<Protected><Bookings /></Protected>} />
+  <Route path="/operator" element={<Role role="operator"><OperatorDashboard /></Role>} />
+  <Route path="/operator/packages/new" element={<Role role="operator"><OperatorPackageForm /></Role>} />
+  <Route path="/admin" element={<Role role="admin"><AdminDashboard /></Role>} />
+  <Route path="*" element={<Navigate to="/" />} />
+</Routes></Layout></BrowserRouter></AuthProvider>; }
