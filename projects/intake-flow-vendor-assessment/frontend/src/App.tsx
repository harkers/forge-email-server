import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AssessmentsList from './pages/AssessmentsList'
import AssessmentDetail from './pages/AssessmentDetail'
import NewAssessment from './pages/NewAssessment'

export default function App() {
  return (
    <BrowserRouter>
      <div className="container">
        <header style={{ marginBottom: '2rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Intake Flow — Vendor Assessment</h1>
            <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>OE-PRIV-IFV-001 · ProPharma Group</p>
          </div>
        </header>
        <Routes>
          <Route path="/" element={<Navigate to="/assessments" replace />} />
          <Route path="/assessments" element={<AssessmentsList />} />
          <Route path="/assessments/new" element={<NewAssessment />} />
          <Route path="/assessments/:id" element={<AssessmentDetail />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
