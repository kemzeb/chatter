import { create } from 'zustand';
import genericListSlice from './genericListSlice';

const usePendingFriendsStore = create((set, get) => ({
  ...genericListSlice(set, get),
  setPendingFriends: (newPendingFriends) => get().setItems(newPendingFriends),
  addPendingFriend: ({ id, requester }) => {
    const pending = { id: id, requester: requester };
    get().addItem(pending);
  },
  removePendingFriend: (id) => get().removeItem(id)
}));

export default usePendingFriendsStore;
