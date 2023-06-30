import { create } from 'zustand';

const useChatGroupStore = create((set, get) => ({
  chatGroups: [],
  setChatGroups: (chatGroups) => {
    set(() => ({
      chatGroups: [...chatGroups]
    }));
  },
  addChatGroup: (chatGroup) => {
    set((state) => ({
      chatGroups: [...state.chatGroups, chatGroup]
    }));
  }
}));

export default useChatGroupStore;
