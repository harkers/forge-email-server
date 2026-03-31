import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { assessmentsApi } from '../utils/api'

const SERVICE_LINES = [
  'Regulatory Affairs',
  'Pharmacovigilance',
  'Quality Assurance',
  'Clinical Operations',
  'Data Annotation and AI',
  'Medical Writing',
  'Biostatistics',
  'IT and Data Management',
]

export default function NewAssessment() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    vendor_name: '',
    registered_jurisdiction: '',
    services_in_scope: [] as string[],
    data_categories: [] as string[],
    has_special_category: false,
    has_cross_border_transfers: false,
    initiated_by: 'Stuart Harker',
    data_categories_raw: '',
  })

  const triggerMutation = useMutation({
    mutationFn: assessmentsApi.trigger,
    onSuccess: (data) => navigate(`/assessments/${data.id}`),
  })

  const toggleService = (svc: string) => {
    setForm(f => ({
      ...f,
      services_in_scope: f.services_in_scope.includes(svc)
        ? f.services_in_scope.filter(s => s !== svc)
        : [...f.services_in_scope, svc],
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const data_categories = form.data_categories_raw
      ? form.data_categories_raw.split(',').map(s => s.trim()).filter(Boolean)
      : []
    triggerMutation.mutate({
      ...form,
      data_categories,
    })
  }

  return (
    <div style={{ maxWidth: 720, margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <button className="btn btn-secondary" onClick={() => navigate('/assessments')} style={{ marginBottom: '1rem' }}>
          ← Back
        </button>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Trigger New Vendor Assessment</h2>
      </div>

      <form onSubmit={handleSubmit} className="card">
        <div className="form-group">
          <label>Vendor Name *</label>
          <input
            required
            value={form.vendor_name}
            onChange={e => setForm(f => ({ ...f, vendor_name: e.target.value }))}
            placeholder="e.g. Cytel Statistical Software"
          />
        </div>

        <div className="form-group">
          <label>Registered Jurisdiction *</label>
          <input
            required
            value={form.registered_jurisdiction}
            onChange={e => setForm(f => ({ ...f, registered_jurisdiction: e.target.value }))}
            placeholder="e.g. United Kingdom"
          />
        </div>

        <div className="form-group">
          <label>ProPharma Service Lines in Scope *</label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
            {SERVICE_LINES.map(svc => (
              <button
                key={svc}
                type="button"
                onClick={() => toggleService(svc)}
                style={{
                  padding: '0.3rem 0.75rem',
                  borderRadius: 6,
                  fontSize: '0.8rem',
                  cursor: 'pointer',
                  border: `1px solid ${form.services_in_scope.includes(svc) ? 'var(--color-accent)' : 'var(--color-border)'}`,
                  background: form.services_in_scope.includes(svc) ? 'rgba(99,102,241,0.15)' : 'transparent',
                  color: form.services_in_scope.includes(svc) ? 'var(--color-accent)' : 'var(--color-text-muted)',
                }}
              >
                {svc}
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>Data Categories (comma-separated)</label>
          <textarea
            value={form.data_categories_raw}
            onChange={e => setForm(f => ({ ...f, data_categories_raw: e.target.value }))}
            placeholder="e.g. HCP names, organisation names, clinical study identifiers, adverse event descriptions"
          />
        </div>

        <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1.5rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={form.has_special_category}
              onChange={e => setForm(f => ({ ...f, has_special_category: e.target.checked }))}
            />
            Special category data involved
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={form.has_cross_border_transfers}
              onChange={e => setForm(f => ({ ...f, has_cross_border_transfers: e.target.checked }))}
            />
            Cross-border transfers involved
          </label>
        </div>

        <div className="form-group">
          <label>Initiated By *</label>
          <input
            required
            value={form.initiated_by}
            onChange={e => setForm(f => ({ ...f, initiated_by: e.target.value }))}
          />
        </div>

        {triggerMutation.error && (
          <div style={{ color: 'var(--color-danger)', marginBottom: '1rem', fontSize: '0.875rem' }}>
            {String(triggerMutation.error)}
          </div>
        )}

        <button
          type="submit"
          className="btn btn-primary"
          disabled={triggerMutation.isPending || !form.vendor_name || !form.registered_jurisdiction || form.services_in_scope.length === 0}
        >
          {triggerMutation.isPending ? 'Starting...' : 'Start Assessment'}
        </button>
      </form>
    </div>
  )
}
