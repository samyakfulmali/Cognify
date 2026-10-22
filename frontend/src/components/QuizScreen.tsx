import React, { useEffect, useState } from 'react';
import { fetchNextQuestion, fetchStudentMastery, submitAnswer } from '../services/api';
import type { AnswerResponse, NextQuestionResponse, StudentMasteryResponse } from '../types';
import { AlertTriangleIcon, ArrowRightIcon, CheckIcon, CloseIcon, RefreshIcon, SparklesIcon } from './Icons';

interface QuizScreenProps {
  studentId: string;
  studentName: string;
  targetConceptId?: string | null;
  onClearTargetConcept?: () => void;
}

export const QuizScreen: React.FC<QuizScreenProps> = ({
  studentId,
  studentName,
  targetConceptId,
  onClearTargetConcept,
}) => {
  const [question, setQuestion] = useState<NextQuestionResponse | null>(null);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [answerResult, setAnswerResult] = useState<AnswerResponse | null>(null);
  const [studentMastery, setStudentMastery] = useState<StudentMasteryResponse | null>(null);
  const [selectedSubject, setSelectedSubject] = useState<string>('all');
  const [activeConceptOverride, setActiveConceptOverride] = useState<string | null>(targetConceptId || null);

  const loadQuestionAndMastery = async (
    subjectToUse: string = selectedSubject,
    conceptToUse: string | null = activeConceptOverride
  ) => {
    setLoading(true);
    setError(null);
    setSelectedOption(null);
    setAnswerResult(null);

    try {
      const subjectParam = subjectToUse === 'all' ? null : subjectToUse;
      const [qData, mData] = await Promise.all([
        fetchNextQuestion(studentId, conceptToUse, subjectParam),
        fetchStudentMastery(studentId),
      ]);
      setQuestion(qData);
      setStudentMastery(mData);
    } catch (err: any) {
      setError(err.message || 'Failed to load adaptive question');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQuestionAndMastery(selectedSubject, activeConceptOverride);
  }, [studentId]);

  useEffect(() => {
    if (targetConceptId) {
      setActiveConceptOverride(targetConceptId);
      loadQuestionAndMastery(selectedSubject, targetConceptId);
    }
  }, [targetConceptId]);

  const handleSubjectChange = (newSubject: string) => {
    setSelectedSubject(newSubject);
    setActiveConceptOverride(null);
    if (onClearTargetConcept) onClearTargetConcept();
    loadQuestionAndMastery(newSubject, null);
  };

  const handleSubmitAnswer = async () => {
    if (selectedOption === null || !question) return;

    setSubmitting(true);
    setError(null);

    try {
      const result = await submitAnswer({
        student_id: studentId,
        question_id: question.question_id,
        selected_option: selectedOption,
      });
      setAnswerResult(result);

      fetchStudentMastery(studentId)
        .then(setStudentMastery)
        .catch(console.error);
    } catch (err: any) {
      setError(err.message || 'Failed to submit answer');
    } finally {
      setSubmitting(false);
    }
  };

  const getOptionLetter = (idx: number) => String.fromCharCode(65 + idx);

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '24px' }}>
      {/* Left Column: Quiz Question & Instant Feedback */}
      <div className="glass-card animate-fade-in">
        {/* Header with recommendation reason */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '16px',
            borderBottom: '1px solid var(--border-color)',
            paddingBottom: '14px',
          }}
        >
          <div>
            <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Adaptive Question
            </span>
            <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)' }}>
              {question ? question.concept_name : 'Loading...'}
            </h2>
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            {question && (
              <>
                <span className="badge badge-cyan">{question.concept_category}</span>
                <span className="badge badge-primary">Diff {question.difficulty}</span>
              </>
            )}
            <button
              className="btn btn-secondary"
              onClick={() => loadQuestionAndMastery()}
              title="Refresh Question"
              style={{ padding: '6px 12px' }}
            >
              <RefreshIcon size={14} />
            </button>
          </div>
        </div>

        {/* Subject Switcher Bar */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '12px',
            background: 'var(--bg-input)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: '10px 14px',
            marginBottom: '16px',
            flexWrap: 'wrap',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)' }}>
              📚 Subject:
            </span>
            <select
              value={selectedSubject}
              onChange={(e) => handleSubjectChange(e.target.value)}
              className="select-dropdown"
              style={{
                fontWeight: 600,
                minWidth: '220px',
                padding: '6px 12px',
                fontSize: '13px',
                borderRadius: '8px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
              }}
            >
              <option value="all">🎯 All Subjects (AI Recommended)</option>
              <option value="Fractions">🍕 Fractions (Basics, LCM, Add/Sub, Mult, Div)</option>
              <option value="Pre-Algebra">🔢 Pre-Algebra (Negatives & PEMDAS)</option>
              <option value="Algebra Basics">📐 Algebra Basics (Variables & Expressions)</option>
              <option value="Equations">⚖️ Equations (One-Step, Two-Step, Multi-Step)</option>
              <option value="Inequalities">📊 Linear Inequalities</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {activeConceptOverride ? (
              <span className="badge badge-warning" style={{ fontSize: '11px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                Topic Locked: {activeConceptOverride}
                <button
                  type="button"
                  onClick={() => {
                    setActiveConceptOverride(null);
                    if (onClearTargetConcept) onClearTargetConcept();
                    loadQuestionAndMastery(selectedSubject, null);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'inherit',
                    cursor: 'pointer',
                    fontWeight: 'bold',
                    padding: '0 2px',
                  }}
                  title="Return to adaptive flow"
                >
                  ✕
                </button>
              </span>
            ) : selectedSubject !== 'all' ? (
              <span className="badge badge-primary" style={{ fontSize: '11px' }}>
                Subject: {selectedSubject}
              </span>
            ) : (
              <span className="badge badge-accent" style={{ fontSize: '11px' }}>
                Adaptive Mode
              </span>
            )}
          </div>
        </div>

        {/* Adaptive Recommendation Reason Banner */}
        {question && (
          <div
            style={{
              padding: '12px 16px',
              borderRadius: 'var(--radius-md)',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '10px',
              background: question.root_gap_alert
                ? 'var(--warning-glow)'
                : 'rgba(99, 102, 241, 0.08)',
              border: question.root_gap_alert
                ? '1px solid rgba(245, 158, 11, 0.35)'
                : '1px solid var(--border-accent)',
            }}
          >
            {question.root_gap_alert ? (
              <AlertTriangleIcon size={18} style={{ color: 'var(--warning)', flexShrink: 0, marginTop: '2px' }} />
            ) : (
              <SparklesIcon size={18} style={{ color: 'var(--primary)', flexShrink: 0, marginTop: '2px' }} />
            )}
            <div>
              <div
                style={{
                  fontSize: '12px',
                  fontWeight: 700,
                  color: question.root_gap_alert ? 'var(--warning)' : 'var(--primary)',
                  marginBottom: '2px',
                }}
              >
                {question.root_gap_alert ? 'Targeted Root-Gap Remediation' : 'Zone of Proximal Development (ZPD)'}
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                {question.recommendation_reason}
              </p>
            </div>
          </div>
        )}

        {/* Loading / Error states */}
        {loading && (
          <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
            <p>Fetching next adaptive question based on BKT knowledge state...</p>
          </div>
        )}

        {error && (
          <div
            style={{
              padding: '16px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--danger-glow)',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              color: 'var(--danger)',
              marginBottom: '20px',
            }}
          >
            {error}
          </div>
        )}

        {/* Question Prompt & Options */}
        {question && !loading && (
          <div>
            <div
              style={{
                fontSize: '17px',
                fontWeight: 600,
                color: 'var(--text-primary)',
                lineHeight: 1.5,
                marginBottom: '24px',
              }}
            >
              {question.prompt}
            </div>

            {/* Options List */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px', marginBottom: '24px' }}>
              {question.options.map((opt, idx) => {
                const isSelected = selectedOption === opt.id;
                const isAnswered = answerResult !== null;
                const isCorrectOption = isAnswered && answerResult.correct_option === opt.id;
                const isUserWrongChoice = isAnswered && !answerResult.is_correct && answerResult.selected_option === opt.id;

                let border = '1px solid var(--border-color)';
                let bg = 'var(--bg-input)';
                let textColor = 'var(--text-primary)';

                if (isAnswered) {
                  if (isCorrectOption) {
                    border = '2px solid var(--success)';
                    bg = 'rgba(16, 185, 129, 0.15)';
                  } else if (isUserWrongChoice) {
                    border = '2px solid var(--danger)';
                    bg = 'rgba(239, 68, 68, 0.15)';
                  }
                } else if (isSelected) {
                  border = '2px solid var(--primary)';
                  bg = 'rgba(99, 102, 241, 0.12)';
                }

                return (
                  <button
                    key={opt.id}
                    onClick={() => !isAnswered && setSelectedOption(opt.id)}
                    disabled={isAnswered}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '14px',
                      padding: '14px 18px',
                      borderRadius: 'var(--radius-md)',
                      background: bg,
                      border: border,
                      color: textColor,
                      textAlign: 'left',
                      fontSize: '15px',
                      cursor: isAnswered ? 'default' : 'pointer',
                      transition: 'all 0.2s ease',
                      outline: 'none',
                    }}
                  >
                    <div
                      style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 700,
                        fontSize: '13px',
                        background: isSelected ? 'var(--primary)' : 'var(--border-color)',
                        color: isSelected ? '#ffffff' : 'var(--text-secondary)',
                        flexShrink: 0,
                      }}
                    >
                      {getOptionLetter(idx)}
                    </div>
                    <span style={{ flex: 1, fontWeight: isSelected ? 600 : 400 }}>{opt.text}</span>
                    {isAnswered && isCorrectOption && (
                      <CheckIcon size={20} style={{ color: 'var(--success)' }} />
                    )}
                    {isAnswered && isUserWrongChoice && (
                      <CloseIcon size={20} style={{ color: 'var(--danger)' }} />
                    )}
                  </button>
                );
              })}
            </div>

            {/* Action Bar */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                {answerResult ? 'Answer evaluated' : selectedOption !== null ? 'Ready to submit' : 'Select an option'}
              </span>

              {!answerResult ? (
                <button
                  className="btn btn-primary"
                  onClick={handleSubmitAnswer}
                  disabled={selectedOption === null || submitting}
                  style={{ minWidth: '160px' }}
                >
                  {submitting ? 'Updating BKT...' : 'Submit Answer ➔'}
                </button>
              ) : (
                <button
                  className="btn btn-primary"
                  onClick={() => loadQuestionAndMastery()}
                  style={{ minWidth: '180px' }}
                >
                  <span>Next Question</span>
                  <ArrowRightIcon size={16} />
                </button>
              )}
            </div>
          </div>
        )}

        {/* Instant Misconception & Root Gap Feedback Card */}
        {answerResult && (
          <div
            className="animate-fade-in"
            style={{
              marginTop: '24px',
              padding: '20px',
              borderRadius: 'var(--radius-lg)',
              background: answerResult.is_correct
                ? 'rgba(16, 185, 129, 0.1)'
                : 'rgba(239, 68, 68, 0.08)',
              border: answerResult.is_correct
                ? '1px solid rgba(16, 185, 129, 0.35)'
                : '1px solid rgba(239, 68, 68, 0.35)',
            }}
          >
            {/* Status Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              {answerResult.is_correct ? (
                <div
                  style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    background: 'var(--success)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#ffffff',
                  }}
                >
                  <CheckIcon size={16} />
                </div>
              ) : (
                <div
                  style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    background: 'var(--danger)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#ffffff',
                  }}
                >
                  <CloseIcon size={16} />
                </div>
              )}
              <h3
                style={{
                  fontSize: '17px',
                  fontWeight: 800,
                  color: answerResult.is_correct ? 'var(--success)' : 'var(--danger)',
                }}
              >
                {answerResult.is_correct ? 'Correct! Knowledge Reinforced' : 'Incorrect Answer'}
              </h3>
            </div>

            {/* Misconception Tag (if incorrect) */}
            {!answerResult.is_correct && answerResult.misconception && (
              <div
                style={{
                  margin: '12px 0',
                  padding: '10px 14px',
                  background: 'var(--bg-input)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: 'var(--radius-md)',
                }}
              >
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    color: 'var(--danger)',
                    display: 'block',
                    marginBottom: '2px',
                  }}
                >
                  Identified Misconception
                </span>
                <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  🏷️ {answerResult.misconception.replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                </span>
              </div>
            )}

            {/* Targeted Misconception Remediation Explanation */}
            {!answerResult.is_correct && (answerResult.remediation || answerResult.misconception_explanation) && (
              <div
                style={{
                  margin: '12px 0',
                  padding: '12px 16px',
                  background: 'rgba(99, 102, 241, 0.1)',
                  border: '1px solid rgba(99, 102, 241, 0.35)',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px',
                }}
              >
                <SparklesIcon size={18} style={{ color: 'var(--primary)', flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      color: 'var(--primary)',
                      display: 'block',
                      marginBottom: '3px',
                      letterSpacing: '0.04em',
                    }}
                  >
                    Targeted Remediation
                  </span>
                  <p style={{ fontSize: '13.5px', color: 'var(--text-primary)', lineHeight: 1.5, margin: 0 }}>
                    {answerResult.remediation || answerResult.misconception_explanation}
                  </p>
                </div>
              </div>
            )}

            {/* Pedagogical Explanation */}
            <p
              style={{
                fontSize: '14px',
                color: 'var(--text-primary)',
                lineHeight: 1.5,
                margin: '10px 0 16px 0',
              }}
            >
              {answerResult.explanation}
            </p>

            {/* BKT Probability Delta Bar */}
            {(() => {
              const pBefore = answerResult.p_before !== undefined ? answerResult.p_before : answerResult.p_known_before;
              const pAfter = answerResult.p_after !== undefined ? answerResult.p_after : answerResult.p_known_after;
              const delta = pAfter - pBefore;
              const deltaPercent = (delta * 100).toFixed(1);
              const deltaFormatted = delta >= 0 ? `+${deltaPercent}%` : `${deltaPercent}%`;

              return (
                <div
                  style={{
                    padding: '12px 14px',
                    background: 'var(--bg-input)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-color)',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '12px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <span style={{ color: 'var(--text-muted)' }}>BKT P(known) on {answerResult.concept_name}:</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>{(pBefore * 100).toFixed(1)}%</span>
                    <span>➔</span>
                    <span
                      style={{
                        fontWeight: 700,
                        color: answerResult.is_correct ? 'var(--success)' : 'var(--danger)',
                      }}
                    >
                      {(pAfter * 100).toFixed(1)}%
                    </span>
                    <span
                      style={{
                        fontSize: '11px',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        background: answerResult.is_correct ? 'var(--success-glow)' : 'var(--danger-glow)',
                        color: answerResult.is_correct ? 'var(--success)' : 'var(--danger)',
                      }}
                    >
                      ({deltaFormatted})
                    </span>
                  </div>
                </div>
              );
            })()}

            {/* Root-Gap Prerequisite Diagnostic Alert (if triggered) */}
            {answerResult.root_gap && answerResult.root_gap.root_gap_found && (
              <div
                style={{
                  marginTop: '16px',
                  padding: '14px 16px',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(245, 158, 11, 0.1)',
                  border: '1px solid rgba(245, 158, 11, 0.4)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                  <AlertTriangleIcon size={16} style={{ color: 'var(--warning)' }} />
                  <span style={{ fontSize: '13px', fontWeight: 800, color: 'var(--warning)' }}>
                    Prerequisite Root Gap Detected!
                  </span>
                </div>
                <p style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.4, marginBottom: '10px' }}>
                  {answerResult.root_gap.message}
                </p>

                {/* Prerequisite Chain */}
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  Prerequisite Dependency Chain:
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                  {answerResult.root_gap.prerequisite_chain.map((cId, idx) => {
                    const isRoot = cId === answerResult.root_gap?.root_concept_id;
                    const isFailed = cId === answerResult.root_gap?.failed_concept_id;
                    let badgeClass = 'badge-primary';
                    if (isRoot) badgeClass = 'badge-danger';
                    if (isFailed) badgeClass = 'badge-warning';

                    return (
                      <React.Fragment key={cId}>
                        <span className={`badge ${badgeClass}`} style={{ fontSize: '11px' }}>
                          {isRoot ? `🚨 ${cId}` : cId}
                        </span>
                        {idx < (answerResult.root_gap?.prerequisite_chain.length || 0) - 1 && (
                          <span style={{ color: 'var(--text-muted)' }}>➔</span>
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right Column: Live Student Mastery Dashboard */}
      <div>
        <div className="glass-card animate-fade-in" style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Student Mastery Profile
            </span>
            <span className="badge badge-primary">{studentName}</span>
          </div>

          {/* Quick Metrics */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
            <div
              style={{
                padding: '14px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--bg-input)',
                border: '1px solid var(--border-color)',
              }}
            >
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Overall Mastery</div>
              <div style={{ fontSize: '24px', fontWeight: 800, color: 'var(--success)' }}>
                {studentMastery ? `${(studentMastery.overall_mastery * 100).toFixed(1)}%` : '—'}
              </div>
            </div>

            <div
              style={{
                padding: '14px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--bg-input)',
                border: '1px solid var(--border-color)',
              }}
            >
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Concepts Mastered</div>
              <div style={{ fontSize: '24px', fontWeight: 800, color: 'var(--primary)' }}>
                {studentMastery ? `${studentMastery.mastered_count} / ${studentMastery.total_concepts}` : '—'}
              </div>
            </div>
          </div>

          {/* Active Root Learning Gaps List */}
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '8px' }}>
              Active Learning Gaps ({studentMastery?.active_root_gaps.length || 0})
            </div>

            {studentMastery && studentMastery.active_root_gaps.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '300px', overflowY: 'auto' }}>
                {studentMastery.active_root_gaps.map((gap, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '10px 12px',
                      borderRadius: 'var(--radius-md)',
                      background: 'rgba(239, 68, 68, 0.08)',
                      border: '1px solid rgba(239, 68, 68, 0.25)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--danger)' }}>
                        {gap.failed_concept_name}
                      </span>
                      <span className="badge badge-danger">{(gap.p_known * 100).toFixed(0)}%</span>
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                      Root bottleneck: <strong style={{ color: 'var(--warning)' }}>{gap.root_concept_name}</strong>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div
                style={{
                  padding: '14px',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--bg-input)',
                  border: '1px solid var(--border-color)',
                  fontSize: '12px',
                  color: 'var(--text-muted)',
                  textAlign: 'center',
                }}
              >
                No active prerequisite root gaps identified.
              </div>
            )}
          </div>
        </div>

        {/* Current Concept Mastery Progress */}
        {question && (
          <div className="glass-card animate-fade-in">
            <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Target Concept Progress
            </span>
            <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', margin: '6px 0' }}>
              {question.concept_name}
            </div>

            {(() => {
              const currentScore = answerResult?.p_after !== undefined 
                ? answerResult.p_after 
                : (answerResult?.p_known_after !== undefined ? answerResult.p_known_after : question.current_mastery);
              return (
                <>
                  <div className="meter-track">
                    <div
                      className="meter-fill"
                      style={{
                        width: `${Math.min(100, currentScore * 100)}%`,
                        background:
                          currentScore >= 0.85
                            ? 'var(--success)'
                            : currentScore < 0.4
                            ? 'var(--danger)'
                            : 'linear-gradient(90deg, var(--primary), var(--accent-cyan))',
                      }}
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--text-muted)' }}>
                    <span>Initial: 30%</span>
                    <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                      {(currentScore * 100).toFixed(1)}% Mastery
                    </span>
                    <span>Target: 85%</span>
                  </div>
                </>
              );
            })()}
          </div>
        )}
      </div>
    </div>
  );
};
