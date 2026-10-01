// Specifications (Plates & Timber) Renderer

import { appState } from '../state.js';

export function renderPlates() {
  if (!appState.data || !appState.data.plates) return;
  const pTbody = document.getElementById('plates-table-body');
  if (!pTbody) return;
  pTbody.innerHTML = appState.data.plates.map(p => `
    <tr class="hover:bg-slate-50 transition">
      <td class="py-3 px-4 font-bold text-slate-800">${p.truss}</td>
      <td class="py-3 px-4 font-semibold text-indigo-600">${p.size_str}</td>
      <td class="py-3 px-4"><span class="px-2 py-0.5 bg-slate-100 rounded text-xs font-mono">${p.gauge}</span></td>
      <td class="py-3 px-4 font-bold text-blue-600">${p.qty}</td>
      <td class="py-3 px-4 font-mono">${((p.depth_mm * p.length_mm) / 1000000).toFixed(2)}</td>
      <td class="py-3 px-4 font-semibold font-mono text-emerald-700">${p.area_m2.toFixed(2)}</td>
      <td class="py-3 px-4">${(p.area_m2 * 11.77).toFixed(2)}</td>
    </tr>
  `).join('');
}

export function renderTimber() {
  if (!appState.data || !appState.data.timber) return;
  const tTbody = document.getElementById('timber-table-body');
  if (!tTbody) return;
  tTbody.innerHTML = appState.data.timber.map(t => `
    <tr class="hover:bg-slate-50 transition">
      <td class="py-2.5 px-4 font-bold text-slate-800">${t.truss}</td>
      <td class="py-2.5 px-4 font-mono text-xs font-semibold text-blue-600">${t.label}</td>
      <td class="py-2.5 px-4 text-xs text-slate-500">${t.type || 'Элемент'}</td>
      <td class="py-2.5 px-4 font-semibold">${t.qty}</td>
      <td class="py-2.5 px-4"><span class="px-2 py-0.5 bg-amber-50 text-amber-800 rounded text-xs font-mono font-medium">${t.section}</span></td>
      <td class="py-2.5 px-4 font-semibold text-slate-900">${Math.round(t.length_m * 1000)}</td>
      <td class="py-2.5 px-4 text-xs">${t.grade}</td>
      <td class="py-2.5 px-4 font-mono text-xs">${t.volume_m3.toFixed(4)}</td>
      <td class="py-2.5 px-4 font-mono text-xs text-emerald-700">${t.surface_area_m2.toFixed(2)}</td>
    </tr>
  `).join('');
}
