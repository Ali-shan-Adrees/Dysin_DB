from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
import datetime
from dateutil.relativedelta import relativedelta


class DaysOfWeek(models.Model):
    _name = 'days.week'

    name = fields.Char('Name')