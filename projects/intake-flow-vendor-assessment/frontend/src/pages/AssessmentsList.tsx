import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { assessmentsApi } from '../utils/api'

const STATUS_LABELS: Record<string, string> = {
  draft: 'Draft',
  intake_parsing: 'Intake Parsing',
  specialist_assessment: 'Specialist Assessment',
  gap_analysis: 'Gap Analysis',
  scoring: 'Scoring',
  remediation: 'Remediation',
  report_synthesis: 'Report Synthesis',
  pending_review: 'Pending Review',
  approved: 'Approved',
  rejected: 'Rejected',
}

export default function AssessmentsList() {
  const { data: assessments, isLoading } = useQuery({
    queryKey: ['assessments'],
    queryFn: () => assessmentsApi.list(),
    refetchInterval: 30000,
  })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 600 }}>Assessments</h2>
        <Link to="/assessments/new" className="btn btn-primary">+ New Assessment</Link>
      </div>

      {isLoading ? (
        <div className="card">Loading...</div>
      ) : !assessments?.length ? (
        <div className="card" style={{ textAlign: 'center', color: 'var(--color-text-muted)', padding: '3rem' }}>
          No assessments yet. Trigger your first vendor assessment above.
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table>
            <thead>
              <tr>
                <th>Reference</th>
                <th>Vendor</th>
                <th>Status</th>
                <th>Risk Tier</th>
                <th>Last Updated</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {assessments.map(a => (
                <tr key={a.id}>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>{a.reference}</td>
                  <td>{a.vendor_id}</td>
                  <td>
                    <span className={`status-badge status-${a.status}`}>
                      {STATUS_LABELS[a.status] ?? a.status}
                    </span>
                  </td>
                  <td>
                    {a.risk_tier ? (
                      <span className={`badge badge-tier-${a.risk_tier}`}>Tier {a.risk_tier}</span>
                    ) : <span style={{ color: 'var(--color-text-muted)' }}>—</span>}
                  </td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                    {new Date(a.updated_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
                  </td>
                  <td>
                    <Link to={`/assessments/${a.id}`} className="btn btn-secondary" style={{ padding: '0.25rem 0.75rem', fontSize: '0.8rem' }}>
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
