// Financials P&L Renderer

import { appState } from '../state.js';
import { fmtRub } from '../helpers.js';

export function renderFinancials() {
  if (!appState.cost) return;
  const str = appState.cost.structures_financials;
  const ext = appState.cost.extras_financials;
  const fin = appState.cost.financial_summary;

  const setEl = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.innerText = val;
  };

  setEl('pl-str-cost', fmtRub(str.total_cost));
  setEl('pl-str-sale', fmtRub(str.total_sale));
  setEl('pl-str-profit', `+${fmtRub(str.profit_pure_structures)}`);
  setEl('pl-str-margin', `${str.margin_pure_structures_pct.toFixed(1)} %`);

  setEl('pl-ext-cost', fmtRub(ext.total_cost));
  setEl('pl-ext-sale', fmtRub(ext.total_sale));
  setEl('pl-ext-profit', `+${fmtRub(ext.profit_extras)}`);

  setEl('pl-discount-val', `-${fmtRub(fin.discount_amount)}`);
  setEl('pl-agent-val', fmtRub(fin.agent_fee));
  setEl('pl-net-profit', `+${fmtRub(fin.dk_net_profit)}`);
}
