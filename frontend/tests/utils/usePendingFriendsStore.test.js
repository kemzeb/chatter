import { renderHook, act } from '@testing-library/react';
import { expect } from '@jest/globals';
import usePendingFriendsStore from '../../src/utils/usePendingFriendsStore';

describe('usePendingFriendsStore', () => {
  afterEach(() => act(() => usePendingFriendsStore.getState().reset()));

  it('should initialize items to []', () => {
    const { result } = renderHook(() => usePendingFriendsStore());
    expect(result.current.items).toStrictEqual([]);
  });

  it('will set items to a new array when setPendingFriends() is called ', () => {
    const { result } = renderHook(() => usePendingFriendsStore());
    const newArray = ['gek', 'korvax', "Vy'keen"];
    act(() => {
      result.current.setPendingFriends(newArray);
    });
    expect(result.current.items).toStrictEqual(newArray);
  });

  it('will add item to items when addPendingFriend() is called ', () => {
    const { result } = renderHook(() => usePendingFriendsStore());
    const item = { id: 0, requester: 'Earth Defense Force' };
    act(() => {
      result.current.addPendingFriend(item);
    });
    expect(result.current.items.length).toEqual(1);
    expect(result.current.items).toContainEqual(item);
  });

  it('will remove item from items when removePendingFriend() is called ', () => {
    const { result } = renderHook(() => usePendingFriendsStore());
    const item = { id: 1, requester: 'Brotherhood of Steel' };
    act(() => {
      result.current.addPendingFriend(item);
    });
    expect(result.current.items.length).toEqual(1);

    act(() => {
      result.current.removePendingFriend(item.id);
    });
    expect(result.current.items.length).toEqual(0);
  });
});
