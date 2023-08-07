const genericListSlice = (set, get, initialState) => ({
  items: initialState || [],
  setItems: (newItems) => {
    set(() => ({
      items: [...newItems]
    }));
  },
  addItem: (item) => {
    // NOTE: If the list is empty, it means we haven't called setItems() yet, just return.
    if (!get().items || get().items.length == 0) return;
    set((state) => ({
      items: [...state.items, item]
    }));
  }
});

export default genericListSlice;
