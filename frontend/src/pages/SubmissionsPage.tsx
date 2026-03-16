/**
 * Submissions Page — manages regulatory reporting schedules.
 *
 * Features: filterable table, schedule auto-generation, deadline timeline.
 */

export default function SubmissionsPage() {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Regulatory Submissions</h1>
        <button style={{
          backgroundColor: 'hsl(217 91% 60%)',
          color: 'white',
          border: 'none',
          borderRadius: 6,
          padding: '0.5rem 1rem',
          fontSize: '0.85rem',
          fontWeight: 500,
          cursor: 'pointer',
        }}>
          + Generate Schedule
        </button>
      </div>
      <p style={{ color: 'hsl(215 20% 65%)', marginBottom: '1rem' }}>
        Track PSUR, DSUR, and RMP submission deadlines across all products and regulatory authorities.
      </p>

      {/* Filter bar placeholder */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        {['All Types', 'EMA', 'FDA', 'Planned', 'In-Progress', 'Overdue'].map(f => (
          <span key={f} style={{
            padding: '0.35rem 0.75rem',
            borderRadius: 16,
            fontSize: '0.75rem',
            border: '1px solid hsl(217 33% 17%)',
            color: 'hsl(215 20% 65%)',
            cursor: 'pointer',
          }}>{f}</span>
        ))}
      </div>

      {/* Table placeholder */}
      <div style={{
        backgroundColor: 'hsl(222 47% 8%)',
        borderRadius: 8,
        border: '1px solid hsl(217 33% 17%)',
        padding: '2rem',
        textAlign: 'center',
        color: 'hsl(215 20% 65%)',
      }}>
        Submission table with product, type, cycle, DLP, due date, status, and authority columns will render here.
      </div>
    </div>
  );
}
