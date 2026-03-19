# -*- coding: utf-8 -*-

from odoo import api, fields, models


class custom_dea(models.Model):
    _name = 'custom_dea'
    _inherit = 'sales'

    dealer_name = fields.Char('Name Dealer', default=False)
    discount = fields.Boolean('Discount', default=False)


