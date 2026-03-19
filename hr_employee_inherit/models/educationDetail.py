from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
import datetime
from dateutil.relativedelta import relativedelta
class educationdetail(models.Model):
    _name = 'education.detail'

    employee_id = fields.Many2one('hr.employee')
    level = fields.Char('Education Level')
    institute = fields.Char('Institute')
    marks = fields.Float('Marks (%)')



