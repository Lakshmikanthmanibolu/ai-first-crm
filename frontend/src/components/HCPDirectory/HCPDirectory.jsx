import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchHCPs, fetchHCPInsights } from '../../store/slices/hcpSlice.js';
import {
  Search, MapPin, Building2, Phone, Mail, Activity,
  Star, Users, Brain, Target, Package, MessageSquare,
  TrendingUp, ChevronDown, ChevronUp, Sparkles, X,
  CheckCircle2, Clock, BarChart3
} from 'lucide-react';

export default function HCPDirectory() {
  const dispatch = useDispatch();
  const { list: hcps, loading, insights, insightsLoading } = useSelector((s) => s.hcps);
  const [search, setSearch] = useState('');
  const [filterSpecialty, setFilterSpecialty] = useState('');
  const [selectedHCPId, setSelectedHCPId] = useState(null);

  useEffect(() => {
    dispatch(fetchHCPs());
  }, [dispatch]);

  const specialties = [...new Set(hcps.map((h) => h.specialty))];

  const filtered = hcps.filter((h) => {
    const matchSearch = !search || 
      `${h.first_name} ${h.last_name}`.toLowerCase().includes(search.toLowerCase()) ||
      h.institution?.toLowerCase().includes(search.toLowerCase());
    const matchSpec = !filterSpecialty || h.specialty === filterSpecialty;
    return matchSearch && matchSpec;
  });

  const getTierColor = (tier) => {
    switch (tier) {
      case 'A': return 'var(--accent-emerald)';
      case 'B': return 'var(--accent-amber)';
      case 'C': return 'var(--text-tertiary)';
      default: return 'var(--text-muted)';
    }
  };

  const handleCardClick = (hcpId) => {
    if (selectedHCPId === hcpId) {
      setSelectedHCPId(null);
    } else {
      setSelectedHCPId(hcpId);
      dispatch(fetchHCPInsights(hcpId));
    }
  };

  const getSentimentColor = (s) => {
    if (s === 'positive') return 'var(--success)';
    if (s === 'negative') return 'var(--error)';
    return 'var(--text-tertiary)';
  };

  return (
    <div>
      {/* Search & Filter Bar */}
      <div style={{ display: 'flex', gap: 'var(--space-md)', marginBottom: 'var(--space-xl)' }}>
        <div className="search-bar" style={{ flex: 1 }}>
          <Search size={16} className="search-icon" />
          <input
            className="form-input"
            type="text"
            placeholder="Search by name or institution..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ paddingLeft: 36 }}
          />
        </div>
        <select
          className="form-select"
          value={filterSpecialty}
          onChange={(e) => setFilterSpecialty(e.target.value)}
          style={{ width: 200 }}
        >
          <option value="">All Specialties</option>
          {specialties.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {/* Results Count */}
      <div style={{ fontSize: '0.82rem', color: 'var(--text-tertiary)', marginBottom: 'var(--space-lg)' }}>
        <Users size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 6 }} />
        {filtered.length} HCP{filtered.length !== 1 ? 's' : ''} found
      </div>

      {loading ? (
        <div className="loading-overlay"><div className="spinner" /></div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 'var(--space-lg)' }}>
          {filtered.map((hcp) => {
            const isSelected = selectedHCPId === hcp.id;
            return (
              <div key={hcp.id} className={`hcp-card animate-in ${isSelected ? 'expanded' : ''}`} onClick={() => handleCardClick(hcp.id)}>
                <div className="hcp-card-header">
                  <div className="hcp-avatar">
                    {hcp.first_name[0]}{hcp.last_name[0]}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div className="hcp-name">Dr. {hcp.first_name} {hcp.last_name}</div>
                    <div className="hcp-specialty">{hcp.specialty}</div>
                  </div>
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: 4,
                    padding: '2px 8px', borderRadius: 'var(--radius-full)',
                    background: 'var(--surface-glass)',
                    fontSize: '0.72rem', fontWeight: 700,
                    color: getTierColor(hcp.tier),
                  }}>
                    <Star size={10} />
                    Tier {hcp.tier}
                  </div>
                </div>

                <div className="hcp-meta">
                  {hcp.institution && (
                    <div className="hcp-meta-item">
                      <Building2 size={12} />
                      {hcp.institution}
                    </div>
                  )}
                  {hcp.city && (
                    <div className="hcp-meta-item">
                      <MapPin size={12} />
                      {hcp.city}, {hcp.state}
                    </div>
                  )}
                  {hcp.phone && (
                    <div className="hcp-meta-item">
                      <Phone size={12} />
                      {hcp.phone}
                    </div>
                  )}
                  {hcp.email && (
                    <div className="hcp-meta-item">
                      <Mail size={12} />
                      {hcp.email}
                    </div>
                  )}
                </div>

                <div style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  marginTop: 'var(--space-lg)', paddingTop: 'var(--space-md)',
                  borderTop: '1px solid var(--border-subtle)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', color: 'var(--text-tertiary)' }}>
                    <Activity size={12} />
                    {hcp.interaction_count || 0} interaction{hcp.interaction_count !== 1 ? 's' : ''}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                    <span className="badge badge-indigo">{hcp.territory}</span>
                    {isSelected ? <ChevronUp size={14} style={{ color: 'var(--text-muted)' }} /> : <ChevronDown size={14} style={{ color: 'var(--text-muted)' }} />}
                  </div>
                </div>

                {/* AI Insights Panel */}
                {isSelected && (
                  <div className="hcp-insights-panel" onClick={(e) => e.stopPropagation()}>
                    <div className="hcp-insights-header">
                      <Brain size={14} style={{ color: 'var(--accent-violet)' }} />
                      <span>AI Insights</span>
                      {insightsLoading && <div className="spinner" style={{ width: 14, height: 14 }} />}
                    </div>

                    {insights && insights.hcp_id === hcp.id && (
                      <div className="hcp-insights-content">
                        {/* Conversion Probability */}
                        <div className="hcp-insight-row">
                          <div className="hcp-insight-label"><TrendingUp size={12} /> Conversion Probability</div>
                          <div className="hcp-insight-progress-wrapper">
                            <div className="hcp-insight-progress">
                              <div className="hcp-insight-progress-bar" style={{
                                width: `${insights.conversion_probability}%`,
                                background: insights.conversion_probability > 70 ? 'var(--accent-emerald)' : insights.conversion_probability > 40 ? 'var(--accent-amber)' : 'var(--accent-rose)',
                              }} />
                            </div>
                            <span className="hcp-insight-progress-value">{insights.conversion_probability}%</span>
                          </div>
                        </div>

                        {/* Recommended Product */}
                        {insights.recommended_product && (
                          <div className="hcp-insight-row">
                            <div className="hcp-insight-label"><Package size={12} /> Recommended Product</div>
                            <div className="hcp-insight-product">
                              <div className="hcp-insight-product-name">{insights.recommended_product}</div>
                              <div className="hcp-insight-product-reason">{insights.recommended_product_reason}</div>
                            </div>
                          </div>
                        )}

                        {/* Communication Style */}
                        <div className="hcp-insight-row">
                          <div className="hcp-insight-label"><MessageSquare size={12} /> Communication Style</div>
                          <div className="hcp-insight-value-text">{insights.communication_style}</div>
                        </div>

                        {/* Preferred Meeting Type */}
                        {insights.preferred_meeting_type && (
                          <div className="hcp-insight-row">
                            <div className="hcp-insight-label"><Clock size={12} /> Preferred Meeting</div>
                            <div className="hcp-insight-value-text">{insights.preferred_meeting_type}</div>
                          </div>
                        )}

                        {/* Avg Sentiment */}
                        <div className="hcp-insight-row">
                          <div className="hcp-insight-label"><BarChart3 size={12} /> Avg Sentiment</div>
                          <span className={`badge ${insights.avg_sentiment === 'positive' ? 'badge-success' : insights.avg_sentiment === 'negative' ? 'badge-error' : 'badge-neutral'}`}>
                            {insights.avg_sentiment}
                          </span>
                        </div>

                        {/* Interested Products */}
                        {insights.interested_products?.length > 0 && (
                          <div className="hcp-insight-row">
                            <div className="hcp-insight-label"><Sparkles size={12} /> Interested Products</div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-xs)' }}>
                              {insights.interested_products.map((p, i) => (
                                <span key={i} className="badge badge-info">{p}</span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Last Meeting Summary */}
                        {insights.last_meeting_summary && (
                          <div className="hcp-insight-row">
                            <div className="hcp-insight-label"><Clock size={12} /> Last Meeting</div>
                            <div className="hcp-insight-summary">{insights.last_meeting_summary}</div>
                          </div>
                        )}

                        {/* Pending Actions */}
                        {insights.pending_actions?.length > 0 && (
                          <div className="hcp-insight-row">
                            <div className="hcp-insight-label"><Target size={12} /> Pending Actions</div>
                            <div className="hcp-insight-actions">
                              {insights.pending_actions.map((a, i) => (
                                <div key={i} className="hcp-insight-action-item">
                                  <CheckCircle2 size={10} style={{ color: 'var(--accent-amber)' }} />
                                  {a}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
