export function getExampleChatGroups() {
  return [
    'Precursors rule',
    'The Glory of Panau',
    'Korvax Fan Club',
    'New Chat Group',
    'Blarg Planet Preservation',
    'CTF practice',
    'NCR Fan Club',
    'Yes to yes mann',
    'Great Khans Fan Club',
    'Brotherhood of Steel Fan Club',
    'What in the GECK?'
  ].map((group, index) => {
    return {
      id: index,
      name: group
    };
  });
}

export function getExampleFriends() {
  return [
    'luikangpang',
    'paganmin',
    'pattycakepraxis',
    'pacman',
    'paynes_me_max',
    'spacehunter',
    'CrateOs',
    'ancientrhodes',
    'marcopolooffical',
    'badlands',
    'dust',
    'oasis',
    'yesman',
    'drzero',
    'drekthechairman',
    'shangsungasong',
    'rayden',
    'barakathetarkata',
    'bo_rai_no'
  ].map((friend, index) => {
    return {
      id: index,
      username: friend
    };
  });
}
