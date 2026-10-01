"""
Quote Export Module - Generates Printable HTML and PDF-ready documents for Commercial Proposals.
"""

from typing import Dict, Any


def render_quote_html(quote_data: Dict[str, Any]) -> str:
    """
    Генерация чистого HTML-документа коммерческого предложения для печати или конвертации в PDF.
    """
    fin = quote_data.get("financials", {})
    items = quote_data.get("items", [])
    
    rows_html = ""
    for it in items:
        rows_html += f"""
        <tr>
            <td style="border: 1px solid #cbd5e1; padding: 8px; text-align: center;">{it['item_no']}</td>
            <td style="border: 1px solid #cbd5e1; padding: 8px;">
                <strong>{it['name']}</strong><br/>
                <small style="color: #64748b;">{it['description']}</small>
            </td>
            <td style="border: 1px solid #cbd5e1; padding: 8px; text-align: center;">{it['qty']} {it['unit']}</td>
            <td style="border: 1px solid #cbd5e1; padding: 8px; text-align: right;">{it['unit_price']:,.2f} ₽</td>
            <td style="border: 1px solid #cbd5e1; padding: 8px; text-align: right; font-weight: bold;">{it['total_price']:,.2f} ₽</td>
        </tr>
        """
        
    discount_html = ""
    if fin.get("discount_amount", 0) > 0:
        discount_html = f"""
        <tr style="background-color: #fef3c7;">
            <td colspan="4" style="border: 1px solid #cbd5e1; padding: 8px; text-align: right; font-weight: bold; color: #b45309;">Специальная скидка на заказ:</td>
            <td style="border: 1px solid #cbd5e1; padding: 8px; text-align: right; font-weight: bold; color: #b45309;">-{fin['discount_amount']:,.2f} ₽</td>
        </tr>
        """

    vat_html = ""
    if fin.get("vat_amount", 0) > 0:
        vat_html = f"""
        <tr>
            <td colspan="4" style="border: 1px solid #cbd5e1; padding: 8px; text-align: right; font-weight: bold;">НДС ({fin.get('vat_pct', 0)}%):</td>
            <td style="border: 1px solid #cbd5e1; padding: 8px; text-align: right; font-weight: bold;">+{fin['vat_amount']:,.2f} ₽</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Коммерческое предложение {quote_data.get('quote_id', '')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 40px; color: #1e293b; }}
        h1 {{ margin-bottom: 4px; color: #0f172a; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background-color: #f1f5f9; border: 1px solid #cbd5e1; padding: 10px; text-align: left; font-size: 13px; text-transform: uppercase; }}
        .header-box {{ display: flex; justify-content: space-between; border-bottom: 2px solid #2563eb; padding-bottom: 15px; }}
        .total-box {{ margin-top: 30px; text-align: right; font-size: 18px; }}
        .total-amount {{ font-size: 24px; font-weight: bold; color: #2563eb; }}
    </style>
</head>
<body>
    <div class="header-box">
        <div>
            <h1>КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ</h1>
            <p style="margin: 0; color: #64748b;">Номер: <strong>{quote_data.get('quote_id')}</strong> от {quote_data.get('date')}</p>
        </div>
        <div style="text-align: right;">
            <h3 style="margin: 0; color: #2563eb;">ООО «ДревКаркас»</h3>
            <p style="margin: 2px 0 0 0; font-size: 13px; color: #64748b;">Производство деревянных ферм на МЗП</p>
        </div>
    </div>

    <div style="margin-top: 20px;">
        <p><strong>Объект / Проект:</strong> {quote_data.get('project_name')}</p>
        <p><strong>Заказчик:</strong> {quote_data.get('client_name')}</p>
    </div>

    <table>
        <thead>
            <tr>
                <th style="width: 40px; text-align: center;">№</th>
                <th>Наименование продукции и услуг</th>
                <th style="width: 100px; text-align: center;">Кол-во</th>
                <th style="width: 120px; text-align: right;">Цена, руб.</th>
                <th style="width: 140px; text-align: right;">Сумма, руб.</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
            {discount_html}
            {vat_html}
        </tbody>
    </table>

    <div class="total-box">
        <p>ИТОГО К ОПЛАТЕ: <span class="total-amount">{fin.get('final_price_with_vat', 0):,.2f} ₽</span></p>
    </div>
</body>
</html>"""
    return html
