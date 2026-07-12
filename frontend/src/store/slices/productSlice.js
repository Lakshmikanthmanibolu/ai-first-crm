import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api.js';

export const fetchProducts = createAsyncThunk('products/fetchProducts', async () => {
  const { data } = await api.get('/api/products');
  return data;
});

const productSlice = createSlice({
  name: 'products',
  initialState: {
    list: [],
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => { state.loading = true; })
      .addCase(fetchProducts.fulfilled, (state, action) => { state.loading = false; state.list = action.payload; })
      .addCase(fetchProducts.rejected, (state, action) => { state.loading = false; state.error = action.error.message; });
  },
});

export default productSlice.reducer;
