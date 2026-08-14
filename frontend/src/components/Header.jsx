import React from 'react';
import { ShieldCheck, Menu, Calendar, Bell } from 'lucide-react';

export function Header({ toggleMobileSidebar }) {
  return (
    <header className="header-bar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', minWidth: 0 }}>
        <button className="mobile-toggle-btn" onClick={toggleMobileSidebar} title="Toggle Menu">
          <Menu size={20} />
        </button>

        <div className="header-title" style={{ minWidth: 0 }}>
          <ShieldCheck size={20} color="#0066b2" style={{ flexShrink: 0 }} />
          <span className="header-title-full">Customs Operational Roster Engine</span>
          <span className="header-title-mobile">CORE Engine</span>
        </div>
      </div>

      <div className="header-right" style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
        <span className="header-date-badge">
          <Calendar size={14} color="#0066b2" />
          <span className="header-date-text">Thu, 30 Jul 2026</span>
        </span>
        
        <button
          style={{ background: 'transparent', border: 'none', color: '#4a607a', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
          title="Notifications"
        >
          <Bell size={16} />
        </button>
      </div>
    </header>
  );
}
