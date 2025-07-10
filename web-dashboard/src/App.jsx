import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import DashboardPage from './pages/Dashboard';
import TeamManagementPage from './pages/TeamManagement';
import CompliancePage from './pages/Compliance'; // New import

function Layout({ children }) {
  return (
    <div className="flex min-h-screen bg-gray-50 font-sans">
      <Sidebar />
      <main className="flex-1 pl-64">
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout><DashboardPage /></Layout>} />
        <Route path="/team-management" element={<Layout><TeamManagementPage /></Layout>} />
        <Route path="/compliance" element={<Layout><CompliancePage /></Layout>} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}