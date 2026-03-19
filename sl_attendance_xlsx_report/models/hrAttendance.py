from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date
from datetime import datetime
class hrAttendance(models.Model):
    _inherit = 'hr.attendance'