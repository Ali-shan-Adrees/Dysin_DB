from odoo import models

class PurchaseOrderXlsx(models.AbstractModel):
    _name = 'report.sl_purchase_excel.purchase_order_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, wizard):
        sheet = workbook.add_worksheet('PO Line Report')

        header_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center'
        })
        text_format = workbook.add_format({'border': 1})

        headers = [
            'Date', 'Order Ref', 'Buyer',
            'Product Name', 'Quantity', 'Unit Price',
            'Taxes', 'Total', 'Description'
        ]

        for col, title in enumerate(headers):
            sheet.write(0, col, title, header_format)
            sheet.set_column(col, col, 20)

        domain = []
        if wizard.date_from:
            domain.append(('date_order', '>=', wizard.date_from))
        if wizard.date_to:
            domain.append(('date_order', '<=', wizard.date_to))
        if hasattr(wizard, 'vendor_id') and wizard.vendor_id:
            domain.append(('partner_id', '=', wizard.vendor_id.id))
        if hasattr(wizard, 'buyer_id') and wizard.buyer_id:
            domain.append(('user_id', '=', wizard.buyer_id.id))

        purchase_orders = self.env['purchase.order'].search(domain, order='date_order')

        row = 1
        for po in purchase_orders:
            for line in po.order_line:
                taxes = ', '.join([t.name for t in line.taxes_id]) if line.taxes_id else ''
                sheet.write(row, 0, po.date_order.strftime('%Y-%m-%d') if po.date_order else '', text_format)
                sheet.write(row, 1, po.name, text_format)
                sheet.write(row, 2, po.user_id.name or '', text_format)
                sheet.write(row, 3, line.product_id.name, text_format)
                sheet.write(row, 4, line.product_qty, text_format)
                sheet.write(row, 5, line.price_unit, text_format)
                sheet.write(row, 6, taxes, text_format)
                sheet.write(row, 7, line.price_total, text_format)
                sheet.write(row, 8, line.name or '', text_format)
                row += 1