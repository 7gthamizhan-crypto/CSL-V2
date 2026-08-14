import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Users, Box, Cpu, Plus, Trash2, Power, CheckCircle, XCircle, X, AlertTriangle } from 'lucide-react';

export function Resources() {
  const [officers, setOfficers] = useState([]);
  const [bays, setBays] = useState([]);
  const [scanners, setScanners] = useState([]);
  const [activeTab, setActiveTab] = useState('officers');
  const [isMobile, setIsMobile] = useState(typeof window !== 'undefined' ? window.innerWidth < 900 : false);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 900);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  const [showAddModal, setShowAddModal] = useState(false);

  // Custom Delete Confirmation Modal State
  const [deleteConfirm, setDeleteConfirm] = useState(null); // { type: 'officer'|'bay'|'scanner', id, name }

  // Form states
  const [officerForm, setOfficerForm] = useState({
    officer_code: `OFF${Math.floor(100 + Math.random() * 900)}`,
    officer_name: '',
    designation: 'Customs Officer',
    qualification: 'General',
    daily_capacity: 6,
    availability: true
  });

  const [bayForm, setBayForm] = useState({
    bay_name: `Bay B${Math.floor(10 + Math.random() * 90)}`,
    bay_type: 'Standard',
    capacity: 1,
    status: 'Available'
  });

  const [scannerForm, setScannerForm] = useState({
    scanner_name: `Scanner SC-${Math.floor(10 + Math.random() * 90)}`,
    location: 'Gate 01 Main Port Entrance',
    capacity: 20,
    availability: true
  });

  const loadAllData = () => {
    Promise.all([api.getOfficers(), api.getBays(), api.getScanners()])
      .then(([oData, bData, sData]) => {
        setOfficers(oData);
        setBays(bData);
        setScanners(sData);
      });
  };

  useEffect(() => {
    loadAllData();
  }, []);

  // Officer Actions
  const handleToggleOfficer = (id) => {
    api.toggleOfficerAvailability(id).then(() => loadAllData());
  };

  const executeDelete = () => {
    if (!deleteConfirm) return;
    const { type, id } = deleteConfirm;

    if (type === 'officer') {
      api.deleteOfficer(id).then(() => { setDeleteConfirm(null); loadAllData(); });
    } else if (type === 'bay') {
      api.deleteBay(id).then(() => { setDeleteConfirm(null); loadAllData(); });
    } else if (type === 'scanner') {
      api.deleteScanner(id).then(() => { setDeleteConfirm(null); loadAllData(); });
    }
  };

  const handleAddOfficerSubmit = (e) => {
    e.preventDefault();
    api.createOfficer(officerForm).then(() => {
      setShowAddModal(false);
      setOfficerForm({
        officer_code: `OFF${Math.floor(100 + Math.random() * 900)}`,
        officer_name: '',
        designation: 'Customs Officer',
        qualification: 'General',
        daily_capacity: 6,
        availability: true
      });
      loadAllData();
    });
  };

  // Bay Actions
  const handleToggleBay = (id) => {
    api.toggleBayStatus(id).then(() => loadAllData());
  };

  const handleAddBaySubmit = (e) => {
    e.preventDefault();
    api.createBay(bayForm).then(() => {
      setShowAddModal(false);
      setBayForm({
        bay_name: `Bay B${Math.floor(10 + Math.random() * 90)}`,
        bay_type: 'Standard',
        capacity: 1,
        status: 'Available'
      });
      loadAllData();
    });
  };

  // Scanner Actions
  const handleAddScannerSubmit = (e) => {
    e.preventDefault();
    api.createScanner(scannerForm).then(() => {
      setShowAddModal(false);
      setScannerForm({
        scanner_name: `Scanner SC-${Math.floor(10 + Math.random() * 90)}`,
        location: 'Gate 01 Main Port Entrance',
        capacity: 20,
        availability: true
      });
      loadAllData();
    });
  };

  return (
    <div>
      <div className="page-header">
        <div style={{ flex: 1, minWidth: 0 }}>
          <h1 className="page-title" style={{ marginBottom: "0.15rem", lineHeight: 1.2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {isMobile ? 'Resource Management' : 'Customs Operational Resource Management'}
          </h1>
          <span style={{ fontSize: isMobile ? '0.7rem' : '0.85rem', color: 'var(--text-muted)', display: 'block', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {isMobile ? 'Officers, Bays & Scanners' : 'Manage officers, examination bays, and gate scanners availability'}
          </span>
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => setShowAddModal(true)}
          style={{ fontSize: isMobile ? '0.725rem' : '0.825rem', padding: isMobile ? '0.35rem 0.65rem' : '0.5rem 1.05rem', whiteSpace: 'nowrap', flexShrink: 0 }}
        >
          <Plus size={isMobile ? 14 : 16} /> {isMobile ? 'Add' : 'Add New'} {activeTab === 'officers' ? 'Officer' : activeTab === 'bays' ? 'Bay' : 'Scanner'}
        </button>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
        <button type="button" className={`btn ${activeTab === 'officers' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab('officers')}>
          <Users size={16} /> Officers ({officers.length})
        </button>
        <button type="button" className={`btn ${activeTab === 'bays' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab('bays')}>
          <Box size={16} /> Examination Bays ({bays.length})
        </button>
        <button type="button" className={`btn ${activeTab === 'scanners' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab('scanners')}>
          <Cpu size={16} /> Scanners ({scanners.length})
        </button>
      </div>

      {/* OFFICERS TAB */}
      {activeTab === 'officers' && (
        <div className="table-container" style={{ padding: isMobile ? '0.75rem' : '0' }}>
          {isMobile ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
              {officers.map((o) => (
                <div key={o.officer_id} style={{ background: '#ffffff', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '0.75rem 0.85rem', boxShadow: 'var(--box-shadow)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <div>
                      <div style={{ fontWeight: 700, color: '#0a2540', fontSize: '0.85rem' }}>{o.officer_name}</div>
                      <div style={{ fontSize: '0.675rem', color: '#64748b' }}>{o.officer_code} • {o.designation}</div>
                    </div>
                    {o.availability ? (
                      <span className="badge badge-ready" style={{ fontSize: '0.65rem' }}>ON DUTY</span>
                    ) : (
                      <span className="badge badge-critical" style={{ fontSize: '0.65rem' }}>OFF DUTY</span>
                    )}
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.4rem', borderTop: '1px solid #f0f4f8' }}>
                    <span style={{ fontSize: '0.725rem', color: '#0066b2', fontWeight: 600 }}>{o.qualification} Qualification</span>
                    <div style={{ display: 'flex', gap: '0.4rem' }}>
                      <button type="button" className={`btn ${o.availability ? 'btn-secondary' : 'btn-primary'}`} style={{ padding: '0.2rem 0.5rem', fontSize: '0.7rem' }} onClick={() => handleToggleOfficer(o.officer_id)}>
                        <Power size={12} /> {o.availability ? 'Off Duty' : 'On Duty'}
                      </button>
                      <button type="button" className="btn btn-danger" style={{ padding: '0.2rem 0.4rem', fontSize: '0.7rem' }} onClick={() => setDeleteConfirm({ type: 'officer', id: o.officer_id, name: o.officer_name })}>
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <table className="data-table">
            <thead>
              <tr>
                <th>Officer Details</th>
                <th>Designation</th>
                <th>Specialized Qualification</th>
                <th>Daily Capacity</th>
                <th>Availability Status</th>
                <th style={{ textAlign: 'center' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {officers.map(o => (
                <tr key={o.officer_id}>
                  <td>
                    <div style={{ fontWeight: 600, color: '#0a2540', fontSize: '0.825rem' }}>{o.officer_name}</div>
                    <div style={{ fontSize: '0.675rem', color: '#70869d', marginTop: '0.05rem', fontWeight: 400 }}>{o.officer_code}</div>
                  </td>
                  <td style={{ color: '#4a607a', fontWeight: 400 }}>{o.designation}</td>
                  <td><span className="badge badge-scheduled">{o.qualification}</span></td>
                  <td style={{ fontWeight: 400 }}>{o.daily_capacity} exams/day</td>
                  <td>
                    {o.availability ? (
                      <span className="badge badge-completed" style={{ gap: '0.25rem' }}><CheckCircle size={13} /> Working / Available</span>
                    ) : (
                      <span className="badge badge-critical" style={{ gap: '0.25rem' }}><XCircle size={13} /> Absent / Not Working</span>
                    )}
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'center' }}>
                      <button
                        type="button"
                        className={`btn ${o.availability ? 'btn-secondary' : 'btn-primary'}`}
                        style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
                        onClick={() => handleToggleOfficer(o.officer_id)}
                      >
                        <Power size={13} /> {o.availability ? 'Mark Absent' : 'Mark Working'}
                      </button>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', color: '#b91c1c' }}
                        onClick={() => setDeleteConfirm({ type: 'officer', id: o.officer_id, name: o.officer_name })}
                      >
                        <Trash2 size={13} /> Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          )}
        </div>
      )}

      {/* BAYS TAB */}
      {activeTab === 'bays' && (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Bay Details</th>
                <th>Bay Type</th>
                <th>Capacity</th>
                <th>Operational Status</th>
                <th style={{ textAlign: 'center' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {bays.map(b => (
                <tr key={b.bay_id}>
                  <td>
                    <div style={{ fontWeight: 600, color: '#0a2540', fontSize: '0.825rem' }}>{b.bay_name}</div>
                    <div style={{ fontSize: '0.675rem', color: '#70869d', marginTop: '0.05rem', fontWeight: 400 }}>{b.bay_type} Containment</div>
                  </td>
                  <td><span className={`badge ${b.bay_type === 'Hazardous' ? 'badge-critical' : 'badge-ready'}`}>{b.bay_type}</span></td>
                  <td style={{ fontWeight: 400 }}>{b.capacity} container at a time</td>
                  <td>
                    {b.status === 'Available' ? (
                      <span className="badge badge-completed" style={{ gap: '0.25rem' }}><CheckCircle size={13} /> Available</span>
                    ) : (
                      <span className="badge badge-critical" style={{ gap: '0.25rem' }}><XCircle size={13} /> Maintenance / Closed</span>
                    )}
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'center' }}>
                      <button
                        type="button"
                        className={`btn ${b.status === 'Available' ? 'btn-secondary' : 'btn-primary'}`}
                        style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
                        onClick={() => handleToggleBay(b.bay_id)}
                      >
                        <Power size={13} /> {b.status === 'Available' ? 'Mark Maintenance' : 'Mark Available'}
                      </button>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', color: '#b91c1c' }}
                        onClick={() => setDeleteConfirm({ type: 'bay', id: b.bay_id, name: b.bay_name })}
                      >
                        <Trash2 size={13} /> Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* SCANNERS TAB */}
      {activeTab === 'scanners' && (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Scanner Details</th>
                <th>Location</th>
                <th>Daily Capacity</th>
                <th>Status</th>
                <th style={{ textAlign: 'center' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {scanners.map(s => (
                <tr key={s.scanner_id}>
                  <td>
                    <div style={{ fontWeight: 600, color: '#0a2540', fontSize: '0.825rem' }}>{s.scanner_name}</div>
                    <div style={{ fontSize: '0.675rem', color: '#70869d', marginTop: '0.05rem', fontWeight: 400 }}>{s.location}</div>
                  </td>
                  <td style={{ color: '#4a607a', fontWeight: 400 }}>{s.location}</td>
                  <td style={{ fontWeight: 400 }}>{s.capacity} scans/day</td>
                  <td>
                    <span className="badge badge-completed">Operational</span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', color: '#b91c1c' }}
                      onClick={() => setDeleteConfirm({ type: 'scanner', id: s.scanner_id, name: s.scanner_name })}
                    >
                      <Trash2 size={13} /> Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* CUSTOM EXECUTIVE DELETE CONFIRMATION POPUP MODAL */}
      {deleteConfirm && (
        <div
          style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(10, 37, 64, 0.45)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, cursor: 'pointer'
          }}
          onClick={() => setDeleteConfirm(null)}
        >
          <div
            style={{ background: '#ffffff', border: '1px solid var(--border-color)', color: '#0a2540', padding: '1.75rem', borderRadius: '14px', width: '90vw', maxWidth: '420px', cursor: 'default', position: 'relative', boxShadow: '0 16px 40px rgba(10, 83, 152, 0.22)' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '1rem' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: '#fee2e2', color: '#b91c1c', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <AlertTriangle size={20} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#0a2540' }}>Confirm Deletion</h3>
                <span style={{ fontSize: '0.75rem', color: '#4a607a', fontWeight: 400 }}>Customs Resource Management</span>
              </div>
            </div>

            <p style={{ fontSize: '0.85rem', color: '#4a607a', lineHeight: '1.45', marginBottom: '1.5rem' }}>
              Are you sure you want to remove <strong>{deleteConfirm.name}</strong> from operational resources? This action will update solver capacity calculations immediately.
            </p>

            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setDeleteConfirm(null)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn"
                style={{ background: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)', color: '#ffffff', boxShadow: '0 4px 12px rgba(220, 38, 38, 0.25)' }}
                onClick={executeDelete}
              >
                Yes, Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ADD RESOURCE MODAL */}
      {showAddModal && (
        <div
          style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(10, 37, 64, 0.45)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, cursor: 'pointer'
          }}
          onClick={() => setShowAddModal(false)}
        >
          <div
            style={{ background: '#ffffff', border: '1px solid var(--border-color)', color: '#0a2540', padding: '1.75rem', borderRadius: '14px', width: '90vw', maxWidth: '480px', maxHeight: '90vh', overflowY: 'auto', cursor: 'default', position: 'relative', boxShadow: '0 12px 40px rgba(10, 83, 152, 0.25)' }}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              onClick={() => setShowAddModal(false)}
              style={{
                position: 'absolute', top: '1.25rem', right: '1.25rem',
                background: '#f4f8fc', border: 'none', borderRadius: '50%', color: '#4a607a', width: '28px', height: '28px',
                display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer'
              }}
            >
              <X size={15} />
            </button>

            <h2 style={{ marginBottom: '1.25rem', color: '#0a2540', fontSize: '1.15rem', fontWeight: 600 }}>
              Add New {activeTab === 'officers' ? 'Customs Officer' : activeTab === 'bays' ? 'Examination Bay' : 'Scanner Machine'}
            </h2>

            {/* ADD OFFICER FORM */}
            {activeTab === 'officers' && (
              <form onSubmit={handleAddOfficerSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0a2540' }}>Officer Code</label>
                  <input
                    type="text"
                    required
                    className="input-field"
                    style={{ width: '100%', marginTop: '0.25rem' }}
                    value={officerForm.officer_code}
                    onChange={(e) => setOfficerForm({ ...officerForm, officer_code: e.target.value })}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0a2540' }}>Full Name *</label>
                  <input
                    type="text"
                    required
                    className="input-field"
                    style={{ width: '100%', marginTop: '0.25rem' }}
                    placeholder="e.g. Supt. Bandara K.M."
                    value={officerForm.officer_name}
                    onChange={(e) => setOfficerForm({ ...officerForm, officer_name: e.target.value })}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0a2540' }}>Designation</label>
                  <input
                    type="text"
                    className="input-field"
                    style={{ width: '100%', marginTop: '0.25rem' }}
                    value={officerForm.designation}
                    onChange={(e) => setOfficerForm({ ...officerForm, designation: e.target.value })}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0a2540' }}>Specialized Qualification</label>
                  <select
                    className="input-field"
                    style={{ width: '100%', marginTop: '0.25rem' }}
                    value={officerForm.qualification}
                    onChange={(e) => setOfficerForm({ ...officerForm, qualification: e.target.value })}
                  >
                    <option value="General">General (Standard Cargo Exams)</option>
                    <option value="Hazardous">Hazardous Cargo Specialist</option>
                    <option value="Complex">Complex Multi-Officer Inspector</option>
                    <option value="Scanner">Scanner Specialist</option>
                  </select>
                </div>

                <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.75rem' }}>
                  <button type="submit" className="btn btn-primary" style={{ flex: 1, justifyContent: 'center' }}>Save Officer</button>
                  <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>Cancel</button>
                </div>
              </form>
            )}

            {/* ADD BAY FORM */}
            {activeTab === 'bays' && (
              <form onSubmit={handleAddBaySubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0a2540' }}>Bay Name *</label>
                  <input
                    type="text"
                    required
                    className="input-field"
                    style={{ width: '100%', marginTop: '0.25rem' }}
                    placeholder="e.g. Examination Bay B05"
                    value={bayForm.bay_name}
                    onChange={(e) => setBayForm({ ...bayForm, bay_name: e.target.value })}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0a2540' }}>Bay Type</label>
                  <select
                    className="input-field"
                    style={{ width: '100%', marginTop: '0.25rem' }}
                    value={bayForm.bay_type}
                    onChange={(e) => setBayForm({ ...bayForm, bay_type: e.target.value })}
                  >
                    <option value="Standard">Standard Physical Bay</option>
                    <option value="Hazardous">Hazardous Containment Bay</option>
                  </select>
                </div>

                <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.75rem' }}>
                  <button type="submit" className="btn btn-primary" style={{ flex: 1, justifyContent: 'center' }}>Save Bay</button>
                  <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>Cancel</button>
                </div>
              </form>
            )}

            {/* ADD SCANNER FORM */}
            {activeTab === 'scanners' && (
              <form onSubmit={handleAddScannerSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0a2540' }}>Scanner Name *</label>
                  <input
                    type="text"
                    required
                    className="input-field"
                    style={{ width: '100%', marginTop: '0.25rem' }}
                    placeholder="e.g. Drive-Through NII Scanner SC-03"
                    value={scannerForm.scanner_name}
                    onChange={(e) => setScannerForm({ ...scannerForm, scanner_name: e.target.value })}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0a2540' }}>Location</label>
                  <input
                    type="text"
                    className="input-field"
                    style={{ width: '100%', marginTop: '0.25rem' }}
                    value={scannerForm.location}
                    onChange={(e) => setScannerForm({ ...scannerForm, location: e.target.value })}
                  />
                </div>

                <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.75rem' }}>
                  <button type="submit" className="btn btn-primary" style={{ flex: 1, justifyContent: 'center' }}>Save Scanner</button>
                  <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>Cancel</button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
