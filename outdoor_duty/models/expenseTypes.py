from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date
from datetime import datetime

class expenseType(models.Model):
    _name = 'expense.types'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Expense Type'
    name = fields.Char(string='Expense Type', required=True)
