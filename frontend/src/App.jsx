import { useState } from 'react';
import Sidebar from './components/Sidebar/Sidebar.jsx';
import Dashboard from './components/Dashboard/Dashboard.jsx';
import LogInteractionScreen from './components/LogInteraction/LogInteractionScreen.jsx';
import HCPDirectory from './components/HCPDirectory/HCPDirectory.jsx';
import InteractionHistory from './components/InteractionHistory/InteractionHistory.jsx';
import ProductCatalog from './components/Products/ProductCatalog.jsx';
import { Activity, Shield } from 'lucide-react';

const PAGE_TITLES = {
  dashboard: 'Dashboard',
  log: 'Log Interaction',
  hcps: 'HCP Directory',
  history: 'Interaction History',
  products: 'Product Catalog',
};

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard': return <Dashboard onNavigate={setActivePage} />;
      case 'log': return <LogInteractionScreen />;
      case 'hcps': return <HCPDirectory />;
      case 'history': return <InteractionHistory />;
      case 'products': return <ProductCatalog />;
      default: return <Dashboard onNavigate={setActivePage} />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />

      <main className="main-content">
        <header className="main-header">
          <h2 className="header-title">{PAGE_TITLES[activePage]}</h2>
          <div className="header-actions">
            <div className="status-chip online">
              <span className="status-dot" />
              Agent Active
            </div>
            <div className="status-chip" style={{
              background: 'var(--accent-indigo-light)',
              color: 'var(--accent-indigo)',
              borderColor: 'rgba(99, 102, 241, 0.2)',
            }}>
              <Shield size={12} />
              HCP Module v1.0
            </div>
          </div>
        </header>

        <div className="main-page">
          {renderPage()}
        </div>
      </main>
    </div>
  );
}
