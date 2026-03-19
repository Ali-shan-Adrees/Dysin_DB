from email.policy import default

from odoo import api, fields, models, _
import re
from odoo.exceptions import ValidationError, AccessError
import datetime
from dateutil.relativedelta import relativedelta


class odVisitReportline(models.Model):
    _name = 'od.visit.report.line'
    _description = 'Outdoor Duty Report'

    outdoor_duty_id = fields.Many2one('outdoor.duty', string='OD No')
    partner_id = fields.Many2one('res.partner', string='Partner')
    sales_team = fields.Many2one('crm.team', string='Sales Team')
    visit_date = fields.Datetime(string='Visit Date')
    visit_end_date = fields.Datetime(string='Visit End Date')
    description = fields.Text(string='Description')
    lead_id = fields.Many2one('crm.lead', string="Lead/Opportunity")
    visit_type = fields.Selection([
        ('1', 'Select Visit Type'),
        ('2', 'New Query'),
        ('3', 'Follow up'),
        ('4', 'Lead'),
        ('5', 'Qualified Lead'),
        ('8', 'Other'),
    ], string='Visit Type', default='')


class taVisitReportline(models.Model):
    _name = 'ta.visit.report.line'
    _description = 'Travel Authority Report'

    travel_authority_id = fields.Many2one('travel.authority', string='Travel Authority')
    partner_id = fields.Many2one('res.partner', string='Partner')
    sales_team = fields.Many2one('crm.team', string='Sales Team')
    visit_date = fields.Datetime(string='Visit Date')
    visit_end_date = fields.Datetime(string='Visit End Date')
    description = fields.Text(string='Description')
    lead_id = fields.Many2one('crm.lead', string="Lead/Opportunity")
    visit_type = fields.Selection([
        ('1', 'Select Visit Type'),
        ('2', 'New Query'),
        ('3', 'Follow up'),
        ('4', 'Lead'),
        ('5', 'Qualified Lead'),
        ('8', 'Other'),
    ], string='Visit Type', default='')
