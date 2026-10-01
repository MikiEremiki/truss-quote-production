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
  const kpiFrames = document.getElementById('wo-kpi-frames');
  if (kpiFrames) kpiFrames.innerText = `${wo.total_frames_count || wo.total_physical_layers || 0} шт`;

  const kpiBoards = document.getElementById('wo-kpi-boards');
  if (kpiBoards) kpiBoards.innerText = `${wo.total_boards_count || 0} шт`;

  const kpiPress = document.getElementById('wo-kpi-press');
  if (kpiPress) kpiPress.innerText = wo.total_press_points || 0;

  const kpiTimber = document.getElementById('wo-kpi-timber');
  if (kpiTimber) kpiTimber.innerText = `${(wo.total_timber_vol_m3 || 0).toFixed(4)} м³`;

  // Timber / Boards Requirement Table (Калькуляция потребности в досках)
  const boardsBody = document.getElementById('wo-boards-body');
  if (boardsBody) {
    if (!wo.boards_summary || wo.boards_summary.length === 0) {
      boardsBody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-slate-400">Нет данных по пиломатериалу</td></tr>';
    } else {
      const boardsRows = wo.boards_summary.map((b, idx) => `
        <tr class="hover:bg-slate-50 transition border-b border-slate-100">
          <td class="py-2.5 px-3 text-center text-slate-500">${idx + 1}</td>
          <td class="py-2.5 px-3 font-semibold text-slate-900">${b.section}</td>
          <td class="py-2.5 px-3 text-center text-slate-700">${(b.stock_length_m || 6.0).toFixed(1)} м</td>
          <td class="py-2.5 px-3 text-center font-bold text-teal-700">${b.total_boards} шт</td>
          <td class="py-2.5 px-3 text-right font-mono text-slate-700">${(b.total_length_m || 0).toFixed(1)} м</td>
          <td class="py-2.5 px-3 text-right font-mono font-semibold text-slate-800">${(b.total_volume_m3 || 0).toFixed(4)} м³</td>
          <td class="py-2.5 px-3 text-center text-slate-700">${b.parts_count || 0} шт</td>
          <td class="py-2.5 px-3 text-right font-mono text-amber-700">${(b.waste_pct || 0).toFixed(1)}%</td>
        </tr>
      `).join('');

      if (wo.boards_summary.length > 1) {
        const totBoards = wo.boards_summary.reduce((acc, b) => acc + (b.total_boards || 0), 0);
        const totLen = wo.boards_summary.reduce((acc, b) => acc + (b.total_length_m || 0), 0);
        const totVol = wo.boards_summary.reduce((acc, b) => acc + (b.total_volume_m3 || 0), 0);
        const totParts = wo.boards_summary.reduce((acc, b) => acc + (b.parts_count || 0), 0);
        const netLen = wo.boards_summary.reduce((acc, b) => acc + (b.net_length_m || 0), 0);
        const avgWaste = totLen > 0 ? ((totLen - netLen) / totLen * 100) : 0;

        boardsBody.innerHTML = boardsRows + `
          <tr class="bg-slate-100/90 font-bold border-t-2 border-slate-300">
            <td class="py-2.5 px-3 text-center" colspan="3">ИТОГО ПО ЗАКАЗУ:</td>
            <td class="py-2.5 px-3 text-center text-teal-800">${totBoards} шт</td>
            <td class="py-2.5 px-3 text-right font-mono">${totLen.toFixed(1)} м</td>
            <td class="py-2.5 px-3 text-right font-mono text-indigo-900">${totVol.toFixed(4)} м³</td>
            <td class="py-2.5 px-3 text-center">${totParts} шт</td>
            <td class="py-2.5 px-3 text-right font-mono text-amber-800">${avgWaste.toFixed(1)}%</td>
          </tr>
        `;
      } else {
        boardsBody.innerHTML = boardsRows;
      }
    }
  }

  // Assembly Tasks Table (Сборочные задания для стола / пресса)
  const tasksBody = document.getElementById('wo-tasks-body');
  if (tasksBody) {
    if (!wo.assembly_tasks || wo.assembly_tasks.length === 0) {
      tasksBody.innerHTML = '<tr><td colspan="7" class="text-center py-6 text-slate-400">Нет сборочных заданий</td></tr>';
    } else {
      tasksBody.innerHTML = wo.assembly_tasks.map(t => `
        <tr class="hover:bg-slate-50 transition border-b border-slate-100">
          <td class="py-2.5 px-3 font-mono font-bold text-blue-700">${t.task_id}</td>
          <td class="py-2.5 px-3 font-semibold text-slate-900">${t.frame_name}</td>
          <td class="py-2.5 px-3 text-center font-bold text-slate-800">${t.qty || 1} шт</td>
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
      platesBody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-slate-400">Нет данных по МЗП</td></tr>';
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
