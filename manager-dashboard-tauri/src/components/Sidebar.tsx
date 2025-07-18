import React from 'react';
import { LayoutDashboard, Users, Shield, Activity, CreditCard } from 'lucide-react';

interface NavItem {
  icon: React.ComponentType<any>;
  label: string;
  href: string;
}

interface SidebarProps {
  activeRoute: string;
  onNavigate: (route: string) => void;
}

const navItems: NavItem[] = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/" },
  { icon: Users, label: "Team Management", href: "/team-management" },
  { icon: CreditCard, label: "Billing", href: "/billing" },
  { icon: Shield, label: "Compliance", href: "/compliance" },
];

export function Sidebar({ activeRoute, onNavigate }: SidebarProps) {
  return (
    <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200">
      <div className="flex h-full flex-col">
        {/* Header */}
        <div className="flex h-16 items-center px-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg text-gray-800">ProductivityFlow</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const isActive = activeRoute === item.href;
            const Icon = item.icon;
            return (
              <button
                key={item.label}
                onClick={() => onNavigate(item.href)}
                className={`w-full flex items-center gap-3 h-10 px-3 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
}