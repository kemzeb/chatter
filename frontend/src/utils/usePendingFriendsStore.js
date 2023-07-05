import { create } from 'zustand';

const usePendingFriendsStore = create((set, get) => ({
  pendingFriends: null,
  setPendingFriends: (list) => {
    set(() => ({
      pendingFriends: [...list]
    }));
  },
  addPendingFriend: ({ id, requester }) => {
    if (!get().pendingFriends) return;
    const pending = { id: id, requester: requester };
    set((state) => ({
      pendingFriends: [...state.pendingFriends, pending]
    }));
  },
  removePendingFriend: (id) => {
    set((state) => ({
      pendingFriends: state.pendingFriends.filter((pending) => pending.id !== id)
    }));
  }
}));

export default usePendingFriendsStore;
