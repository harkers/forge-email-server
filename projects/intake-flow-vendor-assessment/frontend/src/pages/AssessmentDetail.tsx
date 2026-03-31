import { useQuery } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { assessmentsApi } from '../utils/api'

export default function AssessmentDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: assessment, isLoading } = useQuery({
    queryKey: ['assessment', id],
    queryFn: () => assessmentsApi.get(id!),
    refetchInterval: 15000,
  })

  if (isLoading) return <div className="card">Loading...</div>
  if (!assessment) return <div className="card">Assessment not found.</div>

  const STATUS_LABELS: Record<string, string> = {
    draft: 'Draft', intake_parsing: 'Intake Parsing',
    specialist_assessment: 'Specialist Assessment', gap_analysis: 'Gap Analysis',
    scoring: 'Scoring', remediation: 'Remediation',
    report_synthesis: 'Report Synthesis', pending_review: 'Pending Review',
    approved: 'Approved', rejected: 'Rejected',
  }

  return (
    <div>
      <button className="btn btn-secondary" onClick={() => navigate('/assessments')} style={{ marginBottom: '1rem' }}>
        ← Back
      </button>

      <div style={{ display: 'grid', gap: '1.5rem' }}>
        {/* Header card */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>
                {assessment.reference}
              </p>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>{assessment.vendor_id}</h2>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <span className={`status-badge status-${assessment.status}`}>
                {STATUS_LABELS[assessment.status] ?? assessment.status}
              </span>
              {assessment.risk_tier && (
                <span className={`badge badge-tier-${assessment.risk_tier}`}>
                  Tier {assessment.risk_tier}
                </span>
              )}
            </div>
          </div>
          <div style={{ marginTop: '1rem', display: 'flex', gap: '2rem', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
            <span>Step {assessment.current_step} of 9</span>
            <span>Updated {new Date(assessment.updated_at).toLocaleString('en-GB')}</span>
            <span>Trigger: {assessment.trigger_type}</span>
          </div>
        </div>

        {/* Review actions — only when pending review */}
        {assessment.status === 'pending_review' && (
          <div className="card" style={{ borderColor: 'var(--color-warning)' }}>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '1rem' }}>Human Review Required</h3>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button
                className="btn btn-primary"
                onClick={() => assessmentsApi.submitReview(assessment.id, 'approved').then(() => navigate('/assessments'))}
              >
                Approve
              </button>
              <button
                className="btn btn-danger"
                onClick={() => {
                  const notes = prompt('Rejection notes (required):')
                  if (notes) assessmentsApi.submitReview(assessment.id, 'rejected', notes).then(() => navigate('/assessments'))
                }}
              >
                Reject / Rework
              </button>
            </div>
          </div>
        )}

        {/* Pipeline step summary */}
        {assessment.intake_output && (
          <div className="card">
            <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.75rem' }}>Step 1 — Intake Output</h3>
            <pre style={{ fontSize: '0.75rem', overflow: 'auto', maxHeight: 300, color: 'var(--color-text-muted)' }}>
              {JSON.stringify(assessment.intake_output, null, 2)}
            </pre>
          </div>
        )}

        {assessment.scoring_output && (
          <div className="card">
            <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.75rem' }}>Step 5 — Scoring</h3>
            <pre style={{ fontSize: '0.75rem', overflow: 'auto', maxHeight: 300, color: 'var(--color-text-muted)' }}>
              {JSON.stringify(assessment.scoring_output, null, 2)}
            </pre>
          </div>
        )}

        {assessment.report_output && (
          <div className="card">
            <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.75rem' }}>Step 7 — Report</h3>
            <pre style={{ fontSize: '0.75rem', overflow: 'auto', maxHeight: 300, color: 'var(--color-text-muted)' }}>
              {JSON.stringify(assessment.report_output, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}
