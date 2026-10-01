"""
1D Bin Packing (Best Fit Decreasing) Stock Cutting Optimizer.
Оптимизирует раскрой заготовок по сечениям на хлысты заданной длины в мм с учетом ширины пропила.
"""

from typing import List, Dict, Any


def optimize_cutting_stock(
    timber_items: List[Dict[str, Any]],
    stock_length_mm: float = 6000.0,
    kerf_mm: float = 4.0
) -> Dict[str, Any]:
    """
    1D Bin Packing (Best Fit Decreasing) раскрой заготовок по сечениям на хлысты заданной длины (в мм).
    """
    stock_length_m = stock_length_mm / 1000.0
    kerf_m = kerf_mm / 1000.0

    by_section: Dict[str, List[Dict[str, Any]]] = {}
    for item in timber_items:
        sec = item.get("section", "Не указано")
        if sec not in by_section:
            by_section[sec] = []
        for _ in range(item.get("qty", 1)):
            by_section[sec].append({
                "truss": item.get("truss", ""),
                "label": item.get("label", ""),
                "length_m": item.get("length_m", 0.0),
                "length_mm": round(item.get("length_m", 0.0) * 1000.0)
            })

    results: Dict[str, Dict[str, Any]] = {}
    total_stock_bars_all = 0
    total_stock_length_all = 0.0
    total_net_length_all = 0.0

    for sec, parts in by_section.items():
        # Сортировка деталей по убыванию длины (BFD heuristic)
        sorted_parts = sorted(parts, key=lambda x: x["length_m"], reverse=True)
        
        bars: List[Dict[str, Any]] = [] # список хлыстов
        
        for part in sorted_parts:
            p_len = part["length_m"]
            if p_len > stock_length_m:
                bars.append({
                    "used_m": p_len,
                    "remaining_m": 0.0,
                    "parts": [part],
                    "oversize": True
                })
                continue

            best_bar_idx = -1
            min_remaining = 9999.0

            for idx, bar in enumerate(bars):
                if bar.get("oversize"):
                    continue
                needed = p_len + (kerf_m if bar["parts"] else 0.0)
                rem = stock_length_m - bar["used_m"]
                if rem >= needed:
                    diff = rem - needed
                    if diff < min_remaining:
                        min_remaining = diff
                        best_bar_idx = idx

            if best_bar_idx != -1:
                bar = bars[best_bar_idx]
                bar["used_m"] += p_len + (kerf_m if bar["parts"] else 0.0)
                bar["parts"].append(part)
            else:
                bars.append({
                    "used_m": p_len,
                    "parts": [part],
                    "oversize": False
                })

        for bar in bars:
            bar["used_m"] = round(bar["used_m"], 4)
            bar["remaining_m"] = round(max(0.0, stock_length_m - bar["used_m"]), 4)
            bar["waste_pct"] = round((bar["remaining_m"] / stock_length_m) * 100.0, 1) if not bar.get("oversize") else 0.0

        sec_stock_bars = len(bars)
        sec_stock_len = sec_stock_bars * stock_length_m
        sec_net_len = sum(p["length_m"] for p in parts)
        sec_waste_len = sec_stock_len - sec_net_len
        sec_waste_pct = round((sec_waste_len / sec_stock_len) * 100.0, 1) if sec_stock_len > 0 else 0.0

        total_stock_bars_all += sec_stock_bars
        total_stock_length_all += sec_stock_len
        total_net_length_all += sec_net_len

        results[sec] = {
            "total_bars": sec_stock_bars,
            "stock_length_mm": stock_length_mm,
            "stock_length_m": stock_length_m,
            "total_parts_count": len(parts),
            "net_length_m": round(sec_net_len, 2),
            "total_stock_length_m": round(sec_stock_len, 2),
            "waste_length_m": round(sec_waste_len, 2),
            "waste_pct": sec_waste_pct,
            "bars": bars
        }

    total_waste_all = total_stock_length_all - total_net_length_all
    total_waste_pct_all = round((total_waste_all / total_stock_length_all) * 100.0, 1) if total_stock_length_all > 0 else 0.0

    return {
        "summary": {
            "stock_length_mm": stock_length_mm,
            "stock_length_m": stock_length_m,
            "total_bars_count": total_stock_bars_all,
            "total_stock_meters": round(total_stock_length_all, 2),
            "total_net_meters": round(total_net_length_all, 2),
            "total_waste_meters": round(total_waste_all, 2),
            "overall_waste_pct": total_waste_pct_all
        },
        "by_section": results
    }
