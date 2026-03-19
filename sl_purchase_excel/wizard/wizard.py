from odoo import models, fields

class PurchaseOrderExcelWizard(models.TransientModel):
    _name = 'purchase.order.excel.wizard'
    _description = 'Purchase Order Excel Wizard'

    date_from = fields.Date(string="Start Date")
    date_to = fields.Date(
        string="End Date",
        default=fields.Date.today
    )
    vendor = fields.Many2one(
        'res.partner',
        string="Vendor",
    )


    buyer = fields.Many2one(
        'res.users',
        string="Buyer"
    )


    def action_export_xlsx(self):
        return self.env.ref(
            'sl_purchase_excel.purchase_order_xlsx_report'
        ).report_action(self)
