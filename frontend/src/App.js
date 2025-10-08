import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import HomePage from "./pages/HomePage";
import RankingsPage from "./pages/RankingsPage";
import ContributePageAdvanced from "./pages/ContributePageAdvanced";
import LoginPage from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/RegisterPage";
import AdminDashboard from "./pages/admin/AdminDashboard";
import ContributionsPage from "./pages/admin/ContributionsPage";
import SyncManagementPage from "./pages/admin/SyncManagementPage";
import { Toaster } from "./components/ui/sonner";
import { AuthProvider } from "./contexts/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <Navbar />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/rankings" element={<RankingsPage />} />
            <Route path="/auth/login" element={<LoginPage />} />
            <Route path="/auth/register" element={<RegisterPage />} />
            <Route
              path="/contribute"
              element={
                <ProtectedRoute>
                  <ContributePageAdvanced />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/contributions"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <ContributionsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/sync"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <SyncManagementPage />
                </ProtectedRoute>
              }
            />
          </Routes>
          <Footer />
          <Toaster />
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;