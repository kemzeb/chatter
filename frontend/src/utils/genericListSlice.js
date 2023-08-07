const genericListSlice = (set, get, isNullState) => ({
  items: isNullState ? null : [],
  wasInitialized: false, // This flag exists so that WS events don't change the store when setItems() hasn't been called yet.
  setItems: (newItems) => {
    set(() => ({
      wasInitialized: true,
      items: [...newItems]
    }));
  },
  addItem: (item) => {
    if (!get().items || !get().wasInitialized) return;
    set((state) => ({
      items: [...state.items, item]
    }));
  },
  removeItem: (id) => {
    if (!get().items) return;
    set((state) => ({
      items: state.items.filter((item) => item.id !== id)
    }));
  }
});

export default genericListSlice;
