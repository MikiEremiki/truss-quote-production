// Quotation & Internal Estimate Renderers

import { appState } from '../state.js';
import { fmtRub } from '../helpers.js';

export function renderClientKP() {
  if (!appState.cost || !appState.data) return;
  const d = appState.data;
  const sum = d.summary || {};
  const fin = appState.cost.financial_summary || {};
  const ext = appState.cost.extras_financials || {};

  const kpObjName = document.getElementById('kp-obj-name');
  if (kpObjName) kpObjName.innerText = sum.project_name || 'Богородск 21 дом 110м2';

  const kpRoofArea = document.getElementById('kp-roof-area');
  if (kpRoofArea) kpRoofArea.innerText = `${(sum.total_roof_area_m2 || 0).toFixed(2)} м²`;

  const kpDate = document.getElementById('kp-date');
  if (kpDate) {
    const today = new Date();
    const dd = String(today.getDate()).padStart(2, '0');
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const yyyy = today.getFullYear();
    kpDate.innerText = `${dd}.${mm}.${yyyy}`;
  }

  const tbody = document.getElementById('kp-table-body');
  if (!tbody) return;

  let rows = [];
  let idx = 1;

  // Позиции конструкций
  (appState.cost.positions || []).forEach(p => {
    const qty = p.qty_packets || 1;
    const plies = p.plies || 1;
    const pliesStr = plies > 1 ? ` (${plies} сл.)` : '';
    const spanStr = p.span_mm ? ` / пролет ${(p.span_mm / 1000).toFixed(2)}м` : '';
    const desc = `${p.subtype_label || p.truss_subtype || ''}${spanStr}${pliesStr}`;
    const unit = plies > 1 ? 'компл.' : 'шт.';
    const totalPrice = p.final_position_sale !== undefined ? p.final_position_sale : (p.sale_price_base || 0);
    const unitPrice = qty > 0 ? totalPrice / qty : totalPrice;

    rows.push(`
      <tr>
        <td class="py-2.5 px-3 text-center border-b text-slate-500">${idx++}</td>
        <td class="py-2.5 px-3 border-b">
          <span class="font-bold text-slate-800">Деревянная конструкция марка ${p.name}</span>
          <span class="block text-[11px] text-slate-500 font-normal">${desc}</span>
        </td>
        <td class="py-2.5 px-3 text-center border-b font-medium text-slate-700">${qty} ${unit}</td>
        <td class="py-2.5 px-3 text-right border-b font-mono text-slate-700">${fmtRub(unitPrice)}</td>
        <td class="py-2.5 px-3 text-right border-b font-mono font-bold text-slate-900">${fmtRub(totalPrice)}</td>
      </tr>
    `);
  });

  // Защитная обработка
  if (ext.treatment_sale > 0) {
    const surfM2 = (appState.cost.treated_timber_surface_m2 || 0).toFixed(2);
    rows.push(`
      <tr>
        <td class="py-2.5 px-3 text-center border-b text-slate-500">${idx++}</td>
        <td class="py-2.5 px-3 border-b">
          <span class="font-bold text-slate-800">Защитная огнебиозащитная обработка (СенежОгнеБио)</span>
          <span class="block text-[11px] text-slate-500 font-normal">Антисептирование 4-х сторон заготовок методом распыления/погружения (${surfM2} м²)</span>
        </td>
        <td class="py-2.5 px-3 text-center border-b font-medium text-slate-700">1 компл.</td>
        <td class="py-2.5 px-3 text-right border-b font-mono text-slate-700">${fmtRub(ext.treatment_sale)}</td>
        <td class="py-2.5 px-3 text-right border-b font-mono font-bold text-slate-900">${fmtRub(ext.treatment_sale)}</td>
      </tr>
    `);
  }

  // Проектирование (только если отдельной строкой)
  if (ext.design_mode === 'separate' && ext.design_sale > 0) {
    rows.push(`
      <tr>
        <td class="py-2.5 px-3 text-center border-b text-slate-500">${idx++}</td>
        <td class="py-2.5 px-3 border-b">
          <span class="font-bold text-slate-800">Разработка конструкторской документации (раздел КР / КДД)</span>
          <span class="block text-[11px] text-slate-500 font-normal">Рабочие чертежи стропильной системы, сборочные схемы и монтажный план узлов</span>
        </td>
        <td class="py-2.5 px-3 text-center border-b font-medium text-slate-700">1 компл.</td>
        <td class="py-2.5 px-3 text-right border-b font-mono text-slate-700">${fmtRub(ext.design_sale)}</td>
        <td class="py-2.5 px-3 text-right border-b font-mono font-bold text-slate-900">${fmtRub(ext.design_sale)}</td>
      </tr>
    `);
  }

  // Крепеж
  if (ext.fasteners_sale > 0) {
    rows.push(`
      <tr>
        <td class="py-2.5 px-3 text-center border-b text-slate-500">${idx++}</td>
        <td class="py-2.5 px-3 border-b">
          <span class="font-bold text-slate-800">Комплект монтажного крепежа и метизов</span>
          <span class="block text-[11px] text-slate-500 font-normal">Анкерные пластины, усиленные уголки, конструкционные саморезы, шпильки</span>
        </td>
        <td class="py-2.5 px-3 text-center border-b font-medium text-slate-700">1 компл.</td>
        <td class="py-2.5 px-3 text-right border-b font-mono text-slate-700">${fmtRub(ext.fasteners_sale)}</td>
        <td class="py-2.5 px-3 text-right border-b font-mono font-bold text-slate-900">${fmtRub(ext.fasteners_sale)}</td>
      </tr>
    `);
  }

  // Доставка
  if (ext.logistics_sale > 0) {
    rows.push(`
      <tr>
        <td class="py-2.5 px-3 text-center border-b text-slate-500">${idx++}</td>
        <td class="py-2.5 px-3 border-b">
          <span class="font-bold text-slate-800">Транспортировка и доставка на объект</span>
          <span class="block text-[11px] text-slate-500 font-normal">Специализированный автотранспорт (шаланда/еврофура)</span>
        </td>
        <td class="py-2.5 px-3 text-center border-b font-medium text-slate-700">1 рейс</td>
        <td class="py-2.5 px-3 text-right border-b font-mono text-slate-700">${fmtRub(ext.logistics_sale)}</td>
        <td class="py-2.5 px-3 text-right border-b font-mono font-bold text-slate-900">${fmtRub(ext.logistics_sale)}</td>
      </tr>
    `);
  }

  // Скидка (если есть)
  if (fin.discount_amount > 0) {
    rows.push(`
      <tr class="bg-amber-50/70">
        <td class="py-2.5 px-3 text-center border-b text-amber-700 font-bold">%</td>
        <td class="py-2.5 px-3 border-b font-bold text-amber-800" colspan="3">Специальная скидка на заказ:</td>
        <td class="py-2.5 px-3 border-b text-right font-mono font-bold text-amber-700">-${fmtRub(fin.discount_amount)}</td>
      </tr>
    `);
  }

  // НДС (если есть)
  if (fin.vat_amount > 0) {
    rows.push(`
      <tr class="bg-slate-50">
        <td class="py-2.5 px-3 text-center border-b text-slate-500 font-bold">+</td>
        <td class="py-2.5 px-3 border-b font-bold text-slate-700" colspan="3">НДС (${appState.cost.parameters?.vat_pct || fin.vat_pct || 0}%):</td>
        <td class="py-2.5 px-3 border-b text-right font-mono font-bold text-slate-800">+${fmtRub(fin.vat_amount)}</td>
      </tr>
    `);
  }

  tbody.innerHTML = rows.join('');
  const totalSum = document.getElementById('kp-total-sum');
  if (totalSum) totalSum.innerText = fmtRub(fin.final_price_with_vat !== undefined ? fin.final_price_with_vat : fin.client_net_price);
}

export function renderInternalEstimate() {
  if (!appState.cost) return;
  const fin = appState.cost.financial_summary;
  const ext = appState.cost.extras_financials;
  const str = appState.cost.structures_financials;
  const tbody = document.getElementById('internal-estimate-body');
  if (!tbody) return;

  const rows = [
    `<tr>
      <td class="py-2.5 px-3 font-semibold text-slate-800">1. Деревянные конструкции (доска + МЗП + сборка + прирезка)</td>
      <td class="py-2.5 px-3 text-right text-slate-600">${fmtRub(str.total_cost)}</td>
      <td class="py-2.5 px-3 text-right text-slate-900">${fmtRub(str.total_sale)}</td>
      <td class="py-2.5 px-3 text-right font-bold text-emerald-700">+${fmtRub(str.profit_pure_structures)}</td>
    </tr>`,
    `<tr>
      <td class="py-2.5 px-3 font-semibold text-slate-800">2. Защитная обработка СенежОгнеБио 300 г/м²</td>
      <td class="py-2.5 px-3 text-right text-slate-600">${fmtRub(ext.treatment_cost)}</td>
      <td class="py-2.5 px-3 text-right text-slate-900">${fmtRub(ext.treatment_sale)}</td>
      <td class="py-2.5 px-3 text-right font-bold text-blue-700">+${fmtRub(ext.treatment_sale - ext.treatment_cost)}</td>
    </tr>`,
    `<tr>
      <td class="py-2.5 px-3 font-semibold text-slate-800">3. Проектирование КР/КДД (режим: ${ext.design_mode === 'separate' ? 'в КП' : 'разнесено'})</td>
      <td class="py-2.5 px-3 text-right text-slate-600">${fmtRub(ext.design_cost)}</td>
      <td class="py-2.5 px-3 text-right text-slate-900">${fmtRub(ext.design_sale)}</td>
      <td class="py-2.5 px-3 text-right font-bold text-blue-700">+${fmtRub(ext.design_sale - ext.design_cost)}</td>
    </tr>`,
    `<tr>
      <td class="py-2.5 px-3 font-semibold text-slate-800">4. Крепеж и метизы</td>
      <td class="py-2.5 px-3 text-right text-slate-600">${fmtRub(ext.fasteners_cost)}</td>
      <td class="py-2.5 px-3 text-right text-slate-900">${fmtRub(ext.fasteners_sale)}</td>
      <td class="py-2.5 px-3 text-right font-bold text-blue-700">+${fmtRub(ext.fasteners_sale - ext.fasteners_cost)}</td>
    </tr>`,
    `<tr>
      <td class="py-2.5 px-3 font-semibold text-slate-800">5. Транспортировка и доставка</td>
      <td class="py-2.5 px-3 text-right text-slate-600">${fmtRub(ext.logistics_cost)}</td>
      <td class="py-2.5 px-3 text-right text-slate-900">${fmtRub(ext.logistics_sale)}</td>
      <td class="py-2.5 px-3 text-right font-bold text-blue-700">+${fmtRub(ext.logistics_sale - ext.logistics_cost)}</td>
    </tr>`,
    `<tr class="bg-slate-50 font-semibold">
      <td class="py-2.5 px-3 text-slate-800">6. Накладные расходы цеха (10%)</td>
      <td class="py-2.5 px-3 text-right text-slate-600">${fmtRub(fin.overhead_cost)}</td>
      <td class="py-2.5 px-3 text-right text-slate-900">—</td>
      <td class="py-2.5 px-3 text-right text-slate-500">-${fmtRub(fin.overhead_cost)}</td>
    </tr>`,
    `<tr class="bg-amber-50 font-bold">
      <td class="py-2.5 px-3 text-amber-900">7. Общая скидка на заказ</td>
      <td class="py-2.5 px-3 text-right text-slate-600">—</td>
      <td class="py-2.5 px-3 text-right text-amber-800">-${fmtRub(fin.discount_amount)}</td>
      <td class="py-2.5 px-3 text-right text-amber-800">-${fmtRub(fin.discount_amount)}</td>
    </tr>`,
    `<tr class="bg-blue-50 font-bold">
      <td class="py-2.5 px-3 text-blue-900">8. Комиссия агента (${appState.cost.parameters.agent_mode || 'markup'})</td>
      <td class="py-2.5 px-3 text-right text-slate-600">—</td>
      <td class="py-2.5 px-3 text-right text-blue-800">${fmtRub(fin.agent_fee)}</td>
      <td class="py-2.5 px-3 text-right text-blue-800">${appState.cost.parameters.agent_mode === 'margin' ? '-' + fmtRub(fin.agent_fee) : '0 ₽'}</td>
    </tr>`,
    `<tr class="bg-slate-900 text-white font-bold text-sm">
      <td class="py-3 px-3">ИТОГО ЧИСТАЯ ПРИБЫЛЬ ДК:</td>
      <td class="py-3 px-3 text-right text-slate-300">${fmtRub(fin.total_cost)}</td>
      <td class="py-3 px-3 text-right text-blue-300">${fmtRub(fin.client_net_price)}</td>
      <td class="py-3 px-3 text-right text-emerald-400 text-base">+${fmtRub(fin.dk_net_profit)}</td>
    </tr>`
  ];

  tbody.innerHTML = rows.join('');
}
