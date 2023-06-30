import { create } from 'zustand';

const useMessageStore = create((set, get) => ({
  chatGroups: {},
  setMessageList: (chatId, messages) => {
    set((state) => ({
      chatGroups: {
        ...state.chatGroups,
        [chatId]: messages
      }
    }));
  },
  addMessageFromEvent: (event) => {
    const message = event.message;
    const chatId = message.chat_group;
    if (!get().chatGroups[chatId]) return;

    set((state) => ({
      chatGroups: {
        ...state.chatGroups,
        [chatId]: [...state.chatGroups[chatId], event.message]
      }
    }));
  }
}));

export default useMessageStore;
