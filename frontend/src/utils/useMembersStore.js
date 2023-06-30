import { create } from 'zustand';

const useMembersStore = create((set, get) => ({
  chatGroups: {},
  setMembers: (chatId, members) => {
    set((state) => ({
      chatGroups: {
        ...state.chatGroups,
        [chatId]: members
      }
    }));
  },
  addMember: (member) => {
    const chatId = member.chat_group;
    if (!get().chatGroups[chatId]) return;

    set((state) => ({
      chatGroups: {
        ...state.chatGroups,
        [chatId]: [...state.chatGroups[chatId], member]
      }
    }));
  }
}));

export default useMembersStore;
