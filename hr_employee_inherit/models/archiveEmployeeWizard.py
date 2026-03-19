from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
import datetime
from dateutil.relativedelta import relativedelta

class archive_employee_wizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    date_of_leaving = fields.Date(string="Leaving Date", required=True)
    departure_description = fields.Text(string="Reason")