import React from 'react';
import { useTheme } from '../context/ThemeContext';
import type { Student, UserRole } from '../types';
import {
  BulbIcon,
  GraduationCapIcon,
  GraphIcon,
  HeatmapIcon,
  LogoutIcon,
  MoonIcon,
  SunIcon,
  TargetIcon,
  UserIcon,
} from './Icons';

export type TabType = 'quiz' | 'graph' | 'heatmap' | 'misconceptions' | 'profile';

interface HeaderProps {
  students: Student[];
  selectedStudentId: string;
  onSelectStudent: (id: string) => void;
  activeTab: TabType;
  onSelectTab: (tab: TabType) => void;
  userRole: UserRole | null;
  studentName?: string;
  loggedInId?: string;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  students,
  selectedStudentId,
  onSelectStudent,
  activeTab,
  onSelectTab,
  userRole,
  studentName,
  loggedInId,
  onLogout,
}) => {
  const { theme, toggleTheme } = useTheme();

  const getPersonaLabel = (id: string) => {
    if (id.startsWith('std_adv')) return 'Advanced Achiever';
    if (id.startsWith('std_frac')) return 'Fraction Struggler';
    if (id.startsWith('std_neg')) return 'Negative Signs Confused';
    if (id.startsWith('std_gap')) return 'Hidden Root Gap';
    if (id.startsWith('std_beg')) return 'Beginner';
    return 'Learner';
  };

  return (
    <header style={{ marginBottom: '28px' }}>
      {/* Top Navbar */}
      <div
        className="glass-card"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '16px 24px',
          marginBottom: '20px',
          borderRadius: 'var(--radius-xl)',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <img
            src="/logo.svg"
            alt="Cognify Logo"
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '12px',
              boxShadow: userRole === 'teacher'
                ? '0 4px 16px rgba(16, 185, 129, 0.3)'
                : '0 4px 16px var(--primary-glow)',
            }}
          />
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1
                style={{
                  fontSize: '20px',
                  fontWeight: 800,
                  letterSpacing: '-0.02em',
                  lineHeight: 1.2,
                  color: 'var(--text-primary)',
                }}
              >
                Cognify <span style={{ color: userRole === 'teacher' ? 'var(--success)' : 'var(--primary)', fontWeight: 600 }}>Tutor</span>
              </h1>
              {userRole === 'teacher' ? (
                <span className="badge badge-success" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <GraduationCapIcon size={12} /> Teacher: {loggedInId || 'Educator'}
                </span>
              ) : (
                <span className="badge badge-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <UserIcon size={12} /> Student: {studentName || selectedStudentId} ({selectedStudentId})
                </span>
              )}
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              {userRole === 'teacher'
                ? 'Cohort Mastery Heatmap & Prerequisite Root-Gap Analytics'
                : 'Personalized Adaptive BKT & Prerequisite Remediation'}
            </p>
          </div>
        </div>

        {/* BKT Parameter Chips and Controls */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div
            style={{
              padding: '6px 12px',
              background: 'var(--bg-input)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              color: 'var(--text-secondary)',
            }}
          >
            P(init): <strong style={{ color: 'var(--accent-cyan)' }}>0.30</strong>
          </div>
          <div
            style={{
              padding: '6px 12px',
              background: 'var(--bg-input)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              color: 'var(--text-secondary)',
            }}
          >
            P(learn): <strong style={{ color: 'var(--success)' }}>0.20</strong>
          </div>
          <div
            style={{
              padding: '6px 12px',
              background: 'var(--bg-input)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              color: 'var(--text-secondary)',
            }}
          >
            P(slip): <strong style={{ color: 'var(--warning)' }}>0.10</strong>
          </div>
          <div
            style={{
              padding: '6px 12px',
              background: 'var(--bg-input)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              color: 'var(--text-secondary)',
            }}
          >
            P(guess): <strong style={{ color: 'var(--primary)' }}>0.25</strong>
          </div>

          {/* Teacher-Only Student Dropdown: Strictly hidden for students */}
          {userRole === 'teacher' && students.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginLeft: '12px' }}>
              <label
                htmlFor="teacher-student-select"
                style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)' }}
              >
                Inspect Student:
              </label>
              <select
                id="teacher-student-select"
                className="select-input"
                value={selectedStudentId}
                onChange={(e) => onSelectStudent(e.target.value)}
                style={{ fontWeight: 600, minWidth: '220px' }}
              >
                {students.map((s) => (
                  <option key={s.student_id} value={s.student_id}>
                    {s.name} ({getPersonaLabel(s.student_id)})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Theme Toggle Button */}
          <button
            className="btn btn-icon"
            onClick={toggleTheme}
            title={`Switch to ${theme === 'dark' ? 'White (Light)' : 'Dark'} Theme`}
            aria-label="Toggle theme"
            style={{ marginLeft: '6px' }}
          >
            {theme === 'dark' ? <SunIcon size={18} /> : <MoonIcon size={18} />}
          </button>

          {/* Logout Button */}
          <button
            className="btn btn-secondary"
            onClick={onLogout}
            title="Log out and clear session"
            aria-label="Logout"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              fontSize: '12px',
              fontWeight: 600,
              borderRadius: 'var(--radius-md)',
              marginLeft: '6px',
            }}
          >
            <LogoutIcon size={15} />
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Role-Filtered Tab Navigation */}
      <nav
        style={{
          display: 'flex',
          gap: '8px',
          background: 'var(--bg-card)',
          padding: '6px',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--border-color)',
          boxShadow: 'var(--shadow-card)',
          overflowX: 'auto',
        }}
      >
        {/* Student Tabs: Adaptive Quiz and Knowledge-Graph Explorer */}
        {userRole === 'student' && (
          <>
            <button
              className={`btn ${activeTab === 'quiz' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => onSelectTab('quiz')}
              style={{ flex: 1, padding: '12px 20px', borderRadius: 'var(--radius-md)' }}
            >
              <TargetIcon size={18} />
              <span>Adaptive Quiz & Misconception Tutor</span>
            </button>

            <button
              className={`btn ${activeTab === 'graph' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => onSelectTab('graph')}
              style={{ flex: 1, padding: '12px 20px', borderRadius: 'var(--radius-md)' }}
            >
              <GraphIcon size={18} />
              <span>Knowledge-Graph Explorer</span>
            </button>
          </>
        )}

        {/* Teacher Tabs: Class Mastery Heatmap, Misconception Analytics, and Student Profile */}
        {userRole === 'teacher' && (
          <>
            <button
              className={`btn ${activeTab === 'heatmap' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => onSelectTab('heatmap')}
              style={{ flex: 1, padding: '12px 20px', borderRadius: 'var(--radius-md)' }}
            >
              <HeatmapIcon size={18} />
              <span>Class Mastery Heatmap</span>
            </button>

            <button
              className={`btn ${activeTab === 'misconceptions' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => onSelectTab('misconceptions')}
              style={{ flex: 1, padding: '12px 20px', borderRadius: 'var(--radius-md)' }}
            >
              <BulbIcon size={18} />
              <span>Misconception Analytics</span>
            </button>

            <button
              className={`btn ${activeTab === 'profile' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => onSelectTab('profile')}
              style={{ flex: 1, padding: '12px 20px', borderRadius: 'var(--radius-md)' }}
            >
              <UserIcon size={18} />
              <span>Student Profile ({studentName || selectedStudentId})</span>
            </button>
          </>
        )}
      </nav>
    </header>
  );
};

export default Header;
