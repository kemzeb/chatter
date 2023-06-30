import { create } from 'zustand';

const useFriendsListStore = create((set, get) => ({
  friendsList: null,
  setFriendsList: (list) => {
    set(() => ({
      friendsList: [...list]
    }));
  },
  addFriend: (friend) => {
    set((state) => ({
      friendsList: [...state.friendsList, friend]
    }));
  }
}));

export default useFriendsListStore;
