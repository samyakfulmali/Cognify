import React, { useEffect, useState } from 'react';
import { fetchConcepts, fetchStudentMastery } from '../services/api';
import type { ConceptGraphData, ConceptNode, StudentMasteryResponse } from '../types';
import { BrainIcon, SparklesIcon } from './Icons';

interface KnowledgeGraphProps {
  studentId: string;
  studentName: string;
  onPracticeConcept?: (conceptId: string) => void;
}

// Fixed 2D layout coordinates for the 16 concepts DAG
const CONCEPT_COORDINATES: Record<string, { x: number; y: number }> = {
  // Level 1: Foundations
  fractions_basics: { x: 220, y: 80 },
  negative_numbers: { x: 680, y: 80 },

  // Level 2
  equivalent_fractions: { x: 140, y: 200 },
  fraction_multiplication: { x: 300, y: 200 },
  order_of_operations: { x: 600, y: 200 },
  variables_expressions: { x: 780, y: 200 },

  // Level 3
  common_denominators: { x: 140, y: 320 },
  fraction_division: { x: 300, y: 320 },
  combining_like_terms: { x: 580, y: 320 },
  one_step_equations_add: { x: 780, y: 320 },

  // Level 4
  fraction_addition: { x: 140, y: 440 },
  one_step_equations_mult: { x: 440, y: 440 },
  distributive_property: { x: 620, y: 440 },
  two_step_equations: { x: 800, y: 440 },

  // Level 5
  multi_step_equations: { x: 710, y: 560 },
  linear_inequalities: { x: 560, y: 680 },
};

export const KnowledgeGraphExplorer: React.FC<KnowledgeGraphProps> = ({
  studentId,
  studentName,
  onPracticeConcept,
}) => {
  const [graphData, setGraphData] = useState<ConceptGraphData | null>(null);
  const [masteryData, setMasteryData] = useState<StudentMasteryResponse | null>(null);
  const [selectedNode, setSelectedNode] = useState<ConceptNode | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchConcepts(), fetchStudentMastery(studentId)])
      .then(([cData, mData]) => {
        setGraphData(cData);
        setMasteryData(mData);
        if (cData.nodes.length > 0 && !selectedNode) {
          setSelectedNode(cData.nodes[0]);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [studentId]);

  const getMasteryLevel = (conceptId: string): number => {
    if (!masteryData) return 0.3;
    const item = masteryData.concepts.find((c) => c.concept_id === conceptId);
    return item ? item.p_known : 0.3;
  };

  const getMasteryColor = (p: number): { fill: string; stroke: string; label: string } => {
    if (p >= 0.85) {
      return { fill: '#10b981', stroke: '#34d399', label: 'Mastered (≥85%)' };
    }
    if (p >= 0.65) {
      return { fill: '#06b6d4', stroke: '#22d3ee', label: 'Proficient (65-84%)' };
    }
    if (p >= 0.40) {
      return { fill: '#f59e0b', stroke: '#fbbf24', label: 'In-Progress (40-64%)' };
    }
    return { fill: '#ef4444', stroke: '#f87171', label: 'Learning Gap (<40%)' };
  };

  // Check if an edge is part of an active root gap for this student
  const isRootGapEdge = (source: string, target: string): boolean => {
    if (!masteryData?.active_root_gaps) return false;
    return masteryData.active_root_gaps.some((gap) => {
      const chain = gap.prerequisite_chain || [];
      const sIdx = chain.indexOf(source);
      const tIdx = chain.indexOf(target);
      return sIdx !== -1 && tIdx !== -1 && tIdx === sIdx + 1;
    });
  };

  const categories = ['all', 'Fractions', 'Pre-Algebra', 'Algebra Basics', 'Equations', 'Inequalities'];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '24px' }}>
      {/* Main Graph Canvas Area */}
      <div className="glass-card animate-fade-in" style={{ padding: '20px' }}>
        {/* Controls & Category Filter */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '16px',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)' }}>
              Math Curriculum Concept Graph
            </h2>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Prerequisite dependencies from Fractions to Algebra • Colored by {studentName}'s mastery
            </p>
          </div>

          {/* Category Filter Pills */}
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {categories.map((cat) => (
              <button
                key={cat}
                className="btn"
                onClick={() => setFilterCategory(cat)}
                style={{
                  padding: '6px 12px',
                  fontSize: '11px',
                  borderRadius: '999px',
                  background: filterCategory === cat ? 'var(--primary)' : 'var(--bg-input)',
                  color: filterCategory === cat ? '#ffffff' : 'var(--text-secondary)',
                  border: '1px solid var(--border-color)',
                }}
              >
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Legend */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            padding: '10px 16px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--bg-input)',
            border: '1px solid var(--border-color)',
            fontSize: '12px',
            marginBottom: '16px',
            flexWrap: 'wrap',
          }}
        >
          <span style={{ fontWeight: 700, color: 'var(--text-secondary)' }}>Mastery Legend:</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#10b981' }}></span>
            <span>Mastered (≥85%)</span>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#06b6d4' }}></span>
            <span>Proficient (65-84%)</span>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#f59e0b' }}></span>
            <span>In-Progress (40-64%)</span>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#ef4444' }}></span>
            <span>Learning Gap (&lt;40%)</span>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '16px', height: '3px', background: '#f59e0b', borderRadius: '2px' }}></span>
            <span style={{ color: '#f59e0b' }}>Active Root Gap Edge</span>
          </span>
        </div>

        {/* SVG Interactive Canvas */}
        <div
          style={{
            position: 'relative',
            width: '100%',
            height: '760px',
            background: 'var(--bg-input)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--border-color)',
            overflow: 'hidden',
          }}
        >
          {loading && (
            <div style={{ textAlign: 'center', padding: '120px 0', color: 'var(--text-muted)' }}>
              Loading concept topology and Bayesian scores...
            </div>
          )}

          {graphData && (
            <svg
              width="100%"
              height="100%"
              viewBox="0 0 960 760"
              style={{ display: 'block', overflow: 'visible' }}
            >
              <defs>
                {/* Arrowhead Markers */}
                <marker
                  id="arrow-default"
                  viewBox="0 0 10 10"
                  refX="18"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="var(--graph-edge)" />
                </marker>
                <marker
                  id="arrow-active"
                  viewBox="0 0 10 10"
                  refX="18"
                  refY="5"
                  markerWidth="7"
                  markerHeight="7"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="var(--primary)" />
                </marker>
                <marker
                  id="arrow-rootgap"
                  viewBox="0 0 10 10"
                  refX="18"
                  refY="5"
                  markerWidth="8"
                  markerHeight="8"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#ef4444" />
                </marker>
              </defs>

              {/* Render Prerequisite Directed Edges */}
              {graphData.edges.map((edge, idx) => {
                const src = CONCEPT_COORDINATES[edge.source];
                const dst = CONCEPT_COORDINATES[edge.target];
                if (!src || !dst) return null;

                const isConnectedToHovered =
                  hoveredNodeId === edge.source || hoveredNodeId === edge.target;
                const isSelectedEdge =
                  selectedNode &&
                  (selectedNode.id === edge.source || selectedNode.id === edge.target);
                const isGapEdge = isRootGapEdge(edge.source, edge.target);

                const dx = dst.x - src.x;
                const dy = dst.y - src.y;
                const cx1 = src.x + dx * 0.1;
                const cy1 = src.y + dy * 0.6;
                const cx2 = dst.x - dx * 0.1;
                const cy2 = dst.y - dy * 0.6;
                const pathData = `M ${src.x} ${src.y} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${dst.x} ${dst.y}`;

                let stroke = 'var(--graph-edge)';
                let strokeWidth = 1.5;
                let marker = 'url(#arrow-default)';

                if (isGapEdge) {
                  stroke = '#ef4444';
                  strokeWidth = 3;
                  marker = 'url(#arrow-rootgap)';
                } else if (isSelectedEdge || isConnectedToHovered) {
                  stroke = 'var(--primary)';
                  strokeWidth = 2.5;
                  marker = 'url(#arrow-active)';
                }

                return (
                  <path
                    key={`edge-${idx}`}
                    d={pathData}
                    fill="none"
                    stroke={stroke}
                    strokeWidth={strokeWidth}
                    strokeDasharray={isGapEdge ? '5,4' : 'none'}
                    markerEnd={marker}
                    style={{ transition: 'stroke 0.2s, stroke-width 0.2s' }}
                  />
                );
              })}

              {/* Render Concept Nodes */}
              {graphData.nodes.map((node) => {
                const pos = CONCEPT_COORDINATES[node.id] || { x: 400, y: 300 };
                const pKnown = getMasteryLevel(node.id);
                const colorInfo = getMasteryColor(pKnown);
                const isSelected = selectedNode?.id === node.id;
                const isHovered = hoveredNodeId === node.id;
                const isDimmed = filterCategory !== 'all' && node.category !== filterCategory;

                return (
                  <g
                    key={node.id}
                    transform={`translate(${pos.x}, ${pos.y})`}
                    onClick={() => setSelectedNode(node)}
                    onMouseEnter={() => setHoveredNodeId(node.id)}
                    onMouseLeave={() => setHoveredNodeId(null)}
                    style={{
                      cursor: 'pointer',
                      opacity: isDimmed ? 0.25 : 1,
                      transition: 'opacity 0.25s ease',
                    }}
                  >
                    {(isSelected || isHovered) && (
                      <circle
                        r={34}
                        fill={colorInfo.fill}
                        opacity={0.2}
                        className={pKnown < 0.4 ? 'pulse-danger' : ''}
                      />
                    )}

                    <circle
                      r={24}
                      fill="var(--bg-secondary)"
                      stroke={isSelected ? '#ffffff' : colorInfo.fill}
                      strokeWidth={isSelected ? 3.5 : 2.5}
                      style={{
                        transition: 'transform 0.15s ease, stroke-width 0.15s ease',
                        filter: isSelected ? 'drop-shadow(0 0 8px rgba(99, 102, 241, 0.6))' : 'none',
                      }}
                    />

                    <circle r={10} fill={colorInfo.fill} />

                    <text
                      y={38}
                      textAnchor="middle"
                      fill="var(--text-primary)"
                      fontSize="11"
                      fontWeight="700"
                      fontFamily="var(--font-main)"
                      style={{ pointerEvents: 'none', userSelect: 'none' }}
                    >
                      {node.name.length > 20 ? node.name.slice(0, 18) + '..' : node.name}
                    </text>

                    <g transform="translate(0, 52)">
                      <rect
                        x="-20"
                        y="-8"
                        width="40"
                        height="16"
                        rx="4"
                        fill="var(--bg-input)"
                        stroke="var(--border-color)"
                        strokeWidth="1"
                      />
                      <text
                        textAnchor="middle"
                        y="3"
                        fill={colorInfo.fill}
                        fontSize="9.5"
                        fontWeight="700"
                        fontFamily="var(--font-mono)"
                        style={{ pointerEvents: 'none', userSelect: 'none' }}
                      >
                        {(pKnown * 100).toFixed(0)}%
                      </text>
                    </g>
                  </g>
                );
              })}
            </svg>
          )}
        </div>
      </div>

      {/* Right Column: Node Details Inspector Drawer */}
      <div className="glass-card animate-fade-in" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <BrainIcon size={20} style={{ color: 'var(--primary)' }} />
          <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Concept Inspector
          </h3>
        </div>

        {selectedNode ? (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', gap: '6px', marginBottom: '6px' }}>
                <span className="badge badge-primary">Diff {selectedNode.difficulty}</span>
                <span className="badge badge-cyan">{selectedNode.category}</span>
              </div>
              <h2 style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1.2 }}>
                {selectedNode.name}
              </h2>
            </div>

            <div
              style={{
                padding: '16px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--bg-input)',
                border: '1px solid var(--border-color)',
                marginBottom: '20px',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Student Mastery</span>
                <span
                  style={{
                    fontSize: '18px',
                    fontWeight: 800,
                    fontFamily: 'var(--font-mono)',
                    color: getMasteryColor(getMasteryLevel(selectedNode.id)).fill,
                  }}
                >
                  {(getMasteryLevel(selectedNode.id) * 100).toFixed(1)}%
                </span>
              </div>

              <div className="meter-track">
                <div
                  className="meter-fill"
                  style={{
                    width: `${Math.min(100, getMasteryLevel(selectedNode.id) * 100)}%`,
                    background: getMasteryColor(getMasteryLevel(selectedNode.id)).fill,
                  }}
                />
              </div>

              <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                Status: <strong>{getMasteryColor(getMasteryLevel(selectedNode.id)).label}</strong>
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-secondary)' }}>
                Pedagogical Scope:
              </span>
              <p
                style={{
                  fontSize: '13px',
                  color: 'var(--text-primary)',
                  lineHeight: 1.5,
                  marginTop: '4px',
                }}
              >
                {selectedNode.prerequisites.length === 0
                  ? 'Core foundational skill with no prior dependencies in this curriculum.'
                  : `Requires foundational mastery in ${selectedNode.prerequisites.join(', ')}.`}
              </p>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-secondary)' }}>
                Prerequisites ({selectedNode.prerequisites.length}):
              </span>
              <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {selectedNode.prerequisites.length > 0 ? (
                  selectedNode.prerequisites.map((prereqId) => {
                    const prereqMastery = getMasteryLevel(prereqId);
                    const color = getMasteryColor(prereqMastery).fill;
                    return (
                      <div
                        key={prereqId}
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '8px 12px',
                          borderRadius: 'var(--radius-sm)',
                          background: 'var(--bg-input)',
                          border: '1px solid var(--border-color)',
                          fontSize: '12px',
                        }}
                      >
                        <span style={{ color: 'var(--text-primary)' }}>{prereqId}</span>
                        <span style={{ fontWeight: 700, color: color, fontFamily: 'var(--font-mono)' }}>
                          {(prereqMastery * 100).toFixed(0)}%
                        </span>
                      </div>
                    );
                  })
                ) : (
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    None (Foundational Root)
                  </span>
                )}
              </div>
            </div>

            {onPracticeConcept && (
              <button
                className="btn btn-primary"
                onClick={() => onPracticeConcept(selectedNode.id)}
                style={{ width: '100%', padding: '12px', marginTop: '10px' }}
              >
                <SparklesIcon size={16} />
                <span>Practice this Concept</span>
              </button>
            )}
          </div>
        ) : (
          <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
            Click on any concept node to inspect its dependencies, mastery score, and root gaps.
          </div>
        )}
      </div>
    </div>
  );
};
