// State management module for MiTek Web Service

export const appState = {
  data: null,
  cost: null,
  cutting: null,
  workorders: null,
  custom_items: {}
};

export function getAppState() {
  return appState;
}

export function setAppState(newState) {
  if (newState.data !== undefined) appState.data = newState.data;
  if (newState.cost !== undefined) appState.cost = newState.cost;
  if (newState.cutting !== undefined) appState.cutting = newState.cutting;
  if (newState.workorders !== undefined) appState.workorders = newState.workorders;
  if (newState.custom_items !== undefined) appState.custom_items = newState.custom_items;
}
