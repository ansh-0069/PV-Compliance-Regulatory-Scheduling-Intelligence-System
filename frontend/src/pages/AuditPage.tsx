/**
 * Audit Readiness Page — compliance scoring dashboard.
 *
 * Features: overall score gauge, dimension radar chart, score trend line,
 * and findings breakdown table.
 */

export default function AuditPage() {
  return (
    <div>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1.5rem' }}>Audit Readiness</h1>

      {/* Score gauge */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 2fr',
        gap: '1rem',
      }}>
        <div style={{
          backgroundColor: 'hsl(222 47% 8%)',
          borderRadius: 8,
          border: '1px solid hsl(217 33% 17%)',
          padding: '1.5rem',
          textAlign: 'center',
        }}>
          <p style={{ fontSize: '0.75rem', color: 'hsl(215 20% 65%)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Overall Score
          </p>
          <p style={{ fontSize: '3rem', fontWeight: 700, color: 'hsl(142 76% 36%)', marginTop: 8 }}>
            —%
          </p>
          <button style={{
            marginTop: '1rem',
            backgroundColor: 'transparent',
            color: 'hsl(217 91% 60%)',
            border: '1px solid hsl(217 91% 60%)',
            borderRadius: 6,
            padding: '0.4rem 0.75rem',
            fontSize: '0.8rem',
            cursor: 'pointer',
          }}>
            Recalculate
          </button>
        </div>

        {/* Dimension breakdown */}
        <div style={{
          backgroundColor: 'hsl(222 47% 8%)',
          borderRadius: 8,
          border: '1px solid hsl(217 33% 17%)',
          padding: '1.5rem',
        }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>Scoring Dimensions</h2>
          {[
            { label: 'Submission Timeliness', weight: '30%' },
            { label: 'QC Pass Rate', weight: '25%' },
            { label: 'CAPA Closure Rate', weight: '25%' },
            { label: 'CAPA Aging', weight: '20%' },
          ].map(d => (
            <div key={d.label} style={{
              display: 'flex',
              justifyContent: 'space-between',
              padding: '0.5rem 0',
              borderBottom: '1px solid hsl(217 33% 12%)',
              fontSize: '0.85rem',
            }}>
              <span>{d.label}</span>
              <span style={{ color: 'hsl(215 20% 65%)' }}>{d.weight}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Trend chart placeholder */}
      <div style={{
        backgroundColor: 'hsl(222 47% 8%)',
        borderRadius: 8,
        border: '1px solid hsl(217 33% 17%)',
        padding: '1.5rem',
        marginTop: '1rem',
        minHeight: 200,
      }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 600 }}>Score Trend</h2>
        <p style={{ color: 'hsl(215 20% 65%)', fontSize: '0.85rem', marginTop: 8 }}>
          Recharts line chart showing audit score trend over time will render here.
        </p>
      </div>
    </div>
  );
}
