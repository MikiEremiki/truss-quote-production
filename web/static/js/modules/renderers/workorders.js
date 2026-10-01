// Production Workorders Renderer Module

import { appState } from '../state.js';
import { fmtRub } from '../helpers.js';

export function renderWorkorders() {
  if (!appState.workorders) return;
  const wo = appState.workorders;

  // Header & Info
  const orderIdEl = document.getElementById('wo-order-id');
  if (orderIdEl) orderIdEl.innerText = wo.order_id || 'WO-—';

  const dateEl = document.getElementById('wo-created-at');
  if (dateEl) dateEl.innerText = wo.created_at || '—';

  const projEl = document.getElementById('wo-project-name');
  if (projEl) projEl.innerText = wo.project_name || '—';

  // KPI Cards
  const kpiLayers = document.getElementById('wo-kpi-layers');
  if (kpiLayers) kpiLayers.innerText = wo.total_physical_layers || 0;

  const kpiPress = document.getElementById('wo-kpi-press');
  if (kpiPress) kpiPress.innerText = wo.total_press_points || 0;

  const kpiTimber = document.getElementById('wo-kpi-timber');
  if (kpiTimber) kpiTimber.innerText = `${(wo.total_timber_vol_m3 || 0).toFixed(4)} м³`;

  // Assembly Tasks Table (Послойные наряды цеха)
  const tasksBody = document.getElementById('wo-tasks-body');
  if (tasksBody) {
    if (!wo.assembly_tasks || wo.assembly_tasks.length === 0) {
      tasksBody.innerHTML = '<tr><td colspan="8" class="text-center py-6 text-slate-400">Нет сборочных заданий</td></tr>';
    } else {
      tasksBody.innerHTML = wo.assembly_tasks.map(t => `
        <tr class="hover:bg-slate-50 transition border-b border-slate-100">
          <td class="py-2.5 px-3 font-mono font-bold text-blue-700">${t.task_id}</td>
          <td class="py-2.5 px-3 font-semibold text-slate-900">${t.frame_name}</td>
          <td class="py-2.5 px-3">
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
              Слой ${t.layer_num} из ${t.total_layers_for_frame}
            </span>
          </td>
          <td class="py-2.5 px-3 text-slate-600 text-xs">${t.packet_info}</td>
          <td class="py-2.5 px-3 text-slate-700 text-xs">
            L=${t.span_mm} мм, H=${t.height_mm} мм, ∠${t.pitch_deg}°
          </td>
          <td class="py-2.5 px-3 text-center font-bold text-slate-800">${t.press_points}</td>
          <td class="py-2.5 px-3 text-right font-mono text-slate-700">${(t.timber_vol_m3 || 0).toFixed(4)} м³</td>
          <td class="py-2.5 px-3 text-right font-mono text-slate-700">${(t.plates_m2 || 0).toFixed(3)} м²</td>
        </tr>
      `).join('');
    }
  }

  // Plates Summary Table (Сводка МЗП для пресса)
  const platesBody = document.getElementById('wo-plates-body');
  if (platesBody) {
    if (!wo.plates_summary || wo.plates_summary.length === 0) {
      platesBody.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-slate-400">Нет данных по МЗП</td></tr>';
    } else {
      platesBody.innerHTML = wo.plates_summary.map((p, idx) => `
        <tr class="hover:bg-slate-50 transition border-b border-slate-100">
          <td class="py-2 px-3 text-center text-slate-500">${idx + 1}</td>
          <td class="py-2 px-3 font-semibold text-slate-800">${p.size_str}</td>
          <td class="py-2 px-3 text-center"><span class="px-2 py-0.5 rounded bg-slate-100 font-mono text-xs">${p.gauge}</span></td>
          <td class="py-2 px-3 text-center font-bold text-slate-900">${p.total_qty} шт</td>
          <td class="py-2 px-3 text-right font-mono text-slate-700">${(p.total_area_m2 || 0).toFixed(2)} м²</td>
        </tr>
      `).join('');
    }
  }
}
