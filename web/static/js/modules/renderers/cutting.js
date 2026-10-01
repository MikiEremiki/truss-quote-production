// Cutting Layout Renderer

import { appState } from '../state.js';

export function renderCutting() {
  if (!appState.cutting) return;
  const cut = appState.cutting;
  const sum = cut.summary;

  const setEl = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.innerText = val;
  };

  setEl('cut-summary-bars', `${sum.total_bars_count} шт`);
  setEl('cut-summary-stock-m', `${sum.total_stock_meters.toFixed(2)} м`);
  setEl('cut-summary-net-m', `${sum.total_net_meters.toFixed(2)} м`);
  setEl('cut-summary-waste-pct', `${sum.overall_waste_pct.toFixed(1)} %`);

  const container = document.getElementById('cutting-patterns-container');
  if (!container) return;

  const colors = ['bg-blue-500', 'bg-indigo-500', 'bg-teal-500', 'bg-emerald-500', 'bg-amber-500', 'bg-rose-500', 'bg-violet-500'];

  container.innerHTML = Object.entries(cut.by_section || {}).map(([sec, secData]) => `
    <div class="border border-slate-200 rounded-xl p-5 bg-slate-50/50 space-y-4">
      <div class="flex flex-wrap justify-between items-center gap-2 border-b pb-2">
        <div>
          <h4 class="font-bold text-slate-800 text-base flex items-center gap-2">
            <span class="px-2.5 py-1 bg-blue-100 text-blue-900 rounded-md font-mono text-sm">${sec} мм</span>
            <span>Раскладка заготовок (${secData.total_parts_count} шт.)</span>
          </h4>
        </div>
        <div class="text-xs text-slate-600 flex gap-4">
          <span>Хлыстов (${Math.round(secData.stock_length_mm)} мм): <b>${secData.total_bars} шт</b> (${secData.total_stock_length_m.toFixed(2)} м)</span>
          <span>Деловой отход: <b class="text-emerald-700">${secData.waste_pct.toFixed(1)}%</b> (${secData.waste_length_m.toFixed(2)} м)</span>
        </div>
      </div>

      <div class="space-y-3">
        ${secData.bars.map((bar, bIdx) => {
          const stockLen = secData.stock_length_m;
          return `
            <div class="bg-white p-3 rounded-lg border border-slate-200 text-xs shadow-2xs space-y-2">
              <div class="flex justify-between items-center font-semibold text-slate-700">
                <span>Хлыст #${bIdx + 1} (${sec})</span>
                <span class="text-slate-500 font-normal">Занято: <b>${bar.used_m.toFixed(3)} м</b> / Остаток: <b class="text-amber-600">${bar.remaining_m.toFixed(3)} м</b> (отход ${bar.waste_pct.toFixed(1)}%)</span>
              </div>

              <!-- Graphic Bar Visualizer -->
              <div class="w-full h-7 bg-slate-100 rounded-md overflow-hidden flex border border-slate-200">
                ${bar.parts.map((p, pIdx) => {
                  const pct = Math.min(100, (p.length_m / stockLen) * 100);
                  const col = colors[(pIdx + bIdx) % colors.length];
                  return `
                    <div style="width: ${pct}%;" class="${col} text-white font-mono flex items-center justify-center text-[10px] font-bold border-r border-white/40 overflow-hidden px-1" title="${p.truss} ${p.label}: ${Math.round(p.length_m * 1000)} мм">
                      ${p.label} (${Math.round(p.length_m * 1000)})
                    </div>
                  `;
                }).join('')}
                ${bar.remaining_m > 0 ? `
                  <div style="width: ${(bar.remaining_m / stockLen) * 100}%;" class="bg-slate-200 text-slate-500 flex items-center justify-center text-[9px] font-mono">
                    Ост: ${Math.round(bar.remaining_m * 1000)}
                  </div>
                ` : ''}
              </div>
            </div>
          `;
        }).join('')}
      </div>
    </div>
  `).join('');
}
