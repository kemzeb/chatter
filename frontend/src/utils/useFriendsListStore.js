import { create } from 'zustand';
import genericListSlice from './genericListSlice';

const useFriendsListStore = create((set, get) => ({
  ...genericListSlice(set, get),
  setFriendsList: (newList) => get().setItems(newList),
  addFriend: ({ id, username }) => get().addItem({ id: id, username: username })
}));

export default useFriendsListStore;
