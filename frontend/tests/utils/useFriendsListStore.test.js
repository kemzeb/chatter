import { renderHook, act } from '@testing-library/react';
import { expect } from '@jest/globals';
import useFriendsListStore from '../../src/utils/useFriendsListStore';

describe('useFriendsListStore', () => {
  afterEach(() => act(() => useFriendsListStore.setState({ items: [] })));

  it('should initialize items to []', () => {
    const { result } = renderHook(() => useFriendsListStore());
    expect(result.current.items).toStrictEqual([]);
  });

  it('will set items to a new array when setFriendsList() is called ', () => {
    const { result } = renderHook(() => useFriendsListStore());
    const newArray = ['gek', 'korvax', "Vy'keen"];
    act(() => {
      result.current.setFriendsList(newArray);
    });
    expect(result.current.items).toStrictEqual(newArray);
  });

  it('will add item to items when addItem() is called ', () => {
    const { result } = renderHook(() => useFriendsListStore());
    const item = 'Red Faction';
    act(() => {
      result.current.addItem(item);
    });
    expect(result.current.items.length).toEqual(1);
    expect(result.current.items).toContain(item);
  });
});
