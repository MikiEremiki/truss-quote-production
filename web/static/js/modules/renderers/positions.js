// Positions Tab Renderer

import { appState } from '../state.js';
import { fmtRub } from '../helpers.js';

export function renderPositions() {
  if (!appState.cost || !appState.cost.positions) return;
  const tbody = document.getElementById('positions-custom-tbody');
  if (!tbody) return;
  const trussTypes = appState.cost.catalogs ? appState.cost.catalogs.truss_types : {};

  tbody.innerHTML = appState.cost.positions.map(p => {
    return `
      <tr class="hover:bg-slate-50 transition">
        <td class="py-3 px-3 font-bold text-slate-900">
          ${p.name}
          ${p.is_span_over_12m ? '<span class="ml-1 text-[10px] bg-amber-100 text-amber-800 px-1 py-0.5 rounded font-mono">>12м</span>' : ''}
        </td>
        <td class="py-3 px-2 font-semibold text-emerald-700">${p.total_layers}</td>
        <td class="py-3 px-2 font-mono">${p.net_vol_m3.toFixed(4)}</td>
        
        <td class="py-3 px-3">
          <input type="hidden" id="pos-type-${p.name}" value="${p.item_type}">
          <select id="pos-subtype-${p.name}" class="border rounded-md text-xs px-2 py-1 bg-white font-medium w-48 shadow-2xs" onchange="onPositionSubtypeChange('${p.name}')">
            ${Object.entries(trussTypes).map(([k, v]) => `
              <option value="${k}" ${p.subtype === k ? 'selected' : ''}>${v.label} (${v.price_m3} ₽/м³)</option>
            `).join('')}
          </select>
        </td>

        <td class="py-3 px-2 text-center">
          <input type="checkbox" id="pos-treat-${p.name}" ${p.has_treatment ? 'checked' : ''} class="w-4 h-4 text-blue-600 rounded" onchange="recalculatePositions()">
        </td>

        <td class="py-3 px-2 text-center">
          <input type="checkbox" id="pos-cut-${p.name}" ${p.has_cutting ? 'checked' : ''} class="w-4 h-4 text-blue-600 rounded" onchange="recalculatePositions()">
        </td>

        <td class="py-3 px-2 text-right">
          <input type="number" id="pos-work-${p.name}" value="${p.work_rate_sale_m3}" class="border rounded px-1.5 py-1 w-20 text-right font-medium" onchange="recalculatePositions()">
        </td>

        <td class="py-3 px-2 text-right">
          <input type="number" id="pos-margin-${p.name}" value="${p.margin_pct}" class="border rounded px-1.5 py-1 w-14 text-right font-medium" onchange="recalculatePositions()">
        </td>

        <td class="py-3 px-3 text-right font-medium text-slate-600 font-mono">${fmtRub(p.prime_cost)}</td>
        <td class="py-3 px-3 text-right font-bold text-blue-700 font-mono">${fmtRub(p.sale_price)}</td>
      </tr>
    `;
  }).join('');
}
