"""
Export utilities for Commercial Proposals (Quote) in HTML and CSV formats.
"""

import csv
import io
from typing import Dict, Any
from costing.quote.pdf_export import render_quote_html


def export_quote_csv(quote_data: Dict[str, Any]) -> str:
    """
    Экспорт коммерческого предложения в формат CSV (с разделителем ; для Excel).
    """
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', lineterminator='\n')

    # Заголовок
    writer.writerow(["КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", quote_data.get("quote_id", ""), f"от {quote_data.get('date', '')}"])
    writer.writerow(["Проект / Объект", quote_data.get("project_name", "")])
    writer.writerow(["Заказчик", quote_data.get("client_name", "")])
    writer.writerow([])

    # Таблица позиций
    writer.writerow(["№", "Наименование", "Описание", "Количество", "Ед. изм.", "Цена за ед., руб.", "Сумма, руб."])
    for item in quote_data.get("items", []):
        writer.writerow([
            item.get("item_no", ""),
            item.get("name", ""),
            item.get("description", ""),
            item.get("qty", 0),
            item.get("unit", ""),
            f"{item.get('unit_price', 0):.2f}",
            f"{item.get('total_price', 0):.2f}"
        ])

    fin = quote_data.get("financials", {})
    if fin.get("discount_amount", 0) > 0:
        writer.writerow(["", "Специальная скидка", "", "", "", "", f"-{fin.get('discount_amount', 0):.2f}"])

    if fin.get("vat_amount", 0) > 0:
        writer.writerow(["", f"НДС ({fin.get('vat_pct', 0)}%)", "", "", "", "", f"+{fin.get('vat_amount', 0):.2f}"])

    writer.writerow([])
    writer.writerow(["", "ИТОГО К ОПЛАТЕ", "", "", "", "", f"{fin.get('final_price_with_vat', 0):.2f}"])

    return output.getvalue()
