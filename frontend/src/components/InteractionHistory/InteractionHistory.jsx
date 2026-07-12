import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchInteractions, deleteInteraction } from '../../store/slices/interactionSlice.js';
import {
  Clock, Filter, Trash2, ChevronDown, ChevronUp,
  Video, Phone, Users as UsersIcon, Mail, Coffee, Mic,
  Package, TrendingUp, Target, AlertTriangle, CheckCircle2,
  Sparkles
} from 'lucide-react';

const TYPE_ICONS = {
  face_to_face: UsersIcon,
  virtual: Video,
  phone: Phone,
  email: Mail,
  conference: Mic,
  lunch_meeting: Coffee,
};

const FILTER_CHIPS = [
  { key: 'all', label: 'All', icon: null },
  { key: 'positive', label: 'Positive', icon: TrendingUp, color: 'var(--success)' },
  { key: 'negative', label: 'Negative', icon: AlertTriangle, color: 'var(--error)' },
  { key: 'follow_up', label: 'Pending Follow-up', icon: Target, color: 'var(--warning)' },
  { key: 'completed', label: 'Completed', icon: CheckCircle2, color: 'var(--accent-emerald)' },
];

export default function InteractionHistory() {
  const dispatch = useDispatch();
  const { list: interactions, loading } = useSelector((s) => s.interactions);
  const [expandedId, setExpandedId] = useState(null);
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [activeChip, setActiveChip] = useState('all');

  useEffect(() => {
    dispatch(fetchInteractions());
  }, [dispatch]);

  const filtered = interactions.filter((ix) => {
    const matchType = !filterType || ix.interaction_type === filterType;
    const matchStatus = !filterStatus || ix.status === filterStatus;
    let matchChip = true;
    if (activeChip === 'positive') matchChip = ix.sentiment === 'positive';
    if (activeChip === 'negative') matchChip = ix.sentiment === 'negative';
    if (activeChip === 'follow_up') matchChip = ix.status === 'follow_up_required';
    if (activeChip === 'completed') matchChip = ix.status === 'completed';
    return matchType && matchStatus && matchChip;
  });

  const handleDelete = async (id) => {
    if (confirm('Delete this interaction?')) {
      dispatch(deleteInteraction(id));
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const getSentimentBadge = (sentiment) => {
    switch (sentiment) {
      case 'positive': return 'badge-success';
      case 'negative': return 'badge-error';
      default: return 'badge-neutral';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed': return 'badge-success';
      case 'follow_up_required': return 'badge-warning';
      case 'scheduled': return 'badge-info';
      case 'cancelled': return 'badge-error';
      default: return 'badge-neutral';
    }
  };

  // Generate AI Score (visual representation)
  const getAIScore = (ix) => {
    let score = 50;
    if (ix.sentiment === 'positive') score += 25;
    if (ix.sentiment === 'negative') score -= 20;
    if (ix.ai_summary) score += 10;
    if (ix.products?.length > 0) score += 10;
    if (ix.follow_up_actions) score += 5;
    return Math.min(100, Math.max(0, score));
  };

  return (
    <div>
      {/* Filter Chips */}
      <div className="filter-chips-bar">
        {FILTER_CHIPS.map((chip) => {
          const Icon = chip.icon;
          return (
            <button
              key={chip.key}
              className={`filter-chip ${activeChip === chip.key ? 'active' : ''}`}
              onClick={() => setActiveChip(chip.key)}
              style={activeChip === chip.key && chip.color ? { borderColor: chip.color, color: chip.color } : {}}
            >
              {Icon && <Icon size={12} />}
              {chip.label}
            </button>
          );
        })}
      </div>

      {/* Type & Status Filters */}
      <div style={{ display: 'flex', gap: 'var(--space-md)', marginBottom: 'var(--space-xl)', alignItems: 'center' }}>
        <Filter size={16} style={{ color: 'var(--text-tertiary)' }} />
        <select
          className="form-select"
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          style={{ width: 180 }}
        >
          <option value="">All Types</option>
          <option value="face_to_face">Face to Face</option>
          <option value="virtual">Virtual</option>
          <option value="phone">Phone</option>
          <option value="email">Email</option>
          <option value="conference">Conference</option>
          <option value="lunch_meeting">Lunch Meeting</option>
        </select>
        <select
          className="form-select"
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          style={{ width: 180 }}
        >
          <option value="">All Statuses</option>
          <option value="completed">Completed</option>
          <option value="follow_up_required">Follow-up Required</option>
          <option value="scheduled">Scheduled</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <span style={{ fontSize: '0.82rem', color: 'var(--text-tertiary)', marginLeft: 'auto' }}>
          {filtered.length} result{filtered.length !== 1 ? 's' : ''}
        </span>
      </div>

      {loading ? (
        <div className="loading-overlay"><div className="spinner" /></div>
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon"><Clock size={24} /></div>
          <h3>No interactions found</h3>
          <p>Log your first interaction using the Log Interaction screen</p>
        </div>
      ) : (
        <div className="timeline">
          {filtered.map((ix) => {
            const TypeIcon = TYPE_ICONS[ix.interaction_type] || UsersIcon;
            const isExpanded = expandedId === ix.id;
            let keyTopics = [];
            try { keyTopics = JSON.parse(ix.key_topics || '[]'); } catch { /* ignore */ }
            const aiScore = getAIScore(ix);

            return (
              <div key={ix.id} className="timeline-item animate-in">
                <div className="timeline-card" onClick={() => setExpandedId(isExpanded ? null : ix.id)} style={{ cursor: 'pointer' }}>
                  {/* Header */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
                    <div className="timeline-type-icon">
                      <TypeIcon size={16} />
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', flexWrap: 'wrap' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>
                          {ix.hcp_name || `HCP #${ix.hcp_id}`}
                        </span>
                        <span className={`badge ${getSentimentBadge(ix.sentiment)}`}>
                          {ix.sentiment || 'N/A'}
                        </span>
                        <span className={`badge ${getStatusBadge(ix.status)}`}>
                          {ix.status?.replace(/_/g, ' ')}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)', marginTop: 2 }}>
                        {ix.interaction_type?.replace(/_/g, ' ')} · {ix.channel?.replace(/_/g, ' ')} · {ix.duration_minutes} min
                      </div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 'var(--space-xs)', flexShrink: 0 }}>
                      <div className="timeline-date">{formatDate(ix.interaction_date)}</div>
                      {/* AI Score */}
                      <div className="ai-score-badge" style={{
                        color: aiScore >= 70 ? 'var(--accent-emerald)' : aiScore >= 40 ? 'var(--accent-amber)' : 'var(--accent-rose)',
                      }}>
                        <Sparkles size={10} />
                        <span>{aiScore}%</span>
                      </div>
                      {isExpanded ? <ChevronUp size={14} style={{ color: 'var(--text-muted)' }} /> : <ChevronDown size={14} style={{ color: 'var(--text-muted)' }} />}
                    </div>
                  </div>

                  {/* Products */}
                  {ix.products?.length > 0 && (
                    <div style={{ display: 'flex', gap: 'var(--space-xs)', marginTop: 'var(--space-sm)', flexWrap: 'wrap' }}>
                      {ix.products.map((p) => (
                        <span key={p.id} className="badge badge-info" style={{ fontSize: '0.7rem' }}>
                          <Package size={9} /> {p.name}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Summary */}
                  <div style={{ marginTop: 'var(--space-md)', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    {ix.ai_summary || ix.raw_notes?.substring(0, 150) || 'No notes'}
                  </div>

                  {/* Follow-up indicator */}
                  {ix.follow_up_actions && (
                    <div className="interaction-followup-tag">
                      <Target size={11} />
                      {ix.follow_up_actions}
                    </div>
                  )}

                  {/* Expanded Details */}
                  {isExpanded && (
                    <div style={{ marginTop: 'var(--space-lg)', paddingTop: 'var(--space-lg)', borderTop: '1px solid var(--border-subtle)' }}>
                      {/* Raw Notes */}
                      {ix.raw_notes && (
                        <div style={{ marginBottom: 'var(--space-md)' }}>
                          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-tertiary)', marginBottom: 4 }}>RAW NOTES</div>
                          <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{ix.raw_notes}</div>
                        </div>
                      )}

                      {/* Key Topics */}
                      {keyTopics.length > 0 && (
                        <div style={{ marginBottom: 'var(--space-md)' }}>
                          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-tertiary)', marginBottom: 4 }}>KEY TOPICS</div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-xs)' }}>
                            {keyTopics.map((t, i) => (
                              <span key={i} className="badge badge-indigo">{t}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Follow-up */}
                      {ix.follow_up_actions && (
                        <div style={{ marginBottom: 'var(--space-md)' }}>
                          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-tertiary)', marginBottom: 4 }}>FOLLOW-UP</div>
                          <div style={{ fontSize: '0.82rem', color: 'var(--warning)' }}>
                            {ix.follow_up_actions}
                            {ix.follow_up_date && <span style={{ color: 'var(--text-muted)' }}> · Due: {formatDate(ix.follow_up_date)}</span>}
                          </div>
                        </div>
                      )}

                      {/* Actions */}
                      <div style={{ display: 'flex', gap: 'var(--space-sm)', marginTop: 'var(--space-md)' }}>
                        <button className="btn btn-danger btn-sm" onClick={(e) => { e.stopPropagation(); handleDelete(ix.id); }}>
                          <Trash2 size={12} /> Delete
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
