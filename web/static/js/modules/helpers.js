// UI Helper Utilities

export function showLoading(show) {
  const el = document.getElementById('loading');
  if (el) el.classList.toggle('hidden', !show);
}

export function fmtRub(val) {
  return (val || 0).toLocaleString('ru-RU', { maximumFractionDigits: 0 }) + ' ₽';
}
