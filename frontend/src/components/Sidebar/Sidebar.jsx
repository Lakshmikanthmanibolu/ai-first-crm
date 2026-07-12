import {
  LayoutDashboard, MessageSquarePlus, Users, Clock, Package,
  Activity, Sparkles
} from 'lucide-react';

const NAV_ITEMS = [
  { section: 'Main', items: [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'log', label: 'Log Interaction', icon: MessageSquarePlus, badge: 'AI' },
  ]},
  { section: 'CRM', items: [
    { id: 'hcps', label: 'HCP Directory', icon: Users },
    { id: 'history', label: 'Interaction History', icon: Clock },
    { id: 'products', label: 'Product Catalog', icon: Package },
  ]},
];

export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-inner">
          <div className="sidebar-logo">
            <Sparkles size={18} />
          </div>
          <div>
            <h1>MedConnect</h1>
            <span>AI-First CRM</span>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((section) => (
          <div key={section.section}>
            <div className="nav-section-label">{section.section}</div>
            {section.items.map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.id}
                  id={`nav-${item.id}`}
                  className={`nav-item ${activePage === item.id ? 'active' : ''}`}
                  onClick={() => onNavigate(item.id)}
                >
                  <Icon size={18} className="nav-item-icon" />
                  {item.label}
                  {item.badge && (
                    <span className="nav-item-badge">{item.badge}</span>
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </nav>

      <div style={{
        padding: '16px 20px',
        borderTop: '1px solid var(--border-subtle)',
        fontSize: '0.72rem',
        color: 'var(--text-muted)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
          <Activity size={12} style={{ color: 'var(--accent-emerald)' }} />
          <span style={{ fontWeight: 600, color: 'var(--text-tertiary)' }}>LangGraph Agent Active</span>
        </div>
        <div>Powered by Groq · gemma2-9b-it</div>
      </div>
    </aside>
  );
}
