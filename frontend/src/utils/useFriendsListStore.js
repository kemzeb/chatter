import { create } from 'zustand';

const useFriendsListStore = create((set, get) => ({
  friendsList: null,
  setFriendsList: (list) => {
    set(() => ({
      friendsList: [...list]
    }));
  },
  addFriend: ({ id, username }) => {
    if (!get().friendsList) return;
    set((state) => ({
      friendsList: [...state.friendsList, { id: id, username: username }]
    }));
  }
}));

export default useFriendsListStore;
