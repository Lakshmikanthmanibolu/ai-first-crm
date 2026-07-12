import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchProducts } from '../../store/slices/productSlice.js';
import { Package, Pill, Tag, FileText } from 'lucide-react';

export default function ProductCatalog() {
  const dispatch = useDispatch();
  const { list: products, loading } = useSelector((s) => s.products);

  useEffect(() => {
    dispatch(fetchProducts());
  }, [dispatch]);

  const parseKeyMessages = (km) => {
    try { return JSON.parse(km || '[]'); } catch { return []; }
  };

  const getCategoryColor = (cat) => {
    const map = {
      Cardiovascular: 'var(--accent-rose)',
      Oncology: 'var(--accent-violet)',
      Neurology: 'var(--accent-cyan)',
      Endocrinology: 'var(--accent-emerald)',
      Immunology: 'var(--accent-amber)',
    };
    return map[cat] || 'var(--accent-indigo)';
  };

  if (loading) return <div className="loading-overlay"><div className="spinner" /></div>;

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 'var(--space-lg)' }}>
        {products.map((p) => {
          const messages = parseKeyMessages(p.key_messages);
          const color = getCategoryColor(p.category);
          return (
            <div key={p.id} className="card animate-in" style={{ position: 'relative', overflow: 'hidden' }}>
              <div style={{
                position: 'absolute', top: 0, left: 0, right: 0, height: 3,
                background: color,
              }} />
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)', marginBottom: 'var(--space-md)' }}>
                <div style={{
                  width: 40, height: 40, borderRadius: 'var(--radius-md)',
                  background: `${color}20`, display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                  color: color,
                }}>
                  <Pill size={18} />
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{p.name}</div>
                  <div style={{ display: 'flex', gap: 'var(--space-sm)', marginTop: 2 }}>
                    <span className="badge" style={{ background: `${color}20`, color: color }}>{p.category}</span>
                    {p.therapeutic_area && (
                      <span className="badge badge-neutral">{p.therapeutic_area}</span>
                    )}
                  </div>
                </div>
              </div>

              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 'var(--space-md)' }}>
                {p.description}
              </p>

              {messages.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 'var(--space-sm)' }}>
                    Key Messages
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
                    {messages.map((m, i) => (
                      <div key={i} style={{
                        display: 'flex', alignItems: 'flex-start', gap: 'var(--space-sm)',
                        padding: 'var(--space-sm) var(--space-md)',
                        background: 'var(--surface-glass)',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.78rem', color: 'var(--text-secondary)',
                      }}>
                        <FileText size={12} style={{ marginTop: 2, flexShrink: 0, color: color }} />
                        {m}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
