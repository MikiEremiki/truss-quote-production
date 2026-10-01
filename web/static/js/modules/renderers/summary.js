// Summary & Geometry Tab Renderer

import { appState } from '../state.js';

export function renderSummary() {
  const d = appState.data;
  if (!d) return;
  const gen = d.general || {};
  const sum = d.summary || {};

  // Display Titles
  const titleDisplay = document.getElementById('project-title-display');
  if (titleDisplay) titleDisplay.innerText = sum.project_name || 'Проект MiTek';

  const subDisplay = document.getElementById('project-sub-display');
  if (subDisplay) {
    subDisplay.innerText = `Уклон: ${sum.pitch_deg}°, Шаг: ${Math.round(sum.spacing_mm)}мм, Снег: ${gen['Snow zone (code)'] || '2.3 кН/м²'}`;
  }

  // Top KPI Cards
  const timberVol = document.getElementById('card-timber-vol');
  if (timberVol) timberVol.innerText = `${sum.total_net_timber_m3.toFixed(4)} м³`;

  const timberGross = document.getElementById('card-timber-gross');
  if (timberGross) timberGross.innerText = `+15% запас: ${(sum.total_net_timber_m3 * 1.15).toFixed(4)} м³`;

  const surfaceArea = document.getElementById('card-surface-area');
  if (surfaceArea) surfaceArea.innerText = `${sum.total_timber_surface_m2.toFixed(2)} м²`;

  const platesArea = document.getElementById('card-plates-area');
  if (platesArea) platesArea.innerText = `${sum.total_plates_area_m2.toFixed(2)} м²`;

  const platesCount = document.getElementById('card-plates-count');
  if (platesCount) platesCount.innerText = `${sum.total_plates_count} шт (~${(sum.total_plates_area_m2 * 11.77).toFixed(1)} кг)`;

  const physicalLayers = document.getElementById('card-physical-layers');
  if (physicalLayers) physicalLayers.innerText = `${sum.total_physical_layers} шт`;

  const pressPoints = document.getElementById('card-press-points');
  if (pressPoints) pressPoints.innerText = `${sum.total_press_points} точек запрессовки`;

  // Frames Table
  const fTbody = document.getElementById('frames-table-body');
  if (fTbody) {
    fTbody.innerHTML = (d.frames || []).map(f => `
      <tr class="hover:bg-slate-50 transition">
        <td class="py-3 px-4 font-bold text-slate-800">${f.name}</td>
        <td class="py-3 px-4 font-semibold text-blue-600">${f.qty}</td>
        <td class="py-3 px-4 text-slate-500">${f.plies}</td>
        <td class="py-3 px-4 font-bold text-emerald-700 bg-emerald-50/50">${f.total_layers} шт</td>
        <td class="py-3 px-4">${Math.round(f.span_mm)}</td>
        <td class="py-3 px-4">${Math.round(f.height_mm)}</td>
        <td class="py-3 px-4 font-mono">${f.vol_m3_ply.toFixed(4)}</td>
        <td class="py-3 px-4 font-mono">${f.plates_m2_ply.toFixed(2)}</td>
        <td class="py-3 px-4 font-semibold text-slate-900 font-mono">${f.total_vol_m3.toFixed(4)}</td>
      </tr>
    `).join('');
  }

  // Roofing List
  const rList = document.getElementById('roofing-metrics-list');
  if (rList) {
    rList.innerHTML = (d.roofing || []).map(r => `
      <div class="flex justify-between items-center text-sm py-1.5 border-b border-slate-100">
        <span class="text-slate-600">${r.name}:</span>
        <span class="font-bold text-slate-800">${r.length_m.toFixed(2)} м</span>
      </div>
    `).join('');
  }

  // Fasteners List
  const fastList = document.getElementById('fasteners-list');
  if (fastList) {
    fastList.innerHTML = (d.fasteners || []).map(f => `
      <div class="flex justify-between items-center text-sm py-1.5 border-b border-slate-100">
        <span class="text-slate-600">${f.desc}:</span>
        <span class="font-bold text-blue-600">${f.qty} шт</span>
      </div>
    `).join('');
  }
}
