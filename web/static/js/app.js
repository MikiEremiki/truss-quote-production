// MiTek Web Service Frontend Logic - Main Entry Point (Modular ES6)

import { appState, getAppState, setAppState } from './modules/state.js';
import { showLoading, fmtRub } from './modules/helpers.js';
import {
  fetchAppInfo,
  fetchSampleData,
  uploadMitekFile,
  apiCalculateCosting,
  apiCalculatePositions,
  apiOptimizeCutting,
  apiCalculateFinancials,
  apiCalculateAll,
  apiGenerateQuote,
  apiGenerateWorkorders
} from './modules/api.js';
import {
  switchTab,
  toggleSidebar,
  initControlsAndPresets,
  applyClientProfile,
  applyAgentPreset,
  onPositionSubtypeChange,
  collectCustomItems,
  collectPayload,
  recalculateCosting,
  recalculatePositions,
  recalculateCutting,
  recalculateFinancials,
  recalculateWorkorders,
  recalculateAll,
  loadSampleData,
  handleFileUpload,
  loadAppInfo
} from './modules/controllers.js';
import {
  renderAll,
  renderSummary,
  renderPositions,
  renderCosting,
  renderCutting,
  renderPlates,
  renderTimber,
  renderFinancials,
  renderClientKP,
  renderInternalEstimate,
  renderWorkorders,
  renderAdmin,
  handleSaveAdminAliases
} from './modules/renderers/index.js';

import { handleIfcUpload } from './modules/ifc-viewer.js';

window.handleIfcUpload = handleIfcUpload;

// Expose functions globally to window for DOM event handlers (onclick, onchange, etc.)
window.appState = appState;
window.getAppState = getAppState;
window.setAppState = setAppState;

window.showLoading = showLoading;
window.fmtRub = fmtRub;

window.switchTab = switchTab;
window.toggleSidebar = toggleSidebar;
window.initControlsAndPresets = initControlsAndPresets;
window.applyClientProfile = applyClientProfile;
window.applyAgentPreset = applyAgentPreset;
window.onPositionSubtypeChange = onPositionSubtypeChange;
window.collectCustomItems = collectCustomItems;
window.collectPayload = collectPayload;

window.recalculateCosting = recalculateCosting;
window.recalculatePositions = recalculatePositions;
window.recalculateCutting = recalculateCutting;
window.recalculateFinancials = recalculateFinancials;
window.recalculateWorkorders = recalculateWorkorders;
window.recalculateAll = recalculateAll;

window.loadSampleData = loadSampleData;
window.handleFileUpload = handleFileUpload;
window.loadAppInfo = loadAppInfo;

window.renderAll = renderAll;
window.renderSummary = renderSummary;
window.renderPositions = renderPositions;
window.renderCosting = renderCosting;
window.renderCutting = renderCutting;
window.renderPlates = renderPlates;
window.renderTimber = renderTimber;
window.renderFinancials = renderFinancials;
window.renderClientKP = renderClientKP;
window.renderInternalEstimate = renderInternalEstimate;
window.renderWorkorders = renderWorkorders;
window.renderAdmin = renderAdmin;
window.saveAdminAliases = handleSaveAdminAliases;

// Auto-load sample and info on DOM ready
window.addEventListener('DOMContentLoaded', () => {
  loadAppInfo();
  loadSampleData();

  // Support opening specific tab from URL query (?tab=admin or ?tab=tab-admin) or hash (#tab-admin)
  const urlParams = new URLSearchParams(window.location.search);
  const tabParam = urlParams.get('tab');
  if (tabParam === 'admin' || tabParam === 'tab-admin') {
    switchTab('tab-admin');
  } else if (window.location.hash) {
    const hashTab = window.location.hash.replace('#', '');
    if (hashTab === 'admin' || hashTab === 'tab-admin') {
      switchTab('tab-admin');
    }
  }
});
