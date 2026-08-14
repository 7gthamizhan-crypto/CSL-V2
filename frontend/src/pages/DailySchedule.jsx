import React, { useEffect, useState, useRef } from 'react';
import { api } from '../services/api';
import { Zap, RotateCcw, BarChart2, Table, Box, HelpCircle, CheckCircle, Eye, X, Calendar, Printer, ChevronDown, Check, Smartphone, Monitor, ChevronRight } from 'lucide-react';
import { ContainerIntelligenceDrawer } from '../components/ContainerIntelligenceDrawer';
import { ConfirmResetModal } from '../components/ConfirmResetModal';

function DateSelectDropdown({ uniqueDates, activeDate, schedules, onSelectDate }) {
  const [isMobile, setIsMobile] = useState(typeof window !== 'undefined' ? window.innerWidth < 900 : false);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 900);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
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

  const activeCount = schedules.filter(s => s.start_time && s.start_time.split('T')[0] === activeDate).length;

  const formatDateLabel = (dateStr) => {
    if (!dateStr) return 'Select Date';
    const [y, m, d] = dateStr.split('-');
    const dateObj = new Date(parseInt(y), parseInt(m) - 1, parseInt(d));
    const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
    const monthName = dateObj.toLocaleDateString('en-US', { month: 'short' });
    return `${dayName}, ${d} ${monthName} ${y}`;
  };

  if (isMobile) {
    return (
      <div style={{ position: 'relative', width: '100%' }}>
        <select
          value={activeDate}
          onChange={(e) => onSelectDate(e.target.value)}
          style={{
            width: '100%',
            background: '#ffffff',
            border: '1px solid #0066b2',
            borderRadius: '8px',
            padding: '0.45rem 2rem 0.45rem 0.85rem',
            fontSize: '0.8rem',
            fontWeight: 600,
            color: '#0066b2',
            appearance: 'none',
            WebkitAppearance: 'none',
            cursor: 'pointer',
            boxShadow: '0 2px 8px rgba(0, 102, 178, 0.12)'
          }}
        >
          {uniqueDates.map((dateStr) => {
            const [y, m, d] = dateStr.split('-');
            const dateObj = new Date(parseInt(y), parseInt(m) - 1, parseInt(d));
            const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
            const monthName = dateObj.toLocaleDateString('en-US', { month: 'short' });
            const count = schedules.filter(s => s.start_time && s.start_time.split('T')[0] === dateStr).length;
            return (
              <option key={dateStr} value={dateStr}>
                {dayName}, {d} {monthName} {y} ({count} Containers)
              </option>
            );
          })}
        </select>
        <ChevronDown size={14} color="#0066b2" style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }} />
      </div>
    );
  }

  return (
    <div ref={containerRef} style={{ position: 'relative', display: 'inline-block' }}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          background: '#ffffff',
          border: '1px solid #0066b2',
          borderRadius: '8px',
          padding: '0.4rem 0.85rem',
          fontSize: '0.8rem',
          fontWeight: 600,
          color: '#0066b2',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '0.55rem',
          boxShadow: '0 2px 8px rgba(0, 102, 178, 0.12)',
          transition: 'all 0.2s ease'
        }}
      >
        <Calendar size={15} color="#0066b2" />
        <span>{formatDateLabel(activeDate)}</span>
        <span
          style={{
            background: '#eef6fc',
            color: '#0066b2',
            padding: '0.1rem 0.45rem',
            borderRadius: '999px',
            fontSize: '0.675rem',
            fontWeight: 700
          }}
        >
          {activeCount} Containers
        </span>
        <ChevronDown size={14} color="#0066b2" style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s ease' }} />
      </button>

      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: 'calc(100% + 6px)',
            left: 0,
            minWidth: '260px',
            maxHeight: '320px',
            overflowY: 'auto',
            background: '#ffffff',
            border: '1px solid var(--border-color)',
            borderRadius: '10px',
            boxShadow: '0 12px 30px rgba(10, 83, 152, 0.2)',
            padding: '0.4rem',
            zIndex: 9999,
            display: 'flex',
            flexDirection: 'column',
            gap: '0.2rem'
          }}
        >
          <div style={{ padding: '0.4rem 0.6rem', fontSize: '0.7rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.4px', borderBottom: '1px solid #e2eef7', marginBottom: '0.2rem' }}>
            Operational Schedule Dates ({uniqueDates.length} Days)
          </div>

          {uniqueDates.map((dateStr) => {
            const countForDate = schedules.filter(s => s.start_time && s.start_time.split('T')[0] === dateStr).length;
            const isSelected = activeDate === dateStr;

            return (
              <div
                key={dateStr}
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectDate(dateStr);
                  setIsOpen(false);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.45rem 0.65rem',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.775rem',
                  fontWeight: isSelected ? 600 : 400,
                  background: isSelected ? '#0066b2' : 'transparent',
                  color: isSelected ? '#ffffff' : '#0a2540',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span>{formatDateLabel(dateStr)}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span
                    style={{
                      background: isSelected ? 'rgba(255,255,255,0.25)' : '#eef6fc',
                      color: isSelected ? '#ffffff' : '#0066b2',
                      padding: '0.1rem 0.4rem',
                      borderRadius: '999px',
                      fontSize: '0.65rem',
                      fontWeight: 600
                    }}
                  >
                    {countForDate}
                  </span>
                  {isSelected && <Check size={14} color="#ffffff" />}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export function DailySchedule() {
  const [schedules, setSchedules] = useState([]);
  const [optimizing, setOptimizing] = useState(false);
  const [optResult, setOptResult] = useState(null);
  const [resetMessage, setResetMessage] = useState('');
  const [viewMode, setViewMode] = useState('gantt_officer'); // gantt_officer, gantt_bay, table
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedItem, setSelectedItem] = useState(null);
  const [showLegendModal, setShowLegendModal] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [resetModalOpen, setResetModalOpen] = useState(false);
  const [resettingData, setResettingData] = useState(false);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const loadSchedule = () => {
    api.getSchedules()
      .then(data => {
        setSchedules(data);
        if (data.length > 0) {
          const dates = Array.from(new Set(data.map(s => s.start_time.split('T')[0]))).sort();
          if (dates.length > 0 && !selectedDate) {
            setSelectedDate(dates[0]);
          }
        }
      })
      .catch(err => console.error("Schedule load error:", err));
  };

  useEffect(() => {
    loadSchedule();
  }, []);

  const handleRunOptimizer = () => {
    setOptimizing(true);
    setOptResult(null);
    setResetMessage('');
    api.generateSchedule()
      .then(res => {
        setOptimizing(false);
        setOptResult(res);
        loadSchedule();
      })
      .catch(err => {
        setOptimizing(false);
        console.error("Optimization error:", err);
      });
  };

  const handleConfirmResetSchedule = async () => {
    setResettingData(true);
    try {
      const res = await api.resetSchedule();
      setOptResult(null);
      setResetMessage(res.message || "All containers reset to Ready for demo!");
      setSelectedDate('');
      setResetModalOpen(false);
      loadSchedule();
    } catch (err) {
      console.error("Reset error:", err);
    } finally {
      setResettingData(false);
    }
  };

  const uniqueDates = Array.from(new Set(schedules.map(s => s.start_time ? s.start_time.split('T')[0] : '2026-07-30'))).sort();
  const activeDate = selectedDate || (uniqueDates.length > 0 ? uniqueDates[0] : '');

  const filteredSchedules = schedules.filter(s => {
    if (!s.start_time) return true;
    return s.start_time.split('T')[0] === activeDate;
  });

  const timeToMinutes = (timeStr) => {
    if (!timeStr) return 0;
    const timePart = timeStr.includes('T') ? timeStr.split('T')[1].slice(0, 5) : timeStr;
    const [h, m] = timePart.split(':').map(Number);
    return (h - 8) * 60 + m;
  };

  const getGanttLanes = (groupBy) => {
    const lanes = {};
    filteredSchedules.forEach((s, index) => {
      const key = groupBy === 'officer' ? s.officer_name : s.bay_name;
      if (!lanes[key]) lanes[key] = [];
      
      const startMins = timeToMinutes(s.start_time);
      const endMins = timeToMinutes(s.end_time);
      const durationMins = Math.max(15, endMins - startMins);

      lanes[key].push({
        ...s,
        itemIndex: index + 1,
        startMins,
        endMins,
        durationMins,
        leftPct: (startMins / 540) * 100,
        widthPct: (durationMins / 540) * 100,
        startTimeFormatted: s.start_time ? (s.start_time.includes('T') ? s.start_time.split('T')[1].slice(0, 5) : s.start_time) : '08:00',
        endTimeFormatted: s.end_time ? (s.end_time.includes('T') ? s.end_time.split('T')[1].slice(0, 5) : s.end_time) : '08:45'
      });
    });
    return lanes;
  };

  const timeTicks = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'];
  const currentLanes = viewMode.startsWith('gantt') ? getGanttLanes(viewMode === 'gantt_officer' ? 'officer' : 'bay') : {};

  const formatDateDisplay = (dateStr) => {
    if (!dateStr) return 'Thursday, 30 July 2026';
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  };

  return (
    <div>
      {/* PAGE HEADER WITH HERO ACTION BUTTONS */}
      <div className="page-header" style={{ marginBottom: '0.75rem' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h1 className="page-title" style={{ marginBottom: "0.15rem", lineHeight: 1.2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {isMobile ? 'Inspection Schedule' : 'Daily Optimized Examination Schedule'}
          </h1>
          <span style={{ fontSize: isMobile ? '0.7rem' : '0.775rem', color: 'var(--text-muted)', display: 'block', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {isMobile ? 'Daily Slot Roster' : 'Multi-day schedule planner & interactive Gantt matrix'}
          </span>
        </div>

        {/* ACTION BUTTONS WITH DISTINCT PRIORITY COLORS */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', flexWrap: 'wrap' }}>
          <button
            type="button"
            className="btn btn-secondary"
            style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem', color: '#047857', border: '1px solid #a7f3d0', background: '#f0fdf4' }}
            onClick={() => window.open('/api/v1/reports/pdf/download', '_blank')}
          >
            <Printer size={13} color="#047857" /> Export PDF
          </button>
          
          <button
            type="button"
            className="btn btn-secondary"
            style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem', color: '#b45309', border: '1px solid #fde68a', background: '#fffbeb' }}
            onClick={() => setResetModalOpen(true)}
          >
            <RotateCcw size={13} color="#b45309" /> Reset Data
          </button>

          <button
            type="button"
            className="btn btn-primary"
            style={{ padding: '0.45rem 0.95rem', fontSize: '0.8rem', fontWeight: 600 }}
            onClick={handleRunOptimizer}
            disabled={optimizing}
          >
            <Zap size={14} /> {optimizing ? 'Executing...' : 'Generate Schedule'}
          </button>
        </div>
      </div>

      {/* MOBILE DESKTOP NOTIFICATION BANNER */}
      {isMobile && (
        <div
          style={{
            background: 'linear-gradient(135deg, #eef6fc 0%, #e0f2fe 100%)',
            border: '1px solid #bae6fd',
            borderRadius: '10px',
            padding: '0.75rem 1rem',
            marginBottom: '1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            boxShadow: '0 4px 12px rgba(0, 102, 178, 0.08)'
          }}
        >
          <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: '#0066b2', color: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <Smartphone size={20} />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '0.825rem', fontWeight: 700, color: '#0a2540', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <span>Mobile Schedule Summary Active</span>
            </div>
            <div style={{ fontSize: '0.725rem', color: '#4a607a', marginTop: '0.1rem', lineHeight: '1.3' }}>
              Viewing simplified mobile daily roster. For full interactive Gantt lane matrix, view on <strong>Desktop</strong> mode.
            </div>
          </div>
        </div>
      )}

      {resetMessage && (
        <div style={{ background: '#e0f2fe', border: '1px solid #bae6fd', color: '#0369a1', padding: '0.5rem 0.85rem', borderRadius: '8px', marginBottom: '0.75rem', fontSize: '0.8rem', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <RotateCcw size={14} /> {resetMessage}
        </div>
      )}

      {optResult && (
        <div style={{ background: '#d1fae5', border: '1px solid #a7f3d0', color: '#047857', padding: '0.5rem 0.85rem', borderRadius: '8px', marginBottom: '0.75rem', fontSize: '0.8rem', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <CheckCircle size={14} /> Scheduled <strong>{optResult.scheduled_count}</strong> containers across <strong>{optResult.total_days} days</strong>!
        </div>
      )}

      {/* COMPACT TOOLBAR BAR */}
      <div
        style={{
          background: '#ffffff',
          border: '1px solid var(--border-color)',
          borderRadius: '10px',
          padding: '0.4rem 0.65rem',
          marginBottom: '0.85rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.5rem',
          boxShadow: 'var(--box-shadow)'
        }}
      >
        {/* Left: Custom Executive Date Selector Dropdown */}
        <DateSelectDropdown
          uniqueDates={uniqueDates}
          activeDate={activeDate}
          schedules={schedules}
          onSelectDate={(d) => setSelectedDate(d)}
        />

        {/* Right: View Switcher & Legend */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', gap: '0.25rem', background: '#f4f8fc', padding: '0.2rem', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
            <button
              type="button"
              onClick={() => setViewMode('gantt_officer')}
              style={{
                background: viewMode === 'gantt_officer' ? '#ffffff' : 'transparent',
                color: viewMode === 'gantt_officer' ? '#0066b2' : '#4a607a',
                border: viewMode === 'gantt_officer' ? '1px solid #0066b2' : 'none',
                borderRadius: '5px',
                padding: '0.25rem 0.6rem',
                fontSize: '0.75rem',
                fontWeight: viewMode === 'gantt_officer' ? 600 : 400,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem'
              }}
            >
              <BarChart2 size={13} /> Officer Lanes
            </button>

            <button
              type="button"
              onClick={() => setViewMode('gantt_bay')}
              style={{
                background: viewMode === 'gantt_bay' ? '#ffffff' : 'transparent',
                color: viewMode === 'gantt_bay' ? '#0066b2' : '#4a607a',
                border: viewMode === 'gantt_bay' ? '1px solid #0066b2' : 'none',
                borderRadius: '5px',
                padding: '0.25rem 0.6rem',
                fontSize: '0.75rem',
                fontWeight: viewMode === 'gantt_bay' ? 600 : 400,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem'
              }}
            >
              <Box size={13} /> Bay Lanes
            </button>

            <button
              type="button"
              onClick={() => setViewMode('table')}
              style={{
                background: viewMode === 'table' ? '#ffffff' : 'transparent',
                color: viewMode === 'table' ? '#0066b2' : '#4a607a',
                border: viewMode === 'table' ? '1px solid #0066b2' : 'none',
                borderRadius: '5px',
                padding: '0.25rem 0.6rem',
                fontSize: '0.75rem',
                fontWeight: viewMode === 'table' ? 600 : 400,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem'
              }}
            >
              <Table size={13} /> Table View
            </button>
          </div>

          <button
            type="button"
            onClick={() => setShowLegendModal(true)}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#0066b2',
              fontSize: '0.75rem',
              fontWeight: 500,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.25rem',
              padding: '0.2rem 0.4rem'
            }}
          >
            <HelpCircle size={14} color="#0066b2" /> Legend
          </button>
        </div>
      </div>

      {/* SIMPLIFIED MOBILE SUMMARY CARDS (MOBILE SCREEN RENDER) */}
      {isMobile && viewMode.startsWith('gantt') ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
          {Object.keys(currentLanes).length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', background: '#ffffff', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              No scheduled containers found for {formatDateDisplay(activeDate)}.
            </div>
          ) : (
            Object.entries(currentLanes).map(([laneName, items]) => (
              <div key={laneName} style={{ background: '#ffffff', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '0.85rem', boxShadow: 'var(--box-shadow)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem', paddingBottom: '0.4rem', borderBottom: '1px solid #eef4f9' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#0a2540' }}>{laneName}</span>
                  <span style={{ fontSize: '0.7rem', color: '#0066b2', background: '#eef6fc', padding: '0.15rem 0.5rem', borderRadius: '999px', fontWeight: 600 }}>
                    {items.length} Exam Slots
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
                  {items.map((item) => {
                    const rLvl = (item.risk_level || 'low').toLowerCase();
                    const badgeClass = `badge badge-${rLvl}`;

                    return (
                      <div
                        key={item.schedule_id || item.container_number}
                        onClick={() => setSelectedItem(item)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          background: '#f4f8fc',
                          border: '1px solid #d8e6f2',
                          padding: '0.45rem 0.65rem',
                          borderRadius: '6px',
                          cursor: 'pointer'
                        }}
                      >
                        <div>
                          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0a2540' }}>
                            Container #{item.container_number}
                          </div>
                          <div style={{ fontSize: '0.7rem', color: '#4a607a', marginTop: '0.05rem' }}>
                            ⏱️ {item.startTimeFormatted} - {item.endTimeFormatted} ({item.duration_minutes || 45}m)
                          </div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                          <span className={badgeClass}>{rLvl}</span>
                          <ChevronRight size={14} color="#64748b" />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))
          )}
        </div>
      ) : viewMode.startsWith('gantt') ? (
        /* FULL DESKTOP GANTT MATRIX RENDER */
        <div className="gantt-container" style={{ padding: '0.85rem' }}>
          <div className="gantt-inner-wrapper">
            <div className="gantt-header-timeline">
              <div className="gantt-lane-label-header">
                {viewMode === 'gantt_officer' ? 'CUSTOMS OFFICER' : 'INSPECTION BAY'}
              </div>
              <div className="gantt-ticks-container">
                {timeTicks.map((t, idx) => (
                  <div
                    key={t}
                    style={{
                      position: 'absolute',
                      left: `${(idx / 9) * 100}%`,
                      transform: idx === 9 ? 'translateX(-100%)' : idx > 0 ? 'translateX(-50%)' : 'none',
                      fontSize: '0.725rem',
                      fontWeight: 600,
                      color: '#64748b',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {t}
                  </div>
                ))}
              </div>
            </div>

            {Object.keys(currentLanes).length === 0 ? (
              <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                No scheduled containers found for {formatDateDisplay(activeDate)}. Click <strong>"Generate Schedule"</strong> to run the optimizer.
              </div>
            ) : (
              Object.entries(currentLanes).map(([laneName, items]) => (
                <div className="gantt-row" key={laneName}>
                  <div className="gantt-lane-label" title={laneName}>{laneName}</div>
                  <div className="gantt-track">
                    {items.map((item) => {
                      const rLvl = (item.risk_level || 'low').toLowerCase();
                      const barClass = `gantt-bar gantt-bar-${rLvl}`;

                      return (
                        <div
                          key={item.schedule_id || item.container_number}
                          className={barClass}
                          style={{
                            left: `${item.leftPct}%`,
                            width: `${Math.max(3.5, item.widthPct)}%`
                          }}
                          onClick={() => setSelectedItem(item)}
                          title={`Container #${item.container_number} | ${item.examination_type} | ${item.startTimeFormatted} - ${item.endTimeFormatted}`}
                        >
                          {item.widthPct > 6 ? item.container_number : `#${item.container_number.slice(-3)}`}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      ) : (
        /* TABLE VIEW RENDER */
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Container & CusDec No</th>
                <th>Assigned Officer</th>
                <th>Inspection Bay</th>
                <th>Scheduled Time</th>
                <th>Duration</th>
                <th>Risk Level</th>
                <th style={{ textAlign: 'center' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredSchedules.length === 0 ? (
                <tr><td colSpan="7" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>No scheduled containers available.</td></tr>
              ) : (
                filteredSchedules.map((s) => {
                  const riskLvl = s.risk_level || 'Low';
                  const riskBadgeClass = `badge badge-${riskLvl.toLowerCase()}`;
                  const startTimeFormatted = s.start_time ? (s.start_time.includes('T') ? s.start_time.split('T')[1].slice(0, 5) : s.start_time) : '08:00';
                  const endTimeFormatted = s.end_time ? (s.end_time.includes('T') ? s.end_time.split('T')[1].slice(0, 5) : s.end_time) : '08:45';

                  return (
                    <tr key={s.schedule_id}>
                      <td>
                        <div style={{ fontWeight: 600, color: '#0a2540', fontSize: '0.825rem' }}>{s.container_number}</div>
                        <div style={{ fontSize: '0.675rem', color: '#70869d', marginTop: '0.05rem', fontWeight: 400 }}>{s.cusdec_number || 'CUS2026/COL/10835'}</div>
                      </td>
                      <td style={{ color: '#0a2540', fontWeight: 500 }}>{s.officer_name}</td>
                      <td><span className="badge badge-ready">{s.bay_name}</span></td>
                      <td style={{ color: '#0066b2', fontWeight: 600 }}>{startTimeFormatted} - {endTimeFormatted}</td>
                      <td style={{ color: '#4a607a', fontWeight: 400 }}>{s.duration_minutes || 45} mins</td>
                      <td><span className={riskBadgeClass}>{riskLvl}</span></td>
                      <td style={{ textAlign: 'center' }}>
                        <button
                          type="button"
                          className="btn btn-secondary"
                          style={{ padding: '0.25rem 0.65rem', fontSize: '0.75rem' }}
                          onClick={() => setSelectedItem(s)}
                        >
                          <Eye size={13} /> View Slot
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* SCHEDULE DETAILS MODAL */}
      {selectedItem && (
        <div
          style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(10, 37, 64, 0.45)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, cursor: 'pointer'
          }}
          onClick={() => setSelectedItem(null)}
        >
          <div
            style={{ background: '#ffffff', border: '1px solid var(--border-color)', color: '#0a2540', padding: '1.75rem', borderRadius: '14px', width: '90vw', maxWidth: '520px', cursor: 'default', position: 'relative', boxShadow: '0 12px 40px rgba(10, 83, 152, 0.25)' }}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              onClick={() => setSelectedItem(null)}
              style={{
                position: 'absolute', top: '1.25rem', right: '1.25rem',
                background: '#f4f8fc', border: 'none', borderRadius: '50%', color: '#4a607a', width: '28px', height: '28px',
                display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer'
              }}
            >
              <X size={15} />
            </button>

            <h2 style={{ marginBottom: '1rem', color: '#0a2540', fontSize: '1.15rem', fontWeight: 600 }}>
              Scheduled Inspection Slot #{selectedItem.container_number}
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem', fontSize: '0.825rem', marginBottom: '1.25rem' }}>
              <div>
                <span style={{ color: '#4a607a', fontWeight: 500 }}>Customs Inspector:</span>
                <div style={{ color: '#0a2540', fontWeight: 600 }}>{selectedItem.officer_name}</div>
              </div>
              <div>
                <span style={{ color: '#4a607a', fontWeight: 500 }}>Assigned Bay:</span>
                <div style={{ color: '#0066b2', fontWeight: 600 }}>{selectedItem.bay_name}</div>
              </div>
              <div>
                <span style={{ color: '#4a607a', fontWeight: 500 }}>Start Time:</span>
                <div style={{ color: '#047857', fontWeight: 600 }}>{selectedItem.startTimeFormatted || '08:00'}</div>
              </div>
              <div>
                <span style={{ color: '#4a607a', fontWeight: 500 }}>Completion Time:</span>
                <div style={{ color: '#047857', fontWeight: 600 }}>{selectedItem.endTimeFormatted || '08:45'}</div>
              </div>
            </div>

            <div style={{ background: '#f4f8fc', border: '1px solid var(--border-color)', padding: '0.85rem', borderRadius: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 600, fontSize: '0.825rem', color: '#0a2540' }}>Risk Classification</span>
                <span className={`badge badge-${(selectedItem.risk_level || 'low').toLowerCase()}`}>
                  {selectedItem.risk_level || 'Low Risk'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* RISK COLOR LEGEND MODAL */}
      {showLegendModal && (
        <div
          style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(10, 37, 64, 0.45)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, cursor: 'pointer'
          }}
          onClick={() => setShowLegendModal(false)}
        >
          <div
            style={{ background: '#ffffff', border: '1px solid var(--border-color)', color: '#0a2540', padding: '1.75rem', borderRadius: '14px', width: '90vw', maxWidth: '450px', cursor: 'default', position: 'relative', boxShadow: '0 12px 40px rgba(10, 83, 152, 0.25)' }}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              onClick={() => setShowLegendModal(false)}
              style={{
                position: 'absolute', top: '1.25rem', right: '1.25rem',
                background: '#f4f8fc', border: 'none', borderRadius: '50%', color: '#4a607a', width: '28px', height: '28px',
                display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer'
              }}
            >
              <X size={15} />
            </button>

            <h2 style={{ marginBottom: '1.25rem', color: '#0a2540', fontSize: '1.15rem', fontWeight: 600 }}>
              Gantt Matrix Risk Tier Color Palette
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.825rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span className="badge badge-critical" style={{ width: '90px', justifyContent: 'center' }}>CRITICAL</span>
                <span style={{ color: '#4a607a' }}>Velvet Rose Gradient (Score ≥ 80)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span className="badge badge-high" style={{ width: '90px', justifyContent: 'center' }}>HIGH</span>
                <span style={{ color: '#4a607a' }}>Coral Orange Gradient (Score 60 - 79)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span className="badge badge-medium" style={{ width: '90px', justifyContent: 'center' }}>MEDIUM</span>
                <span style={{ color: '#4a607a' }}>Golden Amber Gradient (Score 40 - 59)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span className="badge badge-low" style={{ width: '90px', justifyContent: 'center' }}>LOW</span>
                <span style={{ color: '#4a607a' }}>Fresh Mint Gradient (Score &lt; 40)</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <ConfirmResetModal
        isOpen={resetModalOpen}
        onClose={() => setResetModalOpen(false)}
        onConfirm={handleConfirmResetSchedule}
        title="Reset Examination Schedule?"
        message="This action will clear all scheduled container time slots and return containers to Ready for optimization."
        loading={resettingData}
      />
    </div>
  );
}
