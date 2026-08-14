import React, { useEffect, useState, useRef } from 'react';
import { api } from '../services/api';
import { Search, Plus, Eye, X, SlidersHorizontal, ShieldAlert, RotateCcw, ChevronDown, Check, Trash2, AlertTriangle } from 'lucide-react';
import { ContainerIntelligenceDrawer } from '../components/ContainerIntelligenceDrawer';

function CustomSelect({ icon: Icon, value, options, onChange, placeholder }) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectedOption = options.find(o => o.value === value) || options[0];

  return (
    <div className="custom-dropdown-container" ref={containerRef}>
      <div 
        className={`custom-dropdown-trigger ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        {Icon && <Icon size={14} color="#0066b2" />}
        <span>{selectedOption ? selectedOption.label : placeholder}</span>
        <ChevronDown size={14} color="#4a607a" style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s ease' }} />
      </div>

      {isOpen && (
        <div className="custom-dropdown-menu">
          {options.map((opt) => (
            <div
              key={opt.value}
              className={`custom-dropdown-item ${value === opt.value ? 'active' : ''}`}
              onClick={(e) => {
                e.stopPropagation();
                onChange(opt.value);
                setIsOpen(false);
              }}
            >
              <span>{opt.label}</span>
              {value === opt.value && <Check size={14} color="#ffffff" />}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function ContainerQueue() {
  const [containers, setContainers] = useState([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedContainerId, setSelectedContainerId] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(typeof window !== 'undefined' ? window.innerWidth < 900 : false);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 900);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const generateNewFormState = () => ({
    container_number: `MSCU${Math.floor(1000000 + Math.random() * 9000000)}`,
    cusdec_number: `CUS2026/COL/${Math.floor(10000 + Math.random() * 90000)}`,
    country_of_origin: 'China',
    hs_code: '870323',
    goods_description: 'Commercial Electronics and Automotive Cargo',
    cif_value: 48000,
    duty_amount: 14000,
    examination_type: 'Standard'
  });

  const [formData, setFormData] = useState(generateNewFormState());

  const fetchContainers = () => {
    setLoading(true);
    api.getContainers({ search, status: statusFilter, risk_level: riskFilter })
      .then(data => {
        setContainers(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Containers fetch error:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchContainers();
  }, [search, statusFilter, riskFilter]);

  const handleOpenAddModal = () => {
    setFormData(generateNewFormState());
    setShowAddModal(true);
  };

  const handleResetFilters = () => {
    setSearch('');
    setStatusFilter('');
    setRiskFilter('');
  };

  const handleAddSubmit = (e) => {
    e.preventDefault();
    api.createContainer({
      ...formData,
      cif_value: parseFloat(formData.cif_value || 0),
      duty_amount: parseFloat(formData.duty_amount || 0)
    })
      .then(() => {
        setShowAddModal(false);
        setFormData(generateNewFormState());
        fetchContainers();
      })
      .catch(err => {
        alert("Error adding container: " + (err.response?.data?.detail || err.message));
      });
  };

  const activeFilterCount = (search ? 1 : 0) + (statusFilter ? 1 : 0) + (riskFilter ? 1 : 0);

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'Pending', label: 'Pending' },
    { value: 'Ready', label: 'Ready' },
    { value: 'Scheduled', label: 'Scheduled' },
    { value: 'Completed', label: 'Completed' }
  ];

  const riskOptions = [
    { value: '', label: 'All Risk Levels' },
    { value: 'Low', label: 'Low Risk' },
    { value: 'Medium', label: 'Medium Risk' },
    { value: 'High', label: 'High Risk' },
    { value: 'Critical', label: 'Critical Risk' }
  ];

  return (
    <div>
      <div className="page-header">
        <div style={{ flex: 1, minWidth: 0 }}>
          <h1 className="page-title" style={{ marginBottom: "0.15rem", lineHeight: 1.2 }}>
            {isMobile ? 'Container Queue' : 'Container Queue & Inspection Intake'}
          </h1>
          <span style={{ fontSize: isMobile ? '0.7rem' : '0.85rem', color: 'var(--text-muted)' }}>
            Real-time container intake inventory and 360° intelligence audit
          </span>
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleOpenAddModal}
          style={{ fontSize: isMobile ? '0.725rem' : '0.825rem', padding: isMobile ? '0.35rem 0.65rem' : '0.5rem 1.05rem' }}
        >
          <Plus size={isMobile ? 14 : 16} /> {isMobile ? 'Container' : 'Add Container'}
        </button>
      </div>

      {/* FILTER & SEARCH BAR */}
      <div className="filter-bar">
        <div className="search-input-wrapper">
          <Search size={16} color="#0066b2" />
          <input
            type="text"
            className="search-input-field"
            placeholder="Search by Container No, CusDec No, Goods..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button
              type="button"
              onClick={() => setSearch('')}
              style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
            >
              <X size={14} />
            </button>
          )}
        </div>

        <CustomSelect
          icon={SlidersHorizontal}
          value={statusFilter}
          options={statusOptions}
          onChange={(val) => setStatusFilter(val)}
          placeholder="All Statuses"
        />

        <CustomSelect
          icon={ShieldAlert}
          value={riskFilter}
          options={riskOptions}
          onChange={(val) => setRiskFilter(val)}
          placeholder="All Risk Levels"
        />

        {activeFilterCount > 0 && (
          <button type="button" className="btn btn-secondary" onClick={handleResetFilters} style={{ fontSize: '0.775rem' }}>
            <RotateCcw size={13} /> Reset Filters ({activeFilterCount})
          </button>
        )}
      </div>

      {/* Table */}
      <div className="table-container" style={{ padding: isMobile ? '0.75rem' : '0' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th className="text-left">Container & CusDec No</th>
              <th className="text-left">Country</th>
              <th className="text-center">HS Code</th>
              <th className="text-right">Cargo Value (USD)</th>
              <th className="text-left">Exam Category</th>
              <th className="text-center">Risk Level</th>
              <th className="text-center">Status</th>
              <th className="text-center">360° Audit Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="8" className="text-center" style={{ padding: '2rem', color: 'var(--text-muted)' }}>Loading container queue...</td></tr>
            ) : containers.length === 0 ? (
              <tr><td colSpan="8" className="text-center" style={{ padding: '2rem', color: 'var(--text-muted)' }}>No containers found matching filter.</td></tr>
            ) : (
              containers.map((c) => {
                const riskLvl = c.risk_assessment?.risk_level || 'Low';
                const riskBadgeClass = `badge badge-${riskLvl.toLowerCase()}`;
                const statusBadgeClass = `badge badge-${c.status.toLowerCase()}`;

                return (
                  <tr key={c.container_id}>
                    <td className="text-left">
                      <div style={{ fontWeight: 600, color: '#0066b2', fontSize: '0.8rem' }}>{c.container_number}</div>
                      <div style={{ fontSize: '0.675rem', color: '#64748b', fontWeight: 400 }}>{c.cusdec_number}</div>
                    </td>
                    <td className="text-left" style={{ fontWeight: 500 }}>{c.country_of_origin}</td>
                    <td className="text-center"><code style={{ background: '#f8fafc', color: '#0a2540', padding: '0.15rem 0.4rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}>{c.hs_code}</code></td>
                    <td className="text-right" style={{ fontWeight: 600, color: '#10b981' }}>${c.cif_value?.toLocaleString()}</td>
                    <td className="text-left" style={{ fontWeight: 500 }}>{c.examination_type}</td>
                    <td className="text-center"><span className={riskBadgeClass}>{riskLvl} ({c.risk_assessment?.risk_score || 0})</span></td>
                    <td className="text-center"><span className={statusBadgeClass}>{c.status}</span></td>
                    <td className="text-center">
                      <button
                        type="button"
                        className="btn btn-secondary"
                        style={{ padding: '0.3rem 0.75rem', fontSize: '0.75rem', fontWeight: 600, backgroundColor: '#0066b2', color: '#fff', border: 'none' }}
                        onClick={() => { setSelectedContainerId(c.container_id); setDrawerOpen(true); }}
                      >
                        <Eye size={13} /> 360° Intelligence Drawer
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Shared Container Intelligence Drawer */}
      <ContainerIntelligenceDrawer
        containerId={selectedContainerId}
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </div>
  );
}
