/**
 * QC Checks Page — upload reports for AI-powered quality control.
 *
 * Features: drag-and-drop upload panel, results list with severity indicators,
 * score gauge, and detailed findings accordion.
 */

export default function QCPage() {
  return (
    <div>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1.5rem' }}>QC AI Checker</h1>
      <p style={{ color: 'hsl(215 20% 65%)', marginBottom: '1.5rem' }}>
        Upload regulatory report sections for automated completeness and consistency analysis.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        {/* Upload panel */}
        <div style={{
          backgroundColor: 'hsl(222 47% 8%)',
          borderRadius: 8,
          border: '2px dashed hsl(217 33% 25%)',
          padding: '2rem',
          textAlign: 'center',
          minHeight: 250,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <p style={{ fontSize: '0.85rem', color: 'hsl(215 20% 65%)' }}>
            Drag & drop report section (PDF/DOCX) or click to browse
          </p>
          <button style={{
            marginTop: '1rem',
            backgroundColor: 'hsl(217 91% 60%)',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            padding: '0.5rem 1rem',
            fontSize: '0.85rem',
            cursor: 'pointer',
          }}>
            Upload for QC
          </button>
        </div>

        {/* Results panel */}
        <div style={{
          backgroundColor: 'hsl(222 47% 8%)',
          borderRadius: 8,
          border: '1px solid hsl(217 33% 17%)',
          padding: '1.25rem',
        }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>Recent QC Results</h2>
          <p style={{ color: 'hsl(215 20% 65%)', fontSize: '0.85rem' }}>
            QC check results with score gauge and findings will appear here after upload.
          </p>
        </div>
      </div>
    </div>
  );
}
