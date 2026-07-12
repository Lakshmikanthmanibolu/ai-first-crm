import { configureStore } from '@reduxjs/toolkit';
import hcpReducer from './slices/hcpSlice.js';
import interactionReducer from './slices/interactionSlice.js';
import chatReducer from './slices/chatSlice.js';
import productReducer from './slices/productSlice.js';

export const store = configureStore({
  reducer: {
    hcps: hcpReducer,
    interactions: interactionReducer,
    chat: chatReducer,
    products: productReducer,
  },
});
