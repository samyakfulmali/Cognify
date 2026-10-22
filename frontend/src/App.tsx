import React, { useEffect, useState } from 'react';
import { ClassHeatmapView } from './components/ClassHeatmapView';
import { Header, type TabType } from './components/Header';
import { KnowledgeGraphExplorer } from './components/KnowledgeGraphExplorer';
import { LoginScreen } from './components/LoginScreen';
import { MisconceptionsView } from './components/MisconceptionsView';
import { QuizScreen } from './components/QuizScreen';
import { ThemeProvider } from './context/ThemeContext';
import { clearAuth, fetchStudents } from './services/api';
import type { Student, UserRole } from './types';

export const AppContent: React.FC = () => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('cognify_token'));
  const [userRole, setUserRole] = useState<UserRole | null>(() => {
    const saved = localStorage.getItem('cognify_user_role');
    if (saved === 'student' || saved === 'teacher') return saved;
    return null;
  });

  const [studentId, setStudentId] = useState<string>(() => {
    return localStorage.getItem('cognify_student_id') || 'std_frac_01';
  });

  const [studentName, setStudentName] = useState<string>(() => {
    return localStorage.getItem('cognify_user_name') || '';
  });

  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  // Active tab depends on role
  const [activeTab, setActiveTab] = useState<TabType>(() => {
    const savedRole = localStorage.getItem('cognify_user_role');
    return savedRole === 'teacher' ? 'heatmap' : 'quiz';
  });

  // Listen to 401/403 auth changes from api.ts
  useEffect(() => {
    const handleAuthChange = () => {
      setToken(null);
      setUserRole(null);
      setStudents([]);
    };

    window.addEventListener('cognify_auth_change', handleAuthChange);
    return () => window.removeEventListener('cognify_auth_change', handleAuthChange);
  }, []);

  // When logged in as teacher, fetch the cohort students list (teacher-only endpoint)
  useEffect(() => {
    if (userRole === 'teacher' && token) {
      setLoading(true);
      fetchStudents()
        .then((data) => {
          setStudents(data);
          if (data.length > 0) {
            // Default to first student if current studentId is not in list
            if (!data.some((s) => s.student_id === studentId)) {
              setStudentId(data[0].student_id);
              setStudentName(data[0].name);
            }
          }
        })
        .catch((err) => {
          console.error('Error fetching student cohort for teacher:', err);
        })
        .finally(() => setLoading(false));
    }
  }, [userRole, token]);

  const handleLoginSuccess = (role: UserRole, loggedInStudentId: string | null, name: string) => {
    const storedToken = localStorage.getItem('cognify_token');
    setToken(storedToken);
    setUserRole(role);

    if (role === 'student' && loggedInStudentId) {
      setStudentId(loggedInStudentId);
      setStudentName(name);
      setActiveTab('quiz');
    } else {
      setStudentName(name);
      setActiveTab('heatmap');
    }
  };

  const handleLogout = () => {
    clearAuth();
    setToken(null);
    setUserRole(null);
    setStudents([]);
  };

  const handleSelectStudent = (id: string) => {
    setStudentId(id);
    const matched = students.find((s) => s.student_id === id);
    if (matched) {
      setStudentName(matched.name);
    }
    // Clicking or selecting a student in teacher mode opens their profile
    if (userRole === 'teacher') {
      setActiveTab('profile');
    }
  };

  const handlePracticeConceptFromGraph = (_conceptId: string) => {
    if (userRole === 'student') {
      setActiveTab('quiz');
    }
  };

  // If not logged in or token missing, render LoginScreen
  if (!userRole || !token) {
    return <LoginScreen onLoginSuccess={handleLoginSuccess} />;
  }

  const activeStudentDisplayName = studentName || studentId;

  return (
    <div className="app-wrapper">
      <Header
        students={students}
        selectedStudentId={studentId}
        onSelectStudent={handleSelectStudent}
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        userRole={userRole}
        studentName={activeStudentDisplayName}
        loggedInId={userRole === 'teacher' ? studentName || 'Instructor' : studentId}
        onLogout={handleLogout}
      />

      <main style={{ minHeight: '600px' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '100px 0', color: 'var(--text-muted)' }}>
            Loading Cognify Data...
          </div>
        ) : (
          <>
            {/* Student Views: Quiz & Knowledge Graph Only */}
            {userRole === 'student' && (
              <>
                {activeTab === 'quiz' && (
                  <QuizScreen
                    studentId={studentId}
                    studentName={activeStudentDisplayName}
                  />
                )}

                {activeTab === 'graph' && (
                  <KnowledgeGraphExplorer
                    studentId={studentId}
                    studentName={activeStudentDisplayName}
                    onPracticeConcept={handlePracticeConceptFromGraph}
                  />
                )}
              </>
            )}

            {/* Teacher Views: Class Heatmap, Misconceptions, and Student Profile */}
            {userRole === 'teacher' && (
              <>
                {activeTab === 'heatmap' && (
                  <ClassHeatmapView
                    onSelectStudent={(id) => {
                      handleSelectStudent(id);
                    }}
                  />
                )}

                {activeTab === 'misconceptions' && <MisconceptionsView />}

                {activeTab === 'profile' && (
                  <div>
                    <div
                      className="glass-card"
                      style={{
                        padding: '16px 24px',
                        marginBottom: '20px',
                        borderRadius: 'var(--radius-lg)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        borderLeft: '4px solid var(--accent-cyan)',
                      }}
                    >
                      <div>
                        <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)' }}>
                          Student Profile & Diagnostic Graph: {activeStudentDisplayName}
                        </h3>
                        <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                          Student ID: <code style={{ color: 'var(--accent-cyan)' }}>{studentId}</code> • Teacher Universal Inspection Access
                        </p>
                      </div>
                      <button
                        className="btn btn-secondary"
                        onClick={() => setActiveTab('heatmap')}
                        style={{ fontSize: '12px', padding: '8px 16px' }}
                      >
                        ← Back to Class Heatmap
                      </button>
                    </div>

                    <KnowledgeGraphExplorer
                      studentId={studentId}
                      studentName={activeStudentDisplayName}
                      onPracticeConcept={() => {}}
                    />
                  </div>
                )}
              </>
            )}
          </>
        )}
      </main>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
};

export default App;
