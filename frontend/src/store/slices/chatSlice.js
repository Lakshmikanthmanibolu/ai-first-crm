import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api.js';

export const sendMessage = createAsyncThunk('chat/sendMessage', async ({ message, conversationHistory }) => {
  const { data } = await api.post('/api/agent/chat', {
    message,
    conversation_history: conversationHistory,
  });
  return data;
});

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    loading: false,
    error: null,
    toolExecutions: [],
    workflowSteps: [],
    draftForm: {
      hcp_name: '',
      hcp_id: '',
      interaction_type: 'face_to_face',
      channel: 'in_clinic',
      interaction_date: new Date().toISOString().slice(0, 16),
      duration_minutes: 15,
      raw_notes: '',
      follow_up_actions: '',
      follow_up_date: '',
      status: 'completed',
      product_ids: [],
      rep_name: 'Alex Morgan',
      sentiment: 'neutral',
      brochures_shared: false,
    },
  },
  reducers: {
    addUserMessage: (state, action) => {
      state.messages.push({ role: 'user', content: action.payload });
    },
    clearChat: (state) => {
      state.messages = [];
      state.toolExecutions = [];
      state.workflowSteps = [];
      state.error = null;
    },
    updateDraftForm: (state, action) => {
      state.draftForm = { ...state.draftForm, ...action.payload };
    },
    resetDraftForm: (state) => {
      state.draftForm = {
        hcp_name: '',
        hcp_id: '',
        interaction_type: 'face_to_face',
        channel: 'in_clinic',
        interaction_date: new Date().toISOString().slice(0, 16),
        duration_minutes: 15,
        raw_notes: '',
        follow_up_actions: '',
        follow_up_date: '',
        status: 'completed',
        product_ids: [],
        rep_name: 'Alex Morgan',
        sentiment: 'neutral',
        brochures_shared: false,
      };
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.workflowSteps = [{ step_name: 'Analyzing Request', status: 'in_progress', description: 'Understanding your request...' }];
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.messages.push({ role: 'assistant', content: action.payload.reply });
        state.toolExecutions = action.payload.tool_executions || [];
        state.workflowSteps = action.payload.workflow_steps || [];
        if (action.payload.extracted_data) {
          state.draftForm = { ...state.draftForm, ...action.payload.extracted_data };
        }
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
        state.workflowSteps = [];
        state.messages.push({
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please check that the backend is running and the Groq API key is configured.',
        });
      });
  },
});

export const { addUserMessage, clearChat, updateDraftForm, resetDraftForm } = chatSlice.actions;
export default chatSlice.reducer;
