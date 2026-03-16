/**
 * Dashboard Page — top-level overview with KPI cards and summary widgets.
 *
 * Displays: overdue submissions KPI, open CAPAs KPI, audit score gauge,
 * submission timeline, and CAPA board summary.
 */

export default function DashboardPage() {
  return (
    <div>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1.5rem' }}>
        Dashboard
      </h1>
      <p style={{ color: 'hsl(215 20% 65%)' }}>
        Overview of regulatory submission deadlines, QC status, CAPA lifecycle, and audit readiness.
      </p>

      {/* KPI Cards row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginTop: '1.5rem' }}>
        {[
          { label: 'Overdue Submissions', value: '—', color: 'hsl(0 62% 50%)' },
          { label: 'Open CAPAs', value: '—', color: 'hsl(38 92% 50%)' },
          { label: 'Audit Readiness', value: '—%', color: 'hsl(142 76% 36%)' },
          { label: 'QC Pass Rate', value: '—%', color: 'hsl(199 89% 48%)' },
        ].map((kpi) => (
          <div
            key={kpi.label}
            style={{
              backgroundColor: 'hsl(222 47% 8%)',
              borderRadius: 8,
              padding: '1.25rem',
              border: '1px solid hsl(217 33% 17%)',
            }}
          >
            <p style={{ fontSize: '0.75rem', color: 'hsl(215 20% 65%)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              {kpi.label}
            </p>
            <p style={{ fontSize: '1.75rem', fontWeight: 700, color: kpi.color, marginTop: 4 }}>
              {kpi.value}
            </p>
          </div>
        ))}
      </div>

      {/* Placeholder sections */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1rem', marginTop: '1.5rem' }}>
        <div style={{ backgroundColor: 'hsl(222 47% 8%)', borderRadius: 8, padding: '1.25rem', border: '1px solid hsl(217 33% 17%)', minHeight: 300 }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600 }}>Submission Timeline</h2>
          <p style={{ color: 'hsl(215 20% 65%)', fontSize: '0.85rem', marginTop: 8 }}>
            Gantt chart of upcoming submission milestones will render here.
          </p>
        </div>
        <div style={{ backgroundColor: 'hsl(222 47% 8%)', borderRadius: 8, padding: '1.25rem', border: '1px solid hsl(217 33% 17%)', minHeight: 300 }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600 }}>CAPA Board</h2>
          <p style={{ color: 'hsl(215 20% 65%)', fontSize: '0.85rem', marginTop: 8 }}>
            Kanban-style CAPA status board will render here.
          </p>
        </div>
      </div>
    </div>
  );
}
