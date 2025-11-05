import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

export interface Message {
    id: string;
    text: string;
    sender: 'user' | 'bot';
    timestamp: number;
}

interface ChatState {
    messages: Message[];
    isLoading: boolean;
}

const initialState: ChatState = {
    messages: [],
    isLoading: false,
};

const chatSlice = createSlice({
    name: 'chat',
    initialState,
    reducers: {
        addMessage: (state, action: PayloadAction<Message>) => {
            state.messages.push(action.payload);
        },
        setLoading: (state, action: PayloadAction<boolean>) => {
            state.isLoading = action.payload;
        },
        clearMessages: (state) => {
            state.messages = [];
        },
    },
});

export const { addMessage, setLoading, clearMessages } = chatSlice.actions;
export default chatSlice.reducer;
