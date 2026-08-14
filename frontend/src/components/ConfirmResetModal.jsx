import React from 'react';
import { RotateCcw, AlertTriangle, X, Check } from 'lucide-react';

export function ConfirmResetModal({
  isOpen,
  onClose,
  onConfirm,
  title = "Reset Demonstration Data?",
  message = "This action will restore all AI recommendations, anomaly dispositions, tariff reviews, and scheduled inspection rosters back to their original default state.",
  loading = false
}) {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(10, 37, 64, 0.45)',
        backdropFilter: 'blur(6px)',
        zIndex: 99999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem',
        animation: 'fadeIn 0.15s ease-out'
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="card"
        style={{
          width: '100%',
          maxWidth: '460px',
          padding: '1.75rem',
          borderRadius: '16px',
          background: '#ffffff',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          border: '1px solid #e2e8f0',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem',
          position: 'relative'
        }}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          disabled={loading}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            background: 'none',
            border: 'none',
            color: '#94a3b8',
            cursor: 'pointer',
            padding: '0.25rem',
            borderRadius: '50%'
          }}
        >
          <X size={18} />
        </button>

        {/* Modal Header */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
          <div
            style={{
              width: '46px',
              height: '46px',
              borderRadius: '12px',
              background: '#fef3c7',
              border: '1px solid #fde68a',
              color: '#d97706',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}
          >
            <RotateCcw size={22} className={loading ? "spin-icon" : ""} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#0a2540', margin: 0, lineHeight: 1.3 }}>
              {title}
            </h3>
            <p style={{ fontSize: '0.825rem', color: '#64748b', margin: '0.35rem 0 0', lineHeight: 1.45 }}>
              {message}
            </p>
          </div>
        </div>

        {/* Modal Action Buttons */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.65rem', marginTop: '0.5rem' }}>
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="btn"
            style={{
              backgroundColor: '#f1f5f9',
              color: '#475569',
              padding: '0.5rem 1.15rem',
              fontSize: '0.8rem',
              fontWeight: 600,
              borderRadius: '8px',
              border: '1px solid #cbd5e1'
            }}
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className="btn"
            style={{
              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
              color: '#ffffff',
              padding: '0.5rem 1.25rem',
              fontSize: '0.8rem',
              fontWeight: 700,
              borderRadius: '8px',
              border: 'none',
              boxShadow: '0 4px 12px rgba(245, 158, 11, 0.3)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem'
            }}
          >
            {loading ? (
              <>Resetting Data...</>
            ) : (
              <><RotateCcw size={14} /> Confirm Reset</>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
