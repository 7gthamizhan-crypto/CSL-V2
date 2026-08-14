import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Sparkles, ShieldAlert, AlertTriangle, FileSearch,
  BookOpenCheck, CheckSquare, CalendarDays, Package, Users, ClipboardCheck,
  Cpu, Database, Scale, FileText, Settings as SettingsIcon, X
} from 'lucide-react';

export function Sidebar({ mobileOpen, closeMobileSidebar }) {
  const navigationGroups = [
    {
      group: 'Overview',
      items: [
        { label: 'Operations Dashboard', path: '/', icon: LayoutDashboard }
      ]
    },
    {
      group: 'Intelligence',
      items: [
        { label: 'AI Recommendation Center', path: '/recommendations', icon: Sparkles, badge: 'NEW' },
        { label: 'AI Risk Intelligence', path: '/risk', icon: ShieldAlert },
        { label: 'Fraud & Anomaly Detection', path: '/anomalies', icon: AlertTriangle, badge: 'NEW' },
        { label: 'Document Intelligence', path: '/documents', icon: FileSearch, badge: 'NEW' },
        { label: 'HS Code Intelligence', path: '/hs-intelligence', icon: BookOpenCheck, badge: 'NEW' }
      ]
    },
    {
      group: 'Operations',
      items: [
        { label: 'Enhanced Readiness', path: '/readiness', icon: CheckSquare },
        { label: 'Schedule & Optimizer', path: '/schedule', icon: CalendarDays },
        { label: 'Container Management', path: '/containers', icon: Package },
        { label: 'Resource Management', path: '/resources', icon: Users },
        { label: 'Examination Outcome', path: '/outcomes', icon: ClipboardCheck, badge: 'NEW' }
      ]
    },
    {
      group: 'Planning',
      items: [
        { label: 'Scenario Simulator', path: '/simulator', icon: Cpu }
      ]
    },
    {
      group: 'Governance',
      items: [
        { label: 'Data Quality & Readiness', path: '/data-quality', icon: Database, badge: 'NEW' },
        { label: 'AI Governance & Audit', path: '/audit', icon: Scale, badge: 'NEW' }
      ]
    },
    {
      group: 'Analytics',
      items: [
        { label: 'Reports & Analytics', path: '/reports', icon: FileText }
      ]
    },
    {
      group: 'Admin',
      items: [
        { label: 'System Settings', path: '/settings', icon: SettingsIcon }
      ]
    }
  ];

  return (
    <>
      <div
        className={`sidebar-overlay ${mobileOpen ? 'mobile-open' : ''}`}
        onClick={closeMobileSidebar}
      />

      <aside className={`sidebar ${mobileOpen ? 'mobile-open' : ''}`}>
        {/* Sleek Header Branding */}
        <div
          className="sidebar-logo"
          style={{
            padding: '1rem 1.15rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            borderBottom: '1px solid var(--border-color)',
            background: '#ffffff',
            position: 'relative'
          }}
        >
          <img
            src="/logo.svg"
            alt="Sri Lanka Customs Logo"
            style={{
              height: '38px',
              width: 'auto',
              objectFit: 'contain',
              flexShrink: 0,
              filter: 'drop-shadow(0 2px 6px rgba(0, 102, 178, 0.2))'
            }}
          />

          <div style={{ display: 'flex', flexDirection: 'column', minWidth: 0, flex: 1 }}>
            <span
              style={{
                fontWeight: 800,
                fontSize: '0.95rem',
                letterSpacing: '-0.2px',
                color: '#0a2540',
                lineHeight: '1.25',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}
            >
              Sri Lanka Customs
            </span>
            <span
              style={{
                fontSize: '0.625rem',
                fontWeight: 700,
                color: '#0066b2',
                letterSpacing: '0.8px',
                textTransform: 'uppercase'
              }}
            >
              CORE AI ENGINE
            </span>
          </div>

          <button
            className="mobile-toggle-btn"
            style={{ color: '#0a2540', background: 'transparent', border: 'none', padding: '0.2rem' }}
            onClick={closeMobileSidebar}
          >
            <X size={18} />
          </button>
        </div>

        {/* Grouped Navigation */}
        <nav className="sidebar-nav">
          {navigationGroups.map((grp) => (
            <div key={grp.group} style={{ marginBottom: '1rem' }}>
              <div
                style={{
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  color: '#94a3b8',
                  letterSpacing: '1px',
                  padding: '0.3rem 0.6rem 0.2rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem'
                }}
              >
                <span>{grp.group}</span>
                <div style={{ flex: 1, height: '1px', background: '#e2e8f0' }} />
              </div>

              {grp.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
                    onClick={closeMobileSidebar}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', minWidth: 0, overflow: 'hidden' }}>
                      <Icon size={16} style={{ flexShrink: 0 }} />
                      <span className="nav-label">{item.label}</span>
                    </div>
                    {item.badge && (
                      <span
                        style={{
                          fontSize: '0.575rem',
                          fontWeight: 700,
                          backgroundColor: '#3b82f6',
                          color: '#ffffff',
                          padding: '0.12rem 0.35rem',
                          borderRadius: '4px',
                          letterSpacing: '0.4px',
                          flexShrink: 0
                        }}
                      >
                        {item.badge}
                      </span>
                    )}
                  </NavLink>
                );
              })}
            </div>
          ))}
        </nav>
      </aside>
    </>
  );
}
