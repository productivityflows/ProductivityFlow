import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import DashboardPage from './pages/Dashboard';
import TeamManagementPage from './pages/TeamManagement';
import CompliancePage from './pages/Compliance';

interface LayoutProps {
  children: React.ReactNode;
  activeRoute: string;
  onNavigate: (route: string) => void;
}

function Layout({ children, activeRoute, onNavigate }: LayoutProps) {
  return (
    <div className="flex min-h-screen bg-gray-50 font-sans">
      <Sidebar activeRoute={activeRoute} onNavigate={onNavigate} />
      <main className="flex-1 pl-64">
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}

export default function App() {
  const [currentRoute, setCurrentRoute] = useState('/');

  const handleNavigate = (route: string) => {
    setCurrentRoute(route);
  };

  const renderPage = () => {
    switch (currentRoute) {
      case '/':
        return <DashboardPage />;
      case '/team-management':
        return <TeamManagementPage />;
      case '/compliance':
        return <CompliancePage />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <Layout activeRoute={currentRoute} onNavigate={handleNavigate}>
      {renderPage()}
    </Layout>
  );
}