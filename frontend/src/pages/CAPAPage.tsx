/**
 * CAPA Page — Kanban-style lifecycle management board.
 *
 * Features: drag-and-drop Kanban board with columns for each lifecycle stage,
 * CAPA detail panel, action management, and audit trail viewer.
 */

export default function CAPAPage() {
  const columns = ['Open', 'Investigation', 'Corrective Action', 'Verification', 'Closed'];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>CAPA Lifecycle Manager</h1>
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
          + New CAPA
        </button>
      </div>

      {/* Kanban board */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${columns.length}, 1fr)`,
        gap: '0.75rem',
        overflowX: 'auto',
      }}>
        {columns.map(col => (
          <div
            key={col}
            style={{
              backgroundColor: 'hsl(222 47% 8%)',
              borderRadius: 8,
              border: '1px solid hsl(217 33% 17%)',
              padding: '0.75rem',
              minHeight: 400,
            }}
          >
            <h3 style={{
              fontSize: '0.8rem',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: 'hsl(215 20% 65%)',
              marginBottom: '0.75rem',
              paddingBottom: '0.5rem',
              borderBottom: '1px solid hsl(217 33% 17%)',
            }}>
              {col}
            </h3>
            <p style={{ color: 'hsl(215 20% 55%)', fontSize: '0.75rem', fontStyle: 'italic' }}>
              CAPA cards will appear here
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
