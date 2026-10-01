// Main Renderers Orchestrator

import { appState } from '../state.js';
import { renderSummary } from './summary.js';
import { renderPositions } from './positions.js';
import { renderCosting } from './costing.js';
import { renderCutting } from './cutting.js';
import { renderPlates, renderTimber } from './specs.js';
import { renderFinancials } from './financials.js';
import { renderClientKP, renderInternalEstimate } from './quotes.js';
import { renderWorkorders } from './workorders.js';

export function renderAll() {
  if (!appState.data || !appState.cost) return;

  renderSummary();
  renderPositions();
  renderCosting();
  renderCutting();
  renderPlates();
  renderTimber();
  renderFinancials();
  renderClientKP();
  renderInternalEstimate();
  renderWorkorders();
}

export {
  renderSummary,
  renderPositions,
  renderCosting,
  renderCutting,
  renderPlates,
  renderTimber,
  renderFinancials,
  renderClientKP,
  renderInternalEstimate,
  renderWorkorders
};
