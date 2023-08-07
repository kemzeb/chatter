import { create } from 'zustand';
import genericListSlice from './genericListSlice';

const useChatGroupStore = create((set, get) => ({
  ...genericListSlice(set, get),
  setChatGroups: (newList) => get().setItems(newList),
  addChatGroup: (chatGroup) => get().addItem(chatGroup)
}));

export default useChatGroupStore;
