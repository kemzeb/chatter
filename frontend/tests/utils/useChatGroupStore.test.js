import { renderHook, act } from '@testing-library/react';
import { expect } from '@jest/globals';
import useChatGroupStore from '../../src/utils/useChatGroupStore';

describe('useChatGroupStore', () => {
  let result = undefined;

  beforeEach(() => {
    act(() => {
      const hook = renderHook(() => useChatGroupStore());
      result = hook.result;
    });
  });
  afterEach(() => act(() => useChatGroupStore.getState().reset()));

  it('should initialize items to []', () => {
    expect(result.current.items).toStrictEqual([]);
  });

  it('will set items to a new array when setChatGroups() is called ', () => {
    const newArray = ['gek', 'korvax', "Vy'keen"];
    act(() => {
      result.current.setChatGroups(newArray);
    });
    expect(result.current.items).toStrictEqual(newArray);
  });

  it('will add item to items when addChatGroup() is called ', () => {
    const item = { id: 0, requester: 'Earth Defense Force' };
    act(() => {
      result.current.addChatGroup(item);
    });
    expect(result.current.items.length).toEqual(1);
    expect(result.current.items).toContainEqual(item);
  });
});
