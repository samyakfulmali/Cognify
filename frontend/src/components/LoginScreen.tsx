import React, { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import { loginUser } from '../services/api';
import type { UserRole } from '../types';
import {
  BrainIcon,
  EyeIcon,
  EyeOffIcon,
  GraduationCapIcon,
  LockIcon,
  MoonIcon,
  SunIcon,
  UserIcon,
} from './Icons';

interface LoginScreenProps {
  onLoginSuccess: (role: UserRole, studentId: string | null, name: string) => void;
}

const PRESET_STUDENTS = [
  { id: 'std_frac_01', name: 'Fraction Struggler (std_frac_01)', persona: 'Fraction Addition & Common Denom Gap' },
  { id: 'std_adv_01', name: 'Advanced Achiever (std_adv_01)', persona: '85%+ Across All 16 Concepts' },
  { id: 'std_gap_01', name: 'Prerequisite Root-Gap (std_gap_01)', persona: 'Fails Linear Eq due to Negative Numbers' },
  { id: 'std_neg_01', name: 'Negative Signs Confused (std_neg_01)', persona: 'Signs & Operations Confusion' },
  { id: 'std_beg_01', name: 'Beginner Learner (std_beg_01)', persona: 'Starting out on foundational roots' },
];

export const LoginScreen: React.FC<LoginScreenProps> = ({ onLoginSuccess }) => {
  const { theme, toggleTheme } = useTheme();

  // Student form state
  const [studentLoginId, setStudentLoginId] = useState<string>(() => {
    return localStorage.getItem('cognify_student_id') || 'std_frac_01';
  });
  const [studentPassword, setStudentPassword] = useState<string>('student123');
  const [showStudentPassword, setShowStudentPassword] = useState<boolean>(false);
  const [studentError, setStudentError] = useState<string | null>(null);
  const [studentLoading, setStudentLoading] = useState<boolean>(false);

  // Teacher form state
  const [teacherLoginId, setTeacherLoginId] = useState<string>('teacher');
  const [teacherPassword, setTeacherPassword] = useState<string>('1234');
  const [showTeacherPassword, setShowTeacherPassword] = useState<boolean>(false);
  const [teacherError, setTeacherError] = useState<string | null>(null);
  const [teacherLoading, setTeacherLoading] = useState<boolean>(false);

  const handleStudentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedId = studentLoginId.trim();
    if (!trimmedId) {
      setStudentError('Please enter a Student Login ID.');
      return;
    }

    setStudentError(null);
    setStudentLoading(true);

    try {
      const res = await loginUser({
        role: 'student',
        student_id: trimmedId,
        password: studentPassword.trim() || 'student123',
      });

      localStorage.setItem('cognify_token', res.access_token);
      localStorage.setItem('cognify_user_role', res.role);
      if (res.student_id) localStorage.setItem('cognify_student_id', res.student_id);
      if (res.name) localStorage.setItem('cognify_user_name', res.name);

      onLoginSuccess('student', res.student_id, res.name || trimmedId);
    } catch (err: any) {
      setStudentError(err.message || 'Student login failed. Check ID.');
    } finally {
      setStudentLoading(false);
    }
  };

  const handleTeacherSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedPin = teacherPassword.trim();
    if (!trimmedPin) {
      setTeacherError('Please enter the Teacher PIN (demo: 1234).');
      return;
    }

    setTeacherError(null);
    setTeacherLoading(true);

    try {
      const res = await loginUser({
        role: 'teacher',
        pin: trimmedPin,
      });

      localStorage.setItem('cognify_token', res.access_token);
      localStorage.setItem('cognify_user_role', res.role);
      if (res.name) localStorage.setItem('cognify_user_name', res.name);
      localStorage.removeItem('cognify_student_id');

      onLoginSuccess('teacher', null, res.name || 'Educator');
    } catch (err: any) {
      setTeacherError(err.message || 'Invalid Teacher PIN.');
    } finally {
      setTeacherLoading(false);
    }
  };

  const handleQuickSelectStudent = (sid: string) => {
    setStudentLoginId(sid);
    setStudentError(null);
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '32px 20px',
      }}
    >
      {/* Top Brand Header */}
      <div
        className="glass-card"
        style={{
          width: '100%',
          maxWidth: '1000px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '16px 28px',
          marginBottom: '36px',
          borderRadius: 'var(--radius-xl)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div
            style={{
              width: '46px',
              height: '46px',
              borderRadius: '14px',
              background: 'linear-gradient(135deg, #6366f1, #06b6d4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              boxShadow: '0 4px 18px var(--primary-glow)',
            }}
          >
            <BrainIcon size={26} />
          </div>
          <div>
            <h1
              style={{
                fontSize: '22px',
                fontWeight: 800,
                letterSpacing: '-0.02em',
                lineHeight: 1.2,
                color: 'var(--text-primary)',
              }}
            >
              Cognify <span style={{ color: 'var(--primary)', fontWeight: 600 }}>Tutor</span>
            </h1>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Bayesian Knowledge Tracing & Prerequisite Root-Gap Detection
            </p>
          </div>
        </div>

        <button
          className="btn btn-icon"
          onClick={toggleTheme}
          title={`Switch to ${theme === 'dark' ? 'White (Light)' : 'Dark'} Theme`}
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <SunIcon size={18} /> : <MoonIcon size={18} />}
        </button>
      </div>

      {/* Main Container */}
      <div style={{ width: '100%', maxWidth: '1000px' }}>
        <div style={{ textAlign: 'center', marginBottom: '36px' }}>
          <h2
            style={{
              fontSize: '32px',
              fontWeight: 800,
              letterSpacing: '-0.02em',
              color: 'var(--text-primary)',
              marginBottom: '10px',
            }}
          >
            Login to Your Learning Portal
          </h2>
          <p
            style={{
              fontSize: '15px',
              color: 'var(--text-secondary)',
              maxWidth: '620px',
              margin: '0 auto',
            }}
          >
            Sign in as a student learner (isolated student view) or an educator (class-wide heatmap & analytics).
          </p>
        </div>

        {/* 2 Role Login Cards */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
            gap: '28px',
          }}
        >
          {/* Card 1: Student Login */}
          <div
            className="glass-card"
            style={{
              padding: '36px 32px',
              borderRadius: 'var(--radius-xl)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              position: 'relative',
              overflow: 'hidden',
              border: '1px solid var(--border-accent)',
              boxShadow: 'var(--shadow-card)',
            }}
          >
            <div>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '20px',
                }}
              >
                <div
                  style={{
                    width: '52px',
                    height: '52px',
                    borderRadius: '16px',
                    background: 'linear-gradient(135deg, #6366f1, #3b82f6)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#ffffff',
                    boxShadow: '0 6px 20px rgba(99, 102, 241, 0.35)',
                  }}
                >
                  <UserIcon size={28} />
                </div>
                <span className="badge badge-primary" style={{ padding: '6px 14px', fontSize: '12px' }}>
                  Student Portal
                </span>
              </div>

              <h3
                style={{
                  fontSize: '24px',
                  fontWeight: 800,
                  color: 'var(--text-primary)',
                  marginBottom: '8px',
                }}
              >
                I&apos;m a Student
              </h3>
              <p
                style={{
                  fontSize: '14px',
                  color: 'var(--text-secondary)',
                  lineHeight: 1.5,
                  marginBottom: '24px',
                }}
              >
                Access your personalized adaptive practice, AI misconception remediation, and prerequisite knowledge graph.
              </p>

              <form onSubmit={handleStudentSubmit}>
                {/* Student Login ID */}
                <div style={{ marginBottom: '16px' }}>
                  <label
                    htmlFor="student-login-id"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '13px',
                      fontWeight: 600,
                      color: 'var(--text-secondary)',
                      marginBottom: '8px',
                    }}
                  >
                    <UserIcon size={14} />
                    <span>Student Login ID:</span>
                  </label>
                  <input
                    id="student-login-id"
                    type="text"
                    className="select-input"
                    value={studentLoginId}
                    onChange={(e) => {
                      setStudentLoginId(e.target.value);
                      setStudentError(null);
                    }}
                    placeholder="e.g. std_frac_01"
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      fontSize: '14px',
                      borderRadius: 'var(--radius-md)',
                    }}
                  />

                  {/* Seeded quick-select helper buttons */}
                  <div style={{ marginTop: '10px' }}>
                    <div
                      style={{
                        fontSize: '11px',
                        fontWeight: 600,
                        color: 'var(--text-muted)',
                        marginBottom: '6px',
                      }}
                    >
                      Quick-fill demo student:
                    </div>
                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                      {PRESET_STUDENTS.map((p) => (
                        <button
                          key={p.id}
                          type="button"
                          onClick={() => handleQuickSelectStudent(p.id)}
                          style={{
                            padding: '4px 8px',
                            fontSize: '11px',
                            background: studentLoginId === p.id ? 'var(--primary)' : 'var(--bg-input)',
                            color: studentLoginId === p.id ? '#ffffff' : 'var(--text-secondary)',
                            border: '1px solid var(--border-color)',
                            borderRadius: 'var(--radius-sm)',
                            cursor: 'pointer',
                          }}
                          title={p.persona}
                        >
                          {p.id}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Student Password */}
                <div style={{ marginBottom: '22px' }}>
                  <label
                    htmlFor="student-password"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '13px',
                      fontWeight: 600,
                      color: 'var(--text-secondary)',
                      marginBottom: '8px',
                    }}
                  >
                    <LockIcon size={14} />
                    <span>Password:</span>
                  </label>
                  <div style={{ position: 'relative' }}>
                    <input
                      id="student-password"
                      type={showStudentPassword ? 'text' : 'password'}
                      className="select-input"
                      value={studentPassword}
                      onChange={(e) => {
                        setStudentPassword(e.target.value);
                        setStudentError(null);
                      }}
                      placeholder="student123"
                      style={{
                        width: '100%',
                        padding: '12px 42px 12px 16px',
                        fontSize: '14px',
                        borderRadius: 'var(--radius-md)',
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowStudentPassword(!showStudentPassword)}
                      style={{
                        position: 'absolute',
                        right: '12px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        padding: '4px',
                      }}
                      aria-label="Toggle password visibility"
                    >
                      {showStudentPassword ? <EyeOffIcon size={18} /> : <EyeIcon size={18} />}
                    </button>
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '6px' }}>
                    Demo Credentials: ID: <strong>std_frac_01</strong> • Password: <strong>student123</strong>
                  </div>

                  {studentError && (
                    <div style={{ color: 'var(--danger)', fontSize: '12px', marginTop: '6px', fontWeight: 600 }}>
                      {studentError}
                    </div>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={studentLoading}
                  className="btn btn-primary"
                  style={{
                    width: '100%',
                    padding: '14px 24px',
                    fontSize: '15px',
                    fontWeight: 700,
                    borderRadius: 'var(--radius-md)',
                    boxShadow: '0 4px 18px var(--primary-glow)',
                  }}
                >
                  {studentLoading ? 'Signing In...' : 'Login as Student ➔'}
                </button>
              </form>
            </div>
          </div>

          {/* Card 2: Teacher Login */}
          <div
            className="glass-card"
            style={{
              padding: '36px 32px',
              borderRadius: 'var(--radius-xl)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              position: 'relative',
              overflow: 'hidden',
              border: '1px solid rgba(16, 185, 129, 0.35)',
              boxShadow: 'var(--shadow-card)',
            }}
          >
            <div>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '20px',
                }}
              >
                <div
                  style={{
                    width: '52px',
                    height: '52px',
                    borderRadius: '16px',
                    background: 'linear-gradient(135deg, #10b981, #06b6d4)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#ffffff',
                    boxShadow: '0 6px 20px rgba(16, 185, 129, 0.35)',
                  }}
                >
                  <GraduationCapIcon size={28} />
                </div>
                <span className="badge badge-success" style={{ padding: '6px 14px', fontSize: '12px' }}>
                  Educator Portal
                </span>
              </div>

              <h3
                style={{
                  fontSize: '24px',
                  fontWeight: 800,
                  color: 'var(--text-primary)',
                  marginBottom: '8px',
                }}
              >
                I&apos;m a Teacher
              </h3>
              <p
                style={{
                  fontSize: '14px',
                  color: 'var(--text-secondary)',
                  lineHeight: 1.5,
                  marginBottom: '24px',
                }}
              >
                Inspect class-wide BKT mastery heatmaps across 30 students, diagnose root gaps, and examine systemic misconceptions.
              </p>

              <form onSubmit={handleTeacherSubmit}>
                {/* Teacher Login ID */}
                <div style={{ marginBottom: '16px' }}>
                  <label
                    htmlFor="teacher-login-id"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '13px',
                      fontWeight: 600,
                      color: 'var(--text-secondary)',
                      marginBottom: '8px',
                    }}
                  >
                    <UserIcon size={14} />
                    <span>Teacher Username:</span>
                  </label>
                  <input
                    id="teacher-login-id"
                    type="text"
                    className="select-input"
                    value={teacherLoginId}
                    onChange={(e) => {
                      setTeacherLoginId(e.target.value);
                      setTeacherError(null);
                    }}
                    placeholder="teacher"
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      fontSize: '14px',
                      borderRadius: 'var(--radius-md)',
                    }}
                  />
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                    Demo ID: <strong>teacher</strong>
                  </div>
                </div>

                {/* Teacher PIN / Password */}
                <div style={{ marginBottom: '22px' }}>
                  <label
                    htmlFor="teacher-password"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '13px',
                      fontWeight: 600,
                      color: 'var(--text-secondary)',
                      marginBottom: '8px',
                    }}
                  >
                    <LockIcon size={14} />
                    <span>Teacher Demo PIN:</span>
                  </label>
                  <div style={{ position: 'relative' }}>
                    <input
                      id="teacher-password"
                      type={showTeacherPassword ? 'text' : 'password'}
                      className="select-input"
                      value={teacherPassword}
                      onChange={(e) => {
                        setTeacherPassword(e.target.value);
                        setTeacherError(null);
                      }}
                      placeholder="1234"
                      style={{
                        width: '100%',
                        padding: '12px 42px 12px 16px',
                        fontSize: '14px',
                        borderRadius: 'var(--radius-md)',
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowTeacherPassword(!showTeacherPassword)}
                      style={{
                        position: 'absolute',
                        right: '12px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        padding: '4px',
                      }}
                      aria-label="Toggle password visibility"
                    >
                      {showTeacherPassword ? <EyeOffIcon size={18} /> : <EyeIcon size={18} />}
                    </button>
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '6px' }}>
                    Demo PIN: <strong>1234</strong> (or <strong>teacher123</strong>)
                  </div>

                  {teacherError && (
                    <div style={{ color: 'var(--danger)', fontSize: '12px', marginTop: '6px', fontWeight: 600 }}>
                      {teacherError}
                    </div>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={teacherLoading}
                  className="btn btn-primary"
                  style={{
                    width: '100%',
                    padding: '14px 24px',
                    fontSize: '15px',
                    fontWeight: 700,
                    borderRadius: 'var(--radius-md)',
                    background: 'linear-gradient(135deg, #10b981, #06b6d4)',
                    boxShadow: '0 4px 18px rgba(16, 185, 129, 0.3)',
                  }}
                >
                  {teacherLoading ? 'Signing In...' : 'Login as Teacher ➔'}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;
