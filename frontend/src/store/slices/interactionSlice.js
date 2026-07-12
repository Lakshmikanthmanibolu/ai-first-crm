import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api.js';

export const fetchInteractions = createAsyncThunk('interactions/fetchInteractions', async (params = {}) => {
  const { data } = await api.get('/api/interactions', { params });
  return data;
});

export const fetchInteractionById = createAsyncThunk('interactions/fetchById', async (id) => {
  const { data } = await api.get(`/api/interactions/${id}`);
  return data;
});

export const createInteraction = createAsyncThunk('interactions/create', async (payload) => {
  const { data } = await api.post('/api/interactions', payload);
  return data;
});

export const updateInteraction = createAsyncThunk('interactions/update', async ({ id, payload }) => {
  const { data } = await api.put(`/api/interactions/${id}`, payload);
  return data;
});

export const deleteInteraction = createAsyncThunk('interactions/delete', async (id) => {
  await api.delete(`/api/interactions/${id}`);
  return id;
});

export const fetchStats = createAsyncThunk('interactions/fetchStats', async () => {
  const { data } = await api.get('/api/interactions/stats');
  return data;
});

const interactionSlice = createSlice({
  name: 'interactions',
  initialState: {
    list: [],
    selected: null,
    loading: false,
    error: null,
    stats: null,
  },
  reducers: {
    clearSelectedInteraction: (state) => {
      state.selected = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchInteractions.fulfilled, (state, action) => { state.loading = false; state.list = action.payload; })
      .addCase(fetchInteractions.rejected, (state, action) => { state.loading = false; state.error = action.error.message; })
      .addCase(fetchInteractionById.fulfilled, (state, action) => { state.selected = action.payload; })
      .addCase(createInteraction.fulfilled, (state, action) => { state.list.unshift(action.payload); })
      .addCase(updateInteraction.fulfilled, (state, action) => {
        const idx = state.list.findIndex((i) => i.id === action.payload.id);
        if (idx !== -1) state.list[idx] = action.payload;
        if (state.selected?.id === action.payload.id) state.selected = action.payload;
      })
      .addCase(deleteInteraction.fulfilled, (state, action) => {
        state.list = state.list.filter((i) => i.id !== action.payload);
      })
      .addCase(fetchStats.fulfilled, (state, action) => { state.stats = action.payload; });
  },
});

export const { clearSelectedInteraction } = interactionSlice.actions;
export default interactionSlice.reducer;
