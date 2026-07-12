import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api.js';

export const fetchHCPs = createAsyncThunk('hcps/fetchHCPs', async (params = {}) => {
  const { data } = await api.get('/api/hcps', { params });
  return data;
});

export const fetchHCPById = createAsyncThunk('hcps/fetchHCPById', async (id) => {
  const { data } = await api.get(`/api/hcps/${id}`);
  return data;
});

export const createHCP = createAsyncThunk('hcps/createHCP', async (payload) => {
  const { data } = await api.post('/api/hcps', payload);
  return data;
});

export const fetchHCPInsights = createAsyncThunk('hcps/fetchInsights', async (id) => {
  const { data } = await api.get(`/api/hcps/${id}/insights`);
  return data;
});

const hcpSlice = createSlice({
  name: 'hcps',
  initialState: {
    list: [],
    selected: null,
    loading: false,
    error: null,
    insights: null,
    insightsLoading: false,
  },
  reducers: {
    clearSelectedHCP: (state) => {
      state.selected = null;
      state.insights = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchHCPs.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchHCPs.fulfilled, (state, action) => { state.loading = false; state.list = action.payload; })
      .addCase(fetchHCPs.rejected, (state, action) => { state.loading = false; state.error = action.error.message; })
      .addCase(fetchHCPById.fulfilled, (state, action) => { state.selected = action.payload; })
      .addCase(createHCP.fulfilled, (state, action) => { state.list.push(action.payload); })
      .addCase(fetchHCPInsights.pending, (state) => { state.insightsLoading = true; })
      .addCase(fetchHCPInsights.fulfilled, (state, action) => { state.insightsLoading = false; state.insights = action.payload; })
      .addCase(fetchHCPInsights.rejected, (state) => { state.insightsLoading = false; });
  },
});

export const { clearSelectedHCP } = hcpSlice.actions;
export default hcpSlice.reducer;
