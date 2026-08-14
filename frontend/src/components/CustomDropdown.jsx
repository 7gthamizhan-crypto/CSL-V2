import React, { useState, useEffect, useRef } from 'react';
import { ChevronDown, Check } from 'lucide-react';

export function CustomDropdown({ icon: Icon, value, options, onChange, placeholder, style }) {
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
    <div className="custom-dropdown-container" ref={containerRef} style={style}>
      <div 
        className={`custom-dropdown-trigger ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.45rem',
          backgroundColor: '#ffffff',
          border: '1px solid #cbd5e1',
          borderRadius: '8px',
          padding: '0.4rem 0.75rem',
          color: '#0a2540',
          fontSize: '0.775rem',
          fontWeight: 600,
          cursor: 'pointer',
          userSelect: 'none',
          whiteSpace: 'nowrap',
          boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
          transition: 'all 0.15s ease'
        }}
      >
        {Icon && <Icon size={14} color="#0066b2" />}
        <span>{selectedOption ? selectedOption.label : placeholder}</span>
        <ChevronDown size={14} color="#64748b" style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s ease', marginLeft: '0.2rem' }} />
      </div>

      {isOpen && (
        <div 
          className="custom-dropdown-menu"
          style={{
            position: 'absolute',
            top: 'calc(100% + 4px)',
            right: 0,
            minWidth: '170px',
            backgroundColor: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            boxShadow: '0 10px 25px rgba(10,37,64,0.12)',
            padding: '0.35rem',
            zIndex: 9999,
            display: 'flex',
            flexDirection: 'column',
            gap: '0.15rem'
          }}
        >
          {options.map((opt) => {
            const isSelected = value === opt.value;
            return (
              <div
                key={opt.value}
                onClick={(e) => {
                  e.stopPropagation();
                  onChange(opt.value);
                  setIsOpen(false);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justify: 'space-between',
                  padding: '0.45rem 0.75rem',
                  color: isSelected ? '#ffffff' : '#334155',
                  backgroundColor: isSelected ? '#0066b2' : 'transparent',
                  fontSize: '0.775rem',
                  fontWeight: isSelected ? 600 : 500,
                  borderRadius: '6px',
                  cursor: 'pointer',
                  transition: 'all 0.12s ease'
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.backgroundColor = '#f1f5f9';
                    e.currentTarget.style.color = '#0066b2';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.color = '#334155';
                  }
                }}
              >
                <span>{opt.label}</span>
                {isSelected && <Check size={14} color="#ffffff" />}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
