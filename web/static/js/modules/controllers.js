// UI Controllers & Business Logic Event Handlers

import { appState, setAppState } from './state.js';
import { showLoading } from './helpers.js';
import {
  fetchAppInfo,
  fetchSampleData,
  uploadMitekFile,
  apiCalculateCosting,
  apiCalculatePositions,
  apiOptimizeCutting,
  apiCalculateFinancials,
  apiCalculateAll,
  apiGenerateWorkorders
} from './api.js';
import { renderAll, renderCutting, renderPositions, renderCosting, renderFinancials, renderClientKP, renderInternalEstimate, renderWorkorders } from './renderers/index.js';

export function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

  const targetTab = document.getElementById(tabId);
  const targetBtn = document.getElementById(`btn-${tabId}`);
  if (targetTab) targetTab.classList.remove('hidden');
  if (targetBtn) targetBtn.classList.add('active');

  // Dispatch resize event to trigger Three.js canvas & chart resizing
  window.dispatchEvent(new Event('resize'));

  // Close mobile sidebar if open
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (sidebar && window.innerWidth < 1024) {
    sidebar.classList.add('-translate-x-full');
    if (backdrop) backdrop.classList.add('hidden');
  }
}

export function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (!sidebar) return;
  const isHidden = sidebar.classList.contains('-translate-x-full');
  if (isHidden) {
    sidebar.classList.remove('-translate-x-full');
    if (backdrop) backdrop.classList.remove('hidden');
  } else {
    sidebar.classList.add('-translate-x-full');
    if (backdrop) backdrop.classList.add('hidden');
  }
}

export function initControlsAndPresets() {
  if (!appState.cost || !appState.cost.catalogs) return;

  const cats = appState.cost.catalogs;

  // 1. Populate Client Profiles Selector
  const profSel = document.getElementById('sel-client-profile');
  if (profSel) {
    profSel.innerHTML = Object.entries(cats.client_profiles).map(([k, v]) => `
      <option value="${k}">${v.name} (+${v.margin_pct}%)</option>
    `).join('');
  }

  // 2. Populate Agent Preset Selector
  const agentSel = document.getElementById('sel-agent-preset');
  if (agentSel) {
    agentSel.innerHTML = Object.entries(cats.agents_catalog).map(([k, v]) => `
      <option value="${k}">${v.name} (${v.pct}%)</option>
    `).join('');
  }

  // 3. Initialize custom_items if empty
  if (appState.data && appState.data.frames) {
    appState.data.frames.forEach(f => {
      if (!appState.custom_items[f.name]) {
        appState.custom_items[f.name] = {
          type: f.item_type || 'truss',
          subtype: f.item_type === 'truss' ? 'duopitch' : (f.item_type === 'cut_timber' ? 'cut_timber' : 'raw_timber'),
          has_treatment: true,
          has_cutting: f.item_type !== 'raw_timber',
          work_rate_m3: f.work_rate_m3 || 4400,
          margin_pct: f.margin_pct || 58
        };
      }
    });
  }
}

export function applyClientProfile() {
  const profKey = document.getElementById('sel-client-profile')?.value;
  const cats = appState.cost ? appState.cost.catalogs : null;
  if (!cats || !profKey || !cats.client_profiles[profKey]) return;

  const prof = cats.client_profiles[profKey];
  const descEl = document.getElementById('client-profile-desc');
  if (descEl) descEl.innerText = prof.description;

  const treatInp = document.getElementById('inp-treatment-price');
  if (treatInp) treatInp.value = prof.treatment_price_m2;

  const timberInp = document.getElementById('inp-timber-price');
  if (timberInp) timberInp.value = prof.timber_price_m3;

  // Update margin by default in custom items
  if (appState.data && appState.data.frames) {
    appState.data.frames.forEach(f => {
      if (appState.custom_items[f.name]) {
        appState.custom_items[f.name].margin_pct = prof.margin_pct;
      }
    });
  }

  recalculateCosting();
}

export function applyAgentPreset() {
  const agentKey = document.getElementById('sel-agent-preset')?.value;
  const cats = appState.cost ? appState.cost.catalogs : null;
  if (!cats || !agentKey || !cats.agents_catalog[agentKey]) return;

  const agent = cats.agents_catalog[agentKey];
  const agentInp = document.getElementById('inp-agent-pct');
  if (agentInp) agentInp.value = agent.pct;

  recalculateFinancials();
}

export function onPositionSubtypeChange(posName) {
  const selEl = document.getElementById(`pos-subtype-${posName}`);
  const workEl = document.getElementById(`pos-work-${posName}`);
  const typeEl = document.getElementById(`pos-type-${posName}`);
  const cats = appState.cost ? appState.cost.catalogs : null;

  if (selEl && workEl && cats && cats.truss_types[selEl.value]) {
    const info = cats.truss_types[selEl.value];
    workEl.value = info.price_m3;
    if (selEl.value === 'cut_timber') {
      typeEl.value = 'cut_timber';
    } else if (selEl.value === 'raw_timber') {
      typeEl.value = 'raw_timber';
    } else {
      typeEl.value = 'truss';
    }
  }
  recalculatePositions();
}

export function collectCustomItems() {
  if (appState.data && appState.data.frames) {
    appState.data.frames.forEach(f => {
      const typeEl = document.getElementById(`pos-type-${f.name}`);
      const subtypeEl = document.getElementById(`pos-subtype-${f.name}`);
      const treatEl = document.getElementById(`pos-treat-${f.name}`);
      const cutEl = document.getElementById(`pos-cut-${f.name}`);
      const workEl = document.getElementById(`pos-work-${f.name}`);
      const marginEl = document.getElementById(`pos-margin-${f.name}`);

      if (typeEl && subtypeEl && treatEl && cutEl && workEl && marginEl) {
        appState.custom_items[f.name] = {
          type: typeEl.value,
          subtype: subtypeEl.value,
          has_treatment: treatEl.checked,
          has_cutting: cutEl.checked,
          work_rate_m3: parseFloat(workEl.value) || 0,
          margin_pct: parseFloat(marginEl.value) || 0
        };
      }
    });
  }
  return appState.custom_items;
}

export function collectPayload() {
  collectCustomItems();

  const getVal = (id, def) => {
    const el = document.getElementById(id);
    if (!el) return def;
    const v = parseFloat(el.value);
    return isNaN(v) ? def : v;
  };

  const getStr = (id, def) => {
    const el = document.getElementById(id);
    return el ? el.value : def;
  };

  return {
    client_profile: getStr('sel-client-profile', 'standard'),
    timber_price_m3: getVal('inp-timber-price', 31900),
    timber_waste_factor: getVal('inp-waste-factor', 1.15),
    plate_price_m2: getVal('inp-plate-price', 4500),
    cutting_price_m3: getVal('inp-cutting-price', 2000),
    treatment_price_m2: getVal('inp-treatment-price', 65),

    design_mode: getStr('sel-design-mode', 'separate'),
    design_price_fixed: getVal('inp-design-price', 15000),
    fasteners_price_fixed: getVal('inp-fasteners-price', 5625),
    logistics_price_fixed: getVal('inp-logistics-price', 12000),
    overhead_pct: getVal('inp-overhead-pct', 10),

    discount_type: getStr('sel-discount-type', 'percent'),
    discount_val: getVal('inp-discount-val', 0),

    agent_id: getStr('sel-agent-preset', 'none'),
    agent_pct: getVal('inp-agent-pct', 0),
    agent_mode: getStr('sel-agent-mode', 'markup'),

    vat_pct: getVal('inp-vat-pct', 0),
    stock_length_mm: getVal('inp-stock-len-mm', 6000),

    custom_items: appState.custom_items
  };
}

// Dedicated endpoint actions for different tabs & operations

export async function recalculateCosting() {
  const payload = collectPayload();
  showLoading(true);
  try {
    const json = await apiCalculateCosting(payload);
    if (json.status === 'success') {
      appState.cost = json.cost;
      renderAll();
    }
  } catch (e) {
    alert('Ошибка пересчета стоимости: ' + e);
  } finally {
    showLoading(false);
  }
}

export async function recalculatePositions() {
  const payload = collectPayload();
  showLoading(true);
  try {
    const json = await apiCalculatePositions(payload);
    if (json.status === 'success') {
      appState.cost = json.cost;
      renderAll();
    }
  } catch (e) {
    alert('Ошибк�� пересчета позиций: ' + e);
  } finally {
    showLoading(false);
  }
}

export async function recalculateCutting() {
  const stockLen = parseFloat(document.getElementById('inp-stock-len-mm')?.value) || 6000;
  showLoading(true);
  try {
    const json = await apiOptimizeCutting({ stock_length_mm: stockLen });
    if (json.status === 'success') {
      appState.cutting = json.cutting;
      renderCutting();
    }
  } catch (e) {
    alert('Ошибка расчета раскроя: ' + e);
  } finally {
    showLoading(false);
  }
}

export async function recalculateFinancials() {
  const payload = collectPayload();
  showLoading(true);
  try {
    const json = await apiCalculateFinancials(payload);
    if (json.status === 'success') {
      appState.cost = json.cost;
      renderFinancials();
      renderCosting();
      renderClientKP();
      renderInternalEstimate();
    }
  } catch (e) {
    alert('Ошибка пересчета финансовых показателей: ' + e);
  } finally {
    showLoading(false);
  }
}

export async function recalculateWorkorders() {
  const stockLen = parseFloat(document.getElementById('inp-stock-len-mm')?.value) || 6000;
  showLoading(true);
  try {
    const json = await apiGenerateWorkorders({ stock_length_mm: stockLen });
    if (json.status === 'success') {
      appState.workorders = json.workorders;
      renderWorkorders();
    }
  } catch (e) {
    alert('Ошибка генерации нарядов цеха: ' + e);
  } finally {
    showLoading(false);
  }
}

export async function recalculateAll() {
  const payload = collectPayload();
  showLoading(true);
  try {
    const json = await apiCalculateAll(payload);
    if (json.status === 'success') {
      appState.cost = json.cost;
      appState.cutting = json.cutting;
      try {
        const woJson = await apiGenerateWorkorders({ stock_length_mm: payload.stock_length_mm });
        if (woJson.status === 'success') {
          appState.workorders = woJson.workorders;
        }
      } catch (err) {
        console.warn('Workorders generation error:', err);
      }
      renderAll();
    }
  } catch (e) {
    alert('Ошибка пересчета: ' + e);
  } finally {
    showLoading(false);
  }
}

export async function loadSampleData() {
  showLoading(true);
  try {
    const json = await fetchSampleData();
    if (json.status === 'success') {
      appState.data = json.data;
      appState.cost = json.cost;
      appState.cutting = json.cutting;
      try {
        const woJson = await apiGenerateWorkorders();
        if (woJson.status === 'success') {
          appState.workorders = woJson.workorders;
        }
      } catch (err) {
        console.warn('Workorders fetch error:', err);
      }
      initControlsAndPresets();
      renderAll();
    }
  } catch (e) {
    alert('Ошибка загрузки данных: ' + e);
  } finally {
    showLoading(false);
  }
}

export async function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  showLoading(true);
  try {
    const json = await uploadMitekFile(file);
    if (json.status === 'success') {
      appState.data = json.data;
      appState.cost = json.cost;
      appState.cutting = json.cutting;
      try {
        const woJson = await apiGenerateWorkorders();
        if (woJson.status === 'success') {
          appState.workorders = woJson.workorders;
        }
      } catch (err) {
        console.warn('Workorders fetch error:', err);
      }
      initControlsAndPresets();
      renderAll();
      alert(`Файл "${json.filename}" успешно загружен и обработан!`);
    } else {
      alert('Ошибка: ' + json.detail);
    }
  } catch (e) {
    alert('Ошибка загрузки файла: ' + e);
  } finally {
    showLoading(false);
  }
}

export async function loadAppInfo() {
  try {
    const json = await fetchAppInfo();
    const verElem = document.getElementById('app-version');
    if (verElem && json.version_full) {
      verElem.textContent = json.version_full;
    }
  } catch (e) {
    console.warn('Не удалось загрузить информацию о версии:', e);
  }
}
