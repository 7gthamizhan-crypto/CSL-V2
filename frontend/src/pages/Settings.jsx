import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Save, CheckCircle, Clock, Timer, ShieldAlert, AlertOctagon, Box, Sliders } from 'lucide-react';

export function Settings() {
  const [settings, setSettings] = useState([]);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isMobile, setIsMobile] = useState(typeof window !== 'undefined' ? window.innerWidth < 900 : false);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 900);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const loadSettings = () => {
    api.getSettings().then(data => setSettings(data));
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleInputChange = (id, newValue) => {
    setSettings(prev => prev.map(s => s.setting_id === id ? { ...s, setting_value: newValue } : s));
  };

  const handleSave = () => {
    setSaving(true);
    setSaveSuccess(false);

    const updatePromises = settings.map(s =>
      api.updateSetting(s.setting_id, { setting_value: String(s.setting_value) })
    );

    Promise.all(updatePromises)
      .then(() => {
        setSaving(false);
        setSaveSuccess(true);
        loadSettings();
        setTimeout(() => setSaveSuccess(false), 4000);
      })
      .catch(err => {
        setSaving(false);
        alert("Error saving settings: " + (err.response?.data?.detail || err.message));
      });
  };

  const shiftSettings = settings.filter(s => s.setting_name.includes('Working Hours'));
  const examDurationSettings = settings.filter(s => !s.setting_name.includes('Working Hours'));

  const getIconForSetting = (name) => {
    if (name.includes('Working Hours')) return Clock;
    if (name.includes('Scanner')) return Timer;
    if (name.includes('Standard')) return Box;
    if (name.includes('High Risk')) return ShieldAlert;
    if (name.includes('Hazardous')) return AlertOctagon;
    if (name.includes('Complex')) return Sliders;
    return Timer;
  };

  return (
    <div style={{ padding: '1rem', maxWidth: '1600px', margin: '0 auto' }}>
      <div className="page-header" style={{ marginBottom: '1.25rem' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h1 className="page-title" style={{ marginBottom: "0.15rem", lineHeight: 1.2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {isMobile ? 'System Settings' : 'System Settings & Configurations'}
          </h1>
          <span style={{ fontSize: isMobile ? '0.7rem' : '0.85rem', color: 'var(--text-muted)', display: 'block', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {isMobile ? 'Algorithm Weights' : 'Configure Customs operational constraints & solver limits'}
          </span>
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleSave}
          disabled={saving}
          style={{ fontSize: isMobile ? '0.725rem' : '0.825rem', padding: isMobile ? '0.35rem 0.65rem' : '0.5rem 1.05rem', whiteSpace: 'nowrap', flexShrink: 0 }}
        >
          <Save size={isMobile ? 14 : 15} /> {saving ? 'Saving...' : isMobile ? 'Save' : 'Save Changes'}
        </button>
      </div>

      {/* FLOATING SUCCESS TOAST */}
      {saveSuccess && (
        <div style={{ background: '#d1fae5', border: '1px solid #a7f3d0', color: '#047857', padding: '0.85rem 1.15rem', borderRadius: '10px', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.65rem', fontWeight: 600, fontSize: '0.85rem', boxShadow: '0 4px 14px rgba(5, 150, 105, 0.15)' }}>
          <CheckCircle size={18} /> System operational parameters updated and saved to CORE Optimizer Engine!
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '1.25rem' }}>
        {/* SHIFT & OPERATIONAL TIMINGS CARD */}
        <div className="card" style={{ padding: '1.35rem', height: 'fit-content' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '1.25rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.85rem' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '8px', background: '#e0f2fe', color: '#0066b2', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Clock size={20} />
            </div>
            <div>
              <h3 style={{ fontSize: '0.95rem', color: '#0a2540', fontWeight: 700, margin: 0 }}>Shift & Operational Hours</h3>
              <span style={{ fontSize: '0.725rem', color: '#64748b', fontWeight: 400 }}>Daily inspection port shift boundaries</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {shiftSettings.map((s) => {
              const Icon = getIconForSetting(s.setting_name);
              return (
                <div key={s.setting_id} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', padding: '0.95rem 1.15rem', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ color: '#0066b2', background: '#ffffff', padding: '0.4rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                      <Icon size={18} />
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, color: '#0a2540', fontSize: '0.85rem' }}>{s.setting_name}</div>
                      <div style={{ fontSize: '0.725rem', color: '#64748b', marginTop: '0.05rem', fontWeight: 400 }}>{s.description}</div>
                    </div>
                  </div>

                  <input
                    type="text"
                    className="input-field"
                    value={s.setting_value}
                    onChange={(e) => handleInputChange(s.setting_id, e.target.value)}
                    style={{ width: '135px', fontWeight: 700, color: '#0066b2', textAlign: 'center', fontSize: '0.85rem', boxShadow: '0 2px 6px rgba(0, 102, 178, 0.08)' }}
                  />
                </div>
              );
            })}
          </div>
        </div>

        {/* EXAMINATION DURATION CONSTRAINTS CARD */}
        <div className="card" style={{ padding: '1.35rem', height: 'fit-content' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '1.25rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.85rem' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '8px', background: '#e0f2fe', color: '#0066b2', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Timer size={20} />
            </div>
            <div>
              <h3 style={{ fontSize: '0.95rem', color: '#0a2540', fontWeight: 700, margin: 0 }}>Inspection Category Durations</h3>
              <span style={{ fontSize: '0.725rem', color: '#64748b', fontWeight: 400 }}>Solver examination duration constraints in minutes</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {examDurationSettings.map((s) => {
              const Icon = getIconForSetting(s.setting_name);
              return (
                <div key={s.setting_id} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', padding: '0.85rem 1.15rem', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ color: '#0066b2', background: '#ffffff', padding: '0.4rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                      <Icon size={17} />
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, color: '#0a2540', fontSize: '0.825rem' }}>{s.setting_name}</div>
                      <div style={{ fontSize: '0.725rem', color: '#64748b', marginTop: '0.05rem', fontWeight: 400 }}>{s.description}</div>
                    </div>
                  </div>

                  <div 
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      background: '#ffffff',
                      border: '1px solid #cbd5e1',
                      borderRadius: '8px',
                      overflow: 'hidden',
                      boxShadow: '0 2px 6px rgba(0, 102, 178, 0.08)'
                    }}
                  >
                    <input
                      type="text"
                      value={s.setting_value}
                      onChange={(e) => handleInputChange(s.setting_id, e.target.value)}
                      style={{
                        width: '65px',
                        border: 'none',
                        outline: 'none',
                        padding: '0.45rem 0.5rem',
                        fontSize: '0.85rem',
                        fontWeight: 700,
                        color: '#0066b2',
                        textAlign: 'center',
                        background: 'transparent'
                      }}
                    />
                    <span 
                      style={{
                        background: '#f1f5f9',
                        color: '#64748b',
                        padding: '0.45rem 0.65rem',
                        fontSize: '0.725rem',
                        fontWeight: 600,
                        borderLeft: '1px solid #e2e8f0'
                      }}
                    >
                      mins
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
