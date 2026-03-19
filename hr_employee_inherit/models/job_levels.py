
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class JobLevels(models.Model):
    _name = 'job.levels'
    _description = 'Job levels'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)

    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True,
                                       relation="res.currency")
    name = fields.Char('Name', tracking=True, required=1)
    minimum_salary = fields.Monetary('Minimum Salary', currency_field='company_currency', tracking=True, required=1)
    maximum_salary = fields.Monetary('Maximum Salary', currency_field='company_currency', tracking=True, required=1)
    petrol_liter = fields.Integer('Petrol (Liter)', tracking=True)
    mobile_package = fields.Char('Mobile Package', tracking=True)
    car_allocation = fields.Char('Car Allocation', tracking=True)
    system_required = fields.Selection([('Laptop', 'Laptop'), ('Desktop', 'Desktop'), ('None', 'None')], string='System', tracking=True, required=1)
    entertainment_budget = fields.Monetary('Entertainment Budget', currency_field='company_currency', tracking=True, required=1)
    daily_allowance = fields.Monetary('Daily Allowance', currency_field='company_currency', tracking=True, required=1)
    hotel_accommodation = fields.Monetary('Hotel Accommodation', currency_field='company_currency', tracking=True, required=1)
    personal_stay_allowance = fields.Monetary('Personal Stay Allowance',
                                              currency_field='company_currency',
                                              tracking=True, required=1)

    @api.model
    def create(self, vals):
        vals['name'] = vals.get('name').upper()
        if vals.get('minimum_salary') <= 0:
            raise ValidationError('Minimum Salary must be greater than 0')
        if vals.get('maximum_salary') <= 0:
            raise ValidationError('Maximum Salary must be greater than 0')
        if vals.get('maximum_salary') < vals.get('minimum_salary'):
            raise ValidationError('Maximum Salary must be greater than Minimum Salary')
        if vals.get('daily_allowance') <= 0:
            raise ValidationError('Daily Allowance must be greater than 0')
        if vals.get('hotel_accommodation') <= 0:
            raise ValidationError('Hotel Accommodation must be greater than 0')
        if vals.get('personal_stay_allowance') <= 0:
            raise ValidationError('Personal Stay Allowance must be greater than 0')
        levels = super(JobLevels, self).create(vals)
        check_name = self.search([('name', '=',  vals['name']), ('id', '!=',  levels.ids[0])])
        if len(check_name) > 0:
            raise ValidationError('Level already exist')
        return levels
