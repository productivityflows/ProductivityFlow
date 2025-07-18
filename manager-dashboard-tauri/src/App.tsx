import React, { useState } from 'react';
import ErrorBoundary from './components/ErrorBoundary';
import { Sidebar } from './components/Sidebar';
import DashboardPage from './pages/Dashboard';
import TeamManagementPage from './pages/TeamManagement';
import BillingPage from './pages/Billing';
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
        <div className="p-8">
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </div>
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
    try {
      switch (currentRoute) {
        case '/':
          return <DashboardPage />;
        case '/team-management':
          return <TeamManagementPage />;
        case '/billing':
          return <BillingPage />;
        case '/compliance':
          return <CompliancePage />;
        default:
          return <DashboardPage />;
      }
    } catch (error) {
      console.error('Error rendering page:', error);
      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <h3 className="text-red-800 font-medium">Page Error</h3>
          <p className="text-red-600 text-sm">
            Failed to load this page. Please try navigating to a different section.
          </p>
        </div>
      );
    }
  };

  return (
    <ErrorBoundary>
      <Layout activeRoute={currentRoute} onNavigate={handleNavigate}>
        {renderPage()}
      </Layout>
    </ErrorBoundary>
  );
}