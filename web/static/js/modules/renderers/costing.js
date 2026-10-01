// Costing Breakdown Renderer

import { appState } from '../state.js';
import { fmtRub } from '../helpers.js';

export function renderCosting() {
  if (!appState.cost) return;
  const c = appState.cost.cost_items;
  const fin = appState.cost.financial_summary;
  const ind = appState.cost.indicators;
  const str = appState.cost.structures_financials;

  const costFinalPrice = document.getElementById('cost-final-price');
  if (costFinalPrice) costFinalPrice.innerText = fmtRub(fin.final_price_with_vat);

  const costPricePerM2 = document.getElementById('cost-price-per-m2');
  if (costPricePerM2) costPricePerM2.innerText = `${ind.price_per_m2_roof.toFixed(2)} ₽ / м² кровли`;

  const costPrimeTotal = document.getElementById('cost-prime-total');
  if (costPrimeTotal) costPrimeTotal.innerText = fmtRub(fin.total_cost);

  const costProfitVal = document.getElementById('cost-profit-val');
  if (costProfitVal) costProfitVal.innerText = `Чистая прибыль ДК: +${fmtRub(fin.dk_net_profit)}`;

  const badgePureProfit = document.getElementById('badge-pure-profit');
  if (badgePureProfit) badgePureProfit.innerText = `Прибыль чисто конструкций: ${fmtRub(str.profit_pure_structures)}`;

  const badgeAgentVal = document.getElementById('badge-agent-val');
  if (badgeAgentVal) badgeAgentVal.innerText = `Бонус агента: ${fmtRub(fin.agent_fee)}`;

  const setCost = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.innerText = fmtRub(val);
  };

  setCost('c-timber', c.timber_cost);
  setCost('c-plates', c.plates_cost);
  setCost('c-treatment', c.treatment_cost);
  setCost('c-fasteners', c.fasteners_cost);
  setCost('c-cutting', c.cutting_cost);
  setCost('c-assembly', c.assembly_work_cost);
  setCost('c-design', c.design_cost);
  setCost('c-logistics', c.logistics_cost);
  setCost('c-overhead', c.overhead_cost);

  const secList = document.getElementById('sections-cost-list');
  if (secList) {
    secList.innerHTML = Object.entries(appState.cost.sections_breakdown || {}).map(([sec, val]) => `
      <div class="p-3 bg-white border border-slate-200 rounded-lg text-xs space-y-1">
        <p class="font-bold text-slate-800">${sec} мм</p>
        <div class="flex justify-between text-slate-500">
          <span>Объем нетто / брутто:</span>
          <span class="font-medium text-slate-700 font-mono">${val.net_vol.toFixed(4)} / ${val.gross_vol.toFixed(4)} м³</span>
        </div>
        <div class="flex justify-between text-slate-500">
          <span>Площадь обработки:</span>
          <span class="font-medium text-emerald-700">${val.surf_m2.toFixed(2)} м²</span>
        </div>
        <div class="flex justify-between text-slate-500">
          <span>Погонаж (${val.count} дет):</span>
          <span class="font-medium text-slate-700">${val.total_length_m.toFixed(2)} м</span>
        </div>
        <div class="flex justify-between text-slate-500 pt-1 border-t">
          <span>Стоимость доски:</span>
          <span class="font-bold text-blue-600">${fmtRub(val.cost_rub)}</span>
        </div>
      </div>
    `).join('');
  }
}
