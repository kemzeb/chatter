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
  ].map((value, index) => {
    return {
      id: index,
      name: value
    };
  });
}
