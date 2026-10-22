import React, { useEffect, useState } from 'react';
import { fetchMisconceptions } from '../services/api';
import type { MisconceptionsResponse } from '../types';
import { BulbIcon } from './Icons';

export const MisconceptionsView: React.FC = () => {
  const [data, setData] = useState<MisconceptionsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetchMisconceptions()
      .then(setData)
      .catch((err) => setError(err.message || 'Failed to load misconceptions'))
      .finally(() => setLoading(false));
  }, []);

  const maxCount = data?.top_misconceptions.length
    ? Math.max(...data.top_misconceptions.map((m) => m.count))
    : 1;

  return (
    <div className="animate-fade-in">
      {/* Metrics Row */}
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
            <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '4px' }}>
              Total Misconception Attempts
            </div>
            <div style={{ fontSize: '28px', fontWeight: 800, color: 'var(--danger)' }}>
              {data.total_occurrences}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Across 600 simulated question attempts
            </div>
          </div>

          <div className="glass-card">
            <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '4px' }}>
              Unique Misconception Types
            </div>
            <div style={{ fontSize: '28px', fontWeight: 800, color: 'var(--primary)' }}>
              {data.unique_misconceptions}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Distinct cognitive error tags in question bank
            </div>
          </div>
        </div>
      )}

      {/* Misconception Leaderboard */}
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
          <BulbIcon size={22} style={{ color: 'var(--warning)' }} />
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)' }}>
              Cohort Misconception Leaderboard
            </h2>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Ranked frequency of systemic student misconceptions to guide class-wide pedagogical intervention
            </p>
          </div>
        </div>

        {loading && (
          <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
            Loading misconception occurrences...
          </div>
        )}

        {error && (
          <div style={{ padding: '16px', color: 'var(--danger)' }}>
            {error}
          </div>
        )}

        {data && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {data.top_misconceptions.map((item, idx) => {
              const barWidth = Math.max(10, (item.count / maxCount) * 100);

              return (
                <div
                  key={idx}
                  style={{
                    padding: '16px 20px',
                    borderRadius: 'var(--radius-lg)',
                    background: 'var(--bg-input)',
                    border: '1px solid var(--border-color)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '10px',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span
                          style={{
                            width: '24px',
                            height: '24px',
                            borderRadius: '6px',
                            background: idx < 3 ? 'var(--danger-glow)' : 'var(--border-color)',
                            color: idx < 3 ? 'var(--danger)' : 'var(--text-secondary)',
                            fontWeight: 800,
                            fontSize: '12px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          #{idx + 1}
                        </span>
                        <span style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)' }}>
                          {item.misconception.replace(/_/g, ' ')}
                        </span>
                      </div>
                      <span style={{ fontSize: '12px', color: 'var(--accent-cyan)', marginLeft: '32px' }}>
                        Concept: {item.concept_name}
                      </span>
                    </div>

                    <div style={{ textAlign: 'right' }}>
                      <span
                        style={{
                          fontSize: '20px',
                          fontWeight: 800,
                          fontFamily: 'var(--font-mono)',
                          color: 'var(--danger)',
                        }}
                      >
                        {item.count}
                      </span>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>
                        {item.affected_students} students affected
                      </span>
                    </div>
                  </div>

                  {/* Relative Frequency Bar */}
                  <div
                    style={{
                      height: '6px',
                      background: 'var(--border-color)',
                      borderRadius: '999px',
                      overflow: 'hidden',
                    }}
                  >
                    <div
                      style={{
                        height: '100%',
                        width: `${barWidth}%`,
                        background:
                          idx < 3
                            ? 'linear-gradient(90deg, #ef4444, #f59e0b)'
                            : 'var(--primary)',
                        borderRadius: '999px',
                        transition: 'width 0.4s ease',
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
