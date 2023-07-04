import { create } from 'zustand';

const usePendingFriendsStore = create((set, get) => ({
  pendingFriends: null,
  setPendingFriends: (list) => {
    set(() => ({
      pendingFriends: [...list]
    }));
  },
  addPendingFriend: ({ id, requester }) => {
    const friend = { id: id, requester: requester };
    set((state) => ({
      pendingFriends: [...state.pendingFriends, friend]
    }));
  }
}));

export default usePendingFriendsStore;
