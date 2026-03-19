# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_category = fields.Selection([
        ('commercial', 'Commercial'),
        ('corporate', 'Corporate'),
        ('csd', 'CSD'),
        ('other', 'Other'),
    ], string="Purchase Category",store=True, tracking = True, required=True)

    @api.onchange('purchase_category')
    def _onchange_purchase_category(self):
        if self.purchase_category:
            seq_code = f'purchase.order.{self.purchase_category}'
            self.name = self.env['ir.sequence'].next_by_code(seq_code) or _('New')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New') and vals.get('purchase_category'):
            seq_code = f'purchase.order.{vals.get("purchase_category")}'
            vals['name'] = self.env['ir.sequence'].next_by_code(seq_code) or _('New')
        return super(PurchaseOrder, self).create(vals)

    def write(self, vals):
        if 'purchase_category' in vals:
            for record in self:
                seq_code = f'purchase.order.{vals.get("purchase_category")}'
                record.name = self.env['ir.sequence'].next_by_code(seq_code) or record.name
        return super(PurchaseOrder, self).write(vals)

