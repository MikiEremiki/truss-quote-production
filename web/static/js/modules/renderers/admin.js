// Admin & Settings Tab Renderer

import { fetchAdminTypeAliases, saveAdminTypeAliases } from '../api.js';
import { updateAliasesCache, renderSummary } from './summary.js';

let adminData = null;

function esc(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

export async function renderAdmin() {
  const body = document.getElementById('admin-alias-body');
  if (!body) return;

  try {
    adminData = await fetchAdminTypeAliases();
    const { types, all_options, aliases } = adminData;

    // Обновляем кэш в модуле summary
    updateAliasesCache(aliases || {}, all_options || {});

    const typeEntries = Object.entries(types || {});
    if (typeEntries.length === 0) {
      body.innerHTML = `
        <tr>
          <td colspan="2" class="py-6 px-4 text-center text-slate-400 text-xs">
            Нет доступных типов конструкций (загрузите файл проекта MiTek или загрузите тестовый проект).
          </td>
        </tr>
      `;
      return;
    }

    const optionsHtml = (selectedVal, defaultLabel) => {
      let out = `<option value="">По умолчанию (${esc(defaultLabel)})</option>`;
      for (const [optKey, optLabel] of Object.entries(all_options || {})) {
        const isSel = selectedVal === optKey || selectedVal === optLabel;
        out += `<option value="${esc(optKey)}" ${isSel ? 'selected' : ''}>${esc(optLabel)}</option>`;
      }
      return out;
    };

    body.innerHTML = typeEntries.map(([key, label]) => `
      <tr class="hover:bg-slate-50/50 transition">
        <td class="py-3 px-4 font-medium text-slate-800">
          ${esc(label)} <span class="font-mono text-xs text-slate-400">(${esc(key)})</span>
        </td>
        <td class="py-3 px-4">
          <select data-key="${esc(key)}" class="admin-alias-select w-full max-w-md border border-slate-300 rounded-lg px-3 py-1.5 bg-white text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-400">
            ${optionsHtml((aliases || {})[key] || '', label)}
          </select>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Failed to render admin aliases:', err);
    body.innerHTML = `
      <tr>
        <td colspan="2" class="py-4 px-4 text-center text-red-500 text-xs">
          Ошибка загрузки настроек: ${esc(err.message)}
        </td>
      </tr>
    `;
  }
}

export async function handleSaveAdminAliases() {
  const body = document.getElementById('admin-alias-body');
  const status = document.getElementById('admin-status');
  if (!body) return;

  const aliases = {};
  body.querySelectorAll('select[data-key]').forEach(s => {
    aliases[s.dataset.key] = s.value ? s.value : '';
  });

  if (status) {
    status.className = 'text-xs text-slate-500 font-medium';
    status.textContent = 'Сохранение...';
  }

  try {
    const res = await saveAdminTypeAliases(aliases);
    if (res.status === 'success') {
      if (status) {
        status.className = 'text-xs text-emerald-600 font-medium';
        status.textContent = 'Настройки успешно сохранены!';
        setTimeout(() => {
          if (status.textContent === 'Настройки успешно сохранены!') {
            status.textContent = '';
          }
        }, 3000);
      }
      // Обновляем локальный кэш и сводную ведомость на вкладке «Обзор»
      if (adminData && adminData.all_options) {
        updateAliasesCache(res.aliases || aliases, adminData.all_options);
      }
      renderSummary();
    } else {
      throw new Error(res.detail || 'Неизвестная ошибка');
    }
  } catch (err) {
    if (status) {
      status.className = 'text-xs text-red-600 font-medium';
      status.textContent = `Ошибка сохранения: ${err.message}`;
    }
  }
}
