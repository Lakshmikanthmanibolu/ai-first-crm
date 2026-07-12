import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchHCPs } from '../../store/slices/hcpSlice.js';
import { fetchProducts } from '../../store/slices/productSlice.js';
import { Calendar, Clock, Search, Plus, Mic } from 'lucide-react';

export default function StructuredForm() {
  const dispatch = useDispatch();
  const { list: hcps } = useSelector((s) => s.hcps);
  const draftForm = useSelector((s) => s.chat.draftForm);

  useEffect(() => {
    dispatch(fetchHCPs());
    dispatch(fetchProducts());
  }, [dispatch]);

  const formatDateForInput = (dateStr) => {
    if (!dateStr) return '04/19/2025';
    try {
      const d = new Date(dateStr);
      const mm = String(d.getMonth() + 1).padStart(2, '0');
      const dd = String(d.getDate()).padStart(2, '0');
      const yyyy = d.getFullYear();
      return `${mm}/${dd}/${yyyy}`;
    } catch {
      return dateStr;
    }
  };

  const formatTimeForInput = (dateStr) => {
    if (!dateStr) return '07:36 PM';
    try {
      const d = new Date(dateStr);
      let hours = d.getHours();
      const minutes = String(d.getMinutes()).padStart(2, '0');
      const ampm = hours >= 12 ? 'PM' : 'AM';
      hours = hours % 12;
      hours = hours ? hours : 12;
      const hh = String(hours).padStart(2, '0');
      return `${hh}:${minutes} ${ampm}`;
    } catch {
      return dateStr;
    }
  };

  // Check if materials were shared (brochures)
  const isBrochuresShared = draftForm.brochures_shared || 
    (draftForm.raw_notes && draftForm.raw_notes.toLowerCase().includes('brochure'));

  return (
    <div style={{
      padding: '24px',
      color: '#333333',
      fontFamily: 'Inter, system-ui, sans-serif',
      background: '#ffffff',
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
    }}>
      <h2 style={{
        fontSize: '1.5rem',
        fontWeight: 700,
        color: '#212529',
        margin: '0 0 10px 0',
        letterSpacing: '-0.01em'
      }}>
        Log HCP Interaction
      </h2>

      {/* Section 1: Interaction Details */}
      <div>
        <h4 style={{
          fontSize: '0.85rem',
          fontWeight: 700,
          color: '#6c757d',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          margin: '0 0 12px 0'
        }}>
          Interaction Details
        </h4>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '16px', marginBottom: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#495057', marginBottom: '6px' }}>
              HCP Name
            </label>
            <input
              type="text"
              style={{
                width: '100%',
                padding: '10px 12px',
                fontSize: '0.88rem',
                border: '1px solid #dee2e6',
                borderRadius: '6px',
                background: '#f8f9fa',
                color: '#495057',
                cursor: 'not-allowed'
              }}
              value={draftForm.hcp_name || (draftForm.hcp_id ? `Dr. ${hcps.find(h => h.id === parseInt(draftForm.hcp_id))?.first_name || ''} ${hcps.find(h => h.id === parseInt(draftForm.hcp_id))?.last_name || ''}` : '')}
              placeholder="Search or select HCP..."
              disabled
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#495057', marginBottom: '6px' }}>
              Interaction Type
            </label>
            <div style={{ position: 'relative' }}>
              <select
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  fontSize: '0.88rem',
                  border: '1px solid #dee2e6',
                  borderRadius: '6px',
                  background: '#f8f9fa',
                  color: '#495057',
                  appearance: 'none',
                  cursor: 'not-allowed'
                }}
                value={draftForm.interaction_type || 'meeting'}
                disabled
              >
                <option value="meeting">Meeting</option>
                <option value="face_to_face">Face to Face</option>
                <option value="virtual">Virtual Meeting</option>
                <option value="phone">Phone Call</option>
                <option value="email">Email</option>
              </select>
              <div style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                pointerEvents: 'none',
                color: '#6c757d',
                fontSize: '0.8rem'
              }}>
                ▼
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#495057', marginBottom: '6px' }}>
              Date
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                style={{
                  width: '100%',
                  padding: '10px 12px 10px 38px',
                  fontSize: '0.88rem',
                  border: '1px solid #dee2e6',
                  borderRadius: '6px',
                  background: '#f8f9fa',
                  color: '#495057',
                  cursor: 'not-allowed'
                }}
                value={formatDateForInput(draftForm.interaction_date)}
                disabled
              />
              <Calendar size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#6c757d' }} />
            </div>
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#495057', marginBottom: '6px' }}>
              Time
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                style={{
                  width: '100%',
                  padding: '10px 12px 10px 38px',
                  fontSize: '0.88rem',
                  border: '1px solid #dee2e6',
                  borderRadius: '6px',
                  background: '#f8f9fa',
                  color: '#495057',
                  cursor: 'not-allowed'
                }}
                value={formatTimeForInput(draftForm.interaction_date)}
                disabled
              />
              <Clock size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#6c757d' }} />
            </div>
          </div>
        </div>
      </div>

      {/* Section 2: Attendees */}
      <div>
        <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#495057', marginBottom: '6px' }}>
          Attendees
        </label>
        <input
          type="text"
          style={{
            width: '100%',
            padding: '10px 12px',
            fontSize: '0.88rem',
            border: '1px solid #dee2e6',
            borderRadius: '6px',
            background: '#f8f9fa',
            color: '#495057',
            cursor: 'not-allowed'
          }}
          placeholder="Enter names or search..."
          value={draftForm.hcp_name ? `${draftForm.hcp_name}, Alex Morgan` : ""}
          disabled
        />
      </div>

      {/* Section 3: Topics Discussed */}
      <div>
        <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#495057', marginBottom: '6px' }}>
          Topics Discussed
        </label>
        <textarea
          style={{
            width: '100%',
            padding: '10px 12px',
            fontSize: '0.88rem',
            border: '1px solid #dee2e6',
            borderRadius: '6px',
            background: '#f8f9fa',
            color: '#495057',
            resize: 'vertical',
            cursor: 'not-allowed'
          }}
          rows={3}
          placeholder="Enter key discussion points..."
          value={draftForm.raw_notes ? (draftForm.raw_notes.toLowerCase().includes('discuss') ? draftForm.raw_notes.substring(draftForm.raw_notes.indexOf('discuss')) : draftForm.raw_notes) : ''}
          disabled
        />
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          color: '#0d6efd',
          fontSize: '0.78rem',
          fontWeight: 500,
          marginTop: '6px',
          cursor: 'not-allowed'
        }}>
          <Mic size={12} />
          <span>Summarize from Voice Note (Requires Consent)</span>
        </div>
      </div>

      {/* Section 4: Materials Shared / Samples Distributed */}
      <div>
        <h4 style={{
          fontSize: '0.82rem',
          fontWeight: 700,
          color: '#495057',
          margin: '0 0 12px 0'
        }}>
          Materials Shared / Samples Distributed
        </h4>

        {/* Materials Shared */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#495057' }}>
              Materials Shared
            </label>
            <button
              type="button"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                background: '#ffffff',
                border: '1px solid #dee2e6',
                borderRadius: '4px',
                padding: '4px 8px',
                fontSize: '0.75rem',
                fontWeight: 500,
                color: '#495057',
                cursor: 'not-allowed'
              }}
              disabled
            >
              <Search size={11} /> Search/Add
            </button>
          </div>
          <div style={{ fontSize: '0.85rem', color: isBrochuresShared ? '#212529' : '#868e96', paddingLeft: '2px' }}>
            {isBrochuresShared ? "Brochures." : "No materials added."}
          </div>
        </div>

        {/* Samples Distributed */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#495057' }}>
              Samples Distributed
            </label>
            <button
              type="button"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                background: '#ffffff',
                border: '1px solid #dee2e6',
                borderRadius: '4px',
                padding: '4px 8px',
                fontSize: '0.75rem',
                fontWeight: 500,
                color: '#495057',
                cursor: 'not-allowed'
              }}
              disabled
            >
              <Plus size={11} /> Add Sample
            </button>
          </div>
          <div style={{ fontSize: '0.85rem', color: '#868e96', paddingLeft: '2px' }}>
            No samples added.
          </div>
        </div>
      </div>

      {/* Section 5: Observed/Inferred HCP Sentiment */}
      <div>
        <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#495057', marginBottom: '8px' }}>
          Observed/Inferred HCP Sentiment
        </label>
        <div style={{ display: 'flex', gap: '20px' }}>
          {[
            { value: 'positive', label: 'Positive', emoji: '😃' },
            { value: 'neutral', label: 'Neutral', emoji: '😐' },
            { value: 'negative', label: 'Negative', emoji: '🙁' }
          ].map((item) => {
            const isChecked = draftForm.sentiment?.toLowerCase() === item.value;
            return (
              <label key={item.value} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', cursor: 'not-allowed' }}>
                <input
                  type="radio"
                  name="sentiment"
                  value={item.value}
                  checked={isChecked}
                  disabled
                  style={{
                    cursor: 'not-allowed',
                    accentColor: '#0d6efd'
                  }}
                />
                <span>{item.emoji} {item.label}</span>
              </label>
            );
          })}
        </div>
      </div>

      {/* Section 6: Outcomes */}
      <div>
        <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#495057', marginBottom: '6px' }}>
          Outcomes
        </label>
        <textarea
          style={{
            width: '100%',
            padding: '10px 12px',
            fontSize: '0.88rem',
            border: '1px solid #dee2e6',
            borderRadius: '6px',
            background: '#f8f9fa',
            color: '#495057',
            resize: 'vertical',
            cursor: 'not-allowed'
          }}
          rows={3}
          placeholder="Key outcomes or agreements..."
          disabled
        />
      </div>

      {/* Section 7: Follow-up Actions */}
      <div>
        <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#495057', marginBottom: '6px' }}>
          Follow-up Actions
        </label>
        <input
          type="text"
          style={{
            width: '100%',
            padding: '10px 12px',
            fontSize: '0.88rem',
            border: '1px solid #dee2e6',
            borderRadius: '6px',
            background: '#f8f9fa',
            color: '#495057',
            cursor: 'not-allowed'
          }}
          placeholder="Key follow-up actions..."
          value={draftForm.follow_up_actions || ''}
          disabled
        />
      </div>
    </div>
  );
}
