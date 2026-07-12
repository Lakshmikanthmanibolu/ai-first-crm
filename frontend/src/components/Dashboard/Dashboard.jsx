import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchInteractions } from '../../store/slices/interactionSlice.js';
import { fetchHCPs } from '../../store/slices/hcpSlice.js';
import { fetchProducts } from '../../store/slices/productSlice.js';
import { fetchStats } from '../../store/slices/interactionSlice.js';
import {
  Users, MessageSquare, TrendingUp, Calendar,
  ArrowUpRight, Clock, Stethoscope, Sparkles,
  Package, AlertTriangle, UserCheck, BarChart3,
  Brain, Zap, Target, ArrowUp, ArrowDown, Minus,
  CheckCircle2, Mail, FileEdit, Search
} from 'lucide-react';

export default function Dashboard({ onNavigate }) {
  const dispatch = useDispatch();
  const { list: interactions, stats } = useSelector((s) => s.interactions);
  const { list: hcps } = useSelector((s) => s.hcps);
  const { list: products } = useSelector((s) => s.products);

  useEffect(() => {
    dispatch(fetchInteractions());
    dispatch(fetchHCPs());
    dispatch(fetchProducts());
    dispatch(fetchStats());
  }, [dispatch]);

  const followUps = interactions.filter((i) => i.status === 'follow_up_required');
  const positiveCount = interactions.filter((i) => i.sentiment === 'positive').length;
  const sentimentRate = interactions.length ? Math.round((positiveCount / interactions.length) * 100) : 0;

  const getTrendIcon = (trend) => {
    if (trend === 'up') return <ArrowUp size={12} />;
    if (trend === 'down') return <ArrowDown size={12} />;
    return <Minus size={12} />;
  };

  const ACTIVITY_ICONS = {
    'Logged': MessageSquare,
    'Summarized': Brain,
    'Follow-up Set': Calendar,
    'Edited': FileEdit,
    'Recommended': Package,
    'Searched': Search,
  };

  return (
    <div>
      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card indigo animate-in">
          <div className="stat-card-icon"><Users size={20} /></div>
          <div className="stat-value">{hcps.length}</div>
          <div className="stat-label">Healthcare Professionals</div>
          <div className="stat-trend up">
            <ArrowUp size={10} />
            <span>{stats?.interactions_this_week || 0} this week</span>
          </div>
        </div>
        <div className="stat-card cyan animate-in">
          <div className="stat-card-icon"><MessageSquare size={20} /></div>
          <div className="stat-value">{interactions.length}</div>
          <div className="stat-label">Total Interactions</div>
          <div className="stat-trend up">
            <ArrowUp size={10} />
            <span>{stats?.interactions_this_week || 0} new</span>
          </div>
        </div>
        <div className="stat-card emerald animate-in">
          <div className="stat-card-icon"><TrendingUp size={20} /></div>
          <div className="stat-value">{sentimentRate}%</div>
          <div className="stat-label">Positive Sentiment</div>
          <div className={`stat-trend ${stats?.sentiment_trend || 'stable'}`}>
            {getTrendIcon(stats?.sentiment_trend)}
            <span>{stats?.sentiment_trend === 'up' ? '+10%' : stats?.sentiment_trend === 'down' ? '-5%' : 'Stable'}</span>
          </div>
        </div>
        <div className="stat-card amber animate-in">
          <div className="stat-card-icon"><Calendar size={20} /></div>
          <div className="stat-value">{followUps.length}</div>
          <div className="stat-label">Pending Follow-ups</div>
          <div className="stat-trend neutral">
            <Target size={10} />
            <span>Action needed</span>
          </div>
        </div>
      </div>

      {/* AI Insights Section */}
      {stats && (
        <div className="ai-insights-section animate-in">
          <div className="ai-insights-header">
            <div className="ai-insights-icon">
              <Sparkles size={18} />
            </div>
            <div>
              <h3>Today's AI Insights</h3>
              <p>Powered by LangGraph Agent Analysis</p>
            </div>
          </div>
          <div className="ai-insights-grid">
            <div className="ai-insight-card violet">
              <div className="ai-insight-icon"><Package size={18} /></div>
              <div className="ai-insight-label">Most Discussed Product</div>
              <div className="ai-insight-value">{stats.most_discussed_product || 'N/A'}</div>
            </div>
            <div className="ai-insight-card cyan">
              <div className="ai-insight-icon"><UserCheck size={18} /></div>
              <div className="ai-insight-label">Highest Priority HCP</div>
              <div className="ai-insight-value">{stats.highest_priority_hcp || 'N/A'}</div>
            </div>
            <div className="ai-insight-card rose">
              <div className="ai-insight-icon"><AlertTriangle size={18} /></div>
              <div className="ai-insight-label">Negative Sentiment</div>
              <div className="ai-insight-value">{stats.negative_sentiment_hcp || 'None'}</div>
            </div>
            <div className="ai-insight-card emerald">
              <div className="ai-insight-icon"><Target size={18} /></div>
              <div className="ai-insight-label">Doctors Need Follow-up</div>
              <div className="ai-insight-value">{stats.doctors_needing_followup}</div>
            </div>
            <div className="ai-insight-card amber">
              <div className="ai-insight-icon"><BarChart3 size={18} /></div>
              <div className="ai-insight-label">Most Successful Product</div>
              <div className="ai-insight-value">{stats.most_successful_product || 'N/A'}</div>
            </div>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Recent Interactions */}
        <div className="card animate-in">
          <div className="card-header">
            <div>
              <div className="card-title">Recent Interactions</div>
              <div className="card-subtitle">Latest HCP engagements</div>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={() => onNavigate('history')}>
              View All <ArrowUpRight size={14} />
            </button>
          </div>
          {interactions.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon"><MessageSquare size={24} /></div>
              <h3>No interactions yet</h3>
              <p>Start logging interactions with HCPs</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
              {interactions.slice(0, 5).map((ix) => (
                <div key={ix.id} className="recent-interaction-item">
                  <div className="recent-interaction-icon">
                    <Stethoscope size={16} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div className="recent-interaction-name">
                      {ix.hcp_name || `HCP #${ix.hcp_id}`}
                    </div>
                    <div className="recent-interaction-summary">
                      {ix.ai_summary || ix.raw_notes?.substring(0, 60) || 'No notes'}
                    </div>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 2, flexShrink: 0 }}>
                    <span className={`badge ${ix.sentiment === 'positive' ? 'badge-success' : ix.sentiment === 'negative' ? 'badge-error' : 'badge-neutral'}`}>
                      {ix.sentiment || 'N/A'}
                    </span>
                    <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                      {ix.interaction_type?.replace(/_/g, ' ')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
          {/* Recent AI Activity */}
          {stats?.recent_ai_activity?.length > 0 && (
            <div className="card animate-in">
              <div className="card-header">
                <div>
                  <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                    <Zap size={16} style={{ color: 'var(--accent-amber)' }} />
                    Recent AI Activity
                  </div>
                  <div className="card-subtitle">Agent operations timeline</div>
                </div>
              </div>
              <div className="ai-activity-list">
                {stats.recent_ai_activity.slice(0, 5).map((act, i) => {
                  const ActIcon = ACTIVITY_ICONS[act.type] || Zap;
                  return (
                    <div key={i} className="ai-activity-item">
                      <div className="ai-activity-dot">
                        <ActIcon size={12} />
                      </div>
                      <div className="ai-activity-content">
                        <div className="ai-activity-text">
                          <span className="ai-activity-type">{act.type}</span> — {act.hcp_name}
                        </div>
                        <div className="ai-activity-meta">
                          {act.interaction_type?.replace(/_/g, ' ')} · {act.date?.split('T')[0]}
                        </div>
                      </div>
                      {act.sentiment && (
                        <span className={`badge badge-sm ${act.sentiment === 'positive' ? 'badge-success' : act.sentiment === 'negative' ? 'badge-error' : 'badge-neutral'}`}>
                          {act.sentiment}
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="card animate-in">
            <div className="card-header">
              <div className="card-title">Quick Actions</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
              <button className="btn btn-primary btn-lg" style={{ width: '100%', justifyContent: 'flex-start' }}
                onClick={() => onNavigate('log')}>
                <MessageSquare size={18} />
                Log New Interaction
              </button>
              <button className="btn btn-secondary" style={{ width: '100%', justifyContent: 'flex-start' }}
                onClick={() => onNavigate('hcps')}>
                <Users size={18} />
                Browse HCP Directory
              </button>
              <button className="btn btn-secondary" style={{ width: '100%', justifyContent: 'flex-start' }}
                onClick={() => onNavigate('history')}>
                <Clock size={18} />
                View Interaction History
              </button>
            </div>
          </div>

          {/* Follow-ups */}
          <div className="card animate-in">
            <div className="card-header">
              <div>
                <div className="card-title">Pending Follow-ups</div>
                <div className="card-subtitle">{followUps.length} action(s) required</div>
              </div>
            </div>
            {followUps.length === 0 ? (
              <div style={{ fontSize: '0.85rem', color: 'var(--text-tertiary)', padding: 'var(--space-lg) 0' }}>
                ✅ All follow-ups completed
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                {followUps.slice(0, 4).map((ix) => (
                  <div key={ix.id} className="followup-item">
                    <div className="followup-name">
                      {ix.hcp_name || `HCP #${ix.hcp_id}`}
                    </div>
                    <div className="followup-action">
                      {ix.follow_up_actions || 'Follow-up required'}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
