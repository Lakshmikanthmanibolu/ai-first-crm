import StructuredForm from './StructuredForm.jsx';
import ChatInterface from './ChatInterface.jsx';

export default function LogInteractionScreen() {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '1.2fr 1fr',
      gap: '24px',
      alignItems: 'stretch',
      height: 'calc(100vh - 120px)',
      background: '#f8f9fa',
      padding: '24px',
      boxSizing: 'border-box'
    }}>
      {/* Left panel: Form */}
      <div style={{
        background: '#ffffff',
        border: '1px solid #dee2e6',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflowY: 'auto'
      }}>
        <StructuredForm />
      </div>

      {/* Right panel: Chat */}
      <div style={{
        background: '#ffffff',
        border: '1px solid #dee2e6',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflow: 'hidden'
      }}>
        <ChatInterface />
      </div>
    </div>
  );
}
