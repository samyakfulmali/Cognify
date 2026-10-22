import React, { useEffect, useState } from 'react';
import { fetchClassHeatmap } from '../services/api';
import type { ClassHeatmapResponse } from '../types';

interface ClassHeatmapViewProps {
  onSelectStudent?: (studentId: string) => void;
}

export const ClassHeatmapView: React.FC<ClassHeatmapViewProps> = ({ onSelectStudent }) => {
  const [data, setData] = useState<ClassHeatmapResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetchClassHeatmap()
      .then(setData)
      .catch((err) => setError(err.message || 'Failed to load class heatmap'))
      .finally(() => setLoading(false));
  }, []);

  const getCellColor = (p: number): string => {
    if (p >= 0.85) return 'rgba(16, 185, 129, 0.8)';
    if (p >= 0.70) return 'rgba(52, 211, 153, 0.45)';
    if (p >= 0.50) return 'rgba(245, 158, 11, 0.65)';
    if (p >= 0.35) return 'rgba(239, 68, 68, 0.45)';
    return 'rgba(239, 68, 68, 0.8)';
  };

  return (
    <div className="animate-fade-in">
      {/* Top Metric Cards */}
      {data && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '18px',
            marginBottom: '24px',
          }}
        >
          <div className="glass-card">
            <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '4px' }}>Cohort Size</div>
            <div style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)' }}>
              {data.total_students} Students
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Simulated 5 learning gap personas
            </div>
          </div>

          <div className="glass-card">
            <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '4px' }}>Class Average Mastery</div>
            <div style={{ fontSize: '28px', fontWeight: 800, color: 'var(--success)' }}>
              {(data.class_average_mastery * 100).toFixed(1)}%
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Across 16 concepts (Fractions → Algebra)
            </div>
          </div>

          <div className="glass-card">
            <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '4px' }}>Bottleneck / Hardest Concept</div>
            <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--danger)', marginTop: '4px' }}>
              {data.hardest_concept || '—'}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Lowest cohort average mastery
            </div>
          </div>

          <div className="glass-card">
            <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '4px' }}>Highest Mastered Concept</div>
            <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: '4px' }}>
              {data.most_mastered_concept || '—'}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Strongest foundational retention
            </div>
          </div>
        </div>
      )}

      {/* Heatmap Matrix Card */}
      <div className="glass-card">
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '18px',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)' }}>
              Class-Wide Mastery Heatmap Matrix
            </h2>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Click any student row to switch active quiz student
            </p>
          </div>

          <div style={{ display: 'flex', gap: '14px', fontSize: '12px', alignItems: 'center' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '12px', height: '12px', background: '#ef4444', borderRadius: '3px' }}></span>
              <span>&lt;40% Gap</span>
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '12px', height: '12px', background: '#f59e0b', borderRadius: '3px' }}></span>
              <span>40-70% Practice</span>
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '12px', height: '12px', background: '#10b981', borderRadius: '3px' }}></span>
              <span>≥85% Mastered</span>
            </span>
          </div>
        </div>

        {loading && (
          <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
            Loading 30×16 student cohort mastery matrix...
          </div>
        )}

        {error && (
          <div style={{ padding: '16px', color: 'var(--danger)' }}>
            {error}
          </div>
        )}

        {data && (
          <div
            style={{
              overflowX: 'auto',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--border-color)',
            }}
          >
            <table
              style={{
                width: '100%',
                borderCollapse: 'collapse',
                fontSize: '12px',
                whiteSpace: 'nowrap',
              }}
            >
              <thead>
                <tr>
                  <th
                    style={{
                      padding: '12px 16px',
                      background: 'var(--bg-card-hover)',
                      color: 'var(--text-primary)',
                      fontWeight: 700,
                      textAlign: 'left',
                      position: 'sticky',
                      left: 0,
                      zIndex: 3,
                      borderBottom: '1px solid var(--border-color)',
                      minWidth: '180px',
                    }}
                  >
                    Student Name
                  </th>
                  {data.concepts.map((c) => (
                    <th
                      key={c.concept_id}
                      style={{
                        padding: '12px 10px',
                        background: 'var(--bg-card-hover)',
                        color: 'var(--text-secondary)',
                        fontWeight: 600,
                        textAlign: 'center',
                        borderBottom: '1px solid var(--border-color)',
                        fontSize: '11px',
                        maxWidth: '90px',
                      }}
                      title={`${c.name} (${c.mastery_percentage}% of class mastered)`}
                    >
                      {c.name.length > 13 ? c.name.slice(0, 11) + '..' : c.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.students.map((s) => (
                  <tr
                    key={s.student_id}
                    onClick={() => onSelectStudent && onSelectStudent(s.student_id)}
                    style={{
                      cursor: onSelectStudent ? 'pointer' : 'default',
                      transition: 'background-color 0.15s ease',
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.background = 'rgba(255, 255, 255, 0.03)';
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.background = 'transparent';
                    }}
                  >
                    <td
                      style={{
                        padding: '10px 16px',
                        fontWeight: 600,
                        position: 'sticky',
                        left: 0,
                        background: 'var(--bg-secondary)',
                        borderBottom: '1px solid var(--border-color)',
                        color: 'var(--text-primary)',
                        zIndex: 1,
                      }}
                    >
                      {s.name}
                    </td>

                    {data.concepts.map((c) => {
                      const score = data.matrix[s.student_id]?.[c.concept_id] ?? 0.3;
                      const bg = getCellColor(score);
                      return (
                        <td
                          key={c.concept_id}
                          style={{
                            padding: '8px 10px',
                            textAlign: 'center',
                            fontFamily: 'var(--font-mono)',
                            fontSize: '11px',
                            fontWeight: 700,
                            color: '#ffffff',
                            background: bg,
                            borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                            borderRight: '1px solid rgba(255, 255, 255, 0.04)',
                          }}
                          title={`${s.name} • ${c.name}: ${(score * 100).toFixed(1)}%`}
                        >
                          {(score * 100).toFixed(0)}%
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
