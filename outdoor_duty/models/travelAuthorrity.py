from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date
from datetime import datetime

class TravelAuthority(models.Model):
    _name = 'travel.authority'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'
    _description = 'Travel Authority'
    _order = 'name_seq desc'

    name_seq = fields.Char(string='Leave Request No', required=True, copy=False, readonly=True, index=True,
                           default=lambda self: _('New'))
    date = fields.Date(string="Date", default=fields.Date.context_today, required=True, states={'done': [('readonly', True)]})
    departure = fields.Datetime(string="Departure Date", default=fields.Date.context_today, required=True, states={'done': [('readonly', True)]})
    arrival = fields.Datetime(string="Expected arrival date", required=True, states={'done': [('readonly', True)]})

    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id
    
    employee_id = fields.Many2one('hr.employee', string='Name', default= _get_employee_id, required=True, states={'done': [('readonly', True)]})
    partner_id = fields.Many2one('res.partner', string='Customer', states={'done': [('readonly', True)]})
    job_id = fields.Many2one(related='employee_id.job_id', string='Designation', store=True)
    emp_no = fields.Char(string="Employee No", related='employee_id.barcode', store=True)
    department_id = fields.Many2one(string='Department', store=True, related='employee_id.department_id')
    manager_id = fields.Many2one(string='Manager', related='employee_id.parent_id')
    coach_id = fields.Many2one(string='SUB HOD', related='employee_id.coach_id', store=True, )
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, states={'done': [('readonly', True)]})
    user_id = fields.Many2one('res.users', string='Requested by',readonly=True, default=lambda self: self.env.user)
    team = fields.Many2many('res.users', string='Team members', states={'done': [('readonly', True)]})
    hod = fields.Many2one('res.users', string='HOD', readonly=True)
    sub_hod = fields.Many2one('res.users', string='Sub HOD', readonly=True)
    audit = fields.Many2one('res.users', string='Approved By', readonly=True)
    cfo = fields.Many2one('res.users', string='Approved By', readonly=True)
    purpose = fields.Char(string='Purpose of visit', required=True, states={'done': [('readonly', True)]})
    visit_location = fields.Char(string='Place(s) to visit', required=True, states={'done': [('readonly', True)]})
    travel_route = fields.Char(string='Travel Route', required=True, states={'done': [('readonly', True)]})
    payment_id = fields.Many2one('account.move', string='Voucher No', readonly=True)
    travel_mode = fields.Selection([
        ('bus', 'Bus'),
        ('daewoo', 'Daewoo'),
        ('coach', 'Coach'),
        ('train', 'Train'),
        ('taxi', 'Taxi'),
        ('own_car', 'Own Car'),
        ('company_car', 'Company Car'),
        ('by_air', 'By Air')
    ], string='Mode of travel', required=True, states={'done': [('readonly', True)]})
    expense_line_ids = fields.One2many('expense.types.line', 'travel_authority_id', states={'done': [('readonly', True)]}, string='Expense line')
    total = fields.Float(string='Total', readonly=True, default=0, compute='_compute_total_expense', store=True)
    visit_details = fields.Text(string='Report')
    report_status = fields.Boolean(string='Report status')
    paid_amount = fields.Float(string='Paid amount', tracking=True,)
    narration = fields.Text(string="Narration" , required=True, tracking=True, states={'done': [('readonly', True)]})
    audit_status = fields.Boolean(string='Audit status', readonly=True)
    travel_from = fields.Char(string="Travel From", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('subhod', 'Sub HOD'),
        ('hod', 'HOD'),
        ('audit', 'Audit'),
        ('cfo', 'CFO'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], default='draft', tracking=True, required=True)
    travel_authority_report_ids = fields.One2many('ta.visit.report.line', 'travel_authority_id', string='T.A Report', readonly=True)

    @api.model
    def create(self, vals):
        today = date.today()
        travelling_date = vals['departure']
        date_obj = datetime.strptime(travelling_date, '%Y-%m-%d %H:%M:%S').date()
        delta = today - date_obj
        total_days = delta.days
        para_days = self.env['ir.config_parameter'].get_param('outdoor_duty.previous_od_days')
        if total_days >= int(para_days):
            raise UserError(_(f"Sorry You can create only {para_days} days old (T.A)"))

        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('travel.authority.sequence') or _('New')
        result = super(TravelAuthority, self).create(vals)
        return result

    @api.onchange('departure')
    def onchange_date(self):
        today = date.today()
        departure_date = self.departure.strftime('%Y-%m-%d %H:%M:%S')
        date_obj = datetime.strptime(departure_date, '%Y-%m-%d %H:%M:%S').date()
        delta = today - date_obj
        total_days = delta.days
        para_days = self.env['ir.config_parameter'].get_param('outdoor_duty.previous_od_days')
        if total_days >= int(para_days):
            raise UserError(_(f"Please can not select {para_days} days old date from now.."))

    @api.depends('expense_line_ids')
    def _compute_total_expense(self):

        for rec in self:
            total_val = 0
            for line in rec.expense_line_ids:
                total_val += line.sub_total
        self.total = total_val


    def action_submitted(self):
        for rec in self:
            rec.state = 'subhod'

    def action_sub_hod(self):

        for rec in self:
            rec.state = 'hod'
            rec.sub_hod = self.env.user
    def action_approved_by_hod(self):
        for rec in self:
            ta_audit_mandatory = self.env['ir.config_parameter'].get_param('outdoor_duty.ta_audit_mandatory')
            if ta_audit_mandatory == 'True':
                rec.state = 'audit'
                rec.hod = self.env.user
            else:
                rec.state = 'cfo'
                rec.hod = self.env.user


    def action_approved_by_audit(self):
        for rec in self:
            rec.state = 'cfo'
            rec.audit_status = True
            rec.audit = self.env.user
    def action_approved_by_cfo(self):
        for rec in self:
            rec.state = 'done'
            rec.cfo = self.env.user

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def name_get(self):
        result = []
        for rec in self:
            name = '('+rec.name_seq+')'
            result.append((rec.id, name))
        return result


    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_for_travel_authority_report(self):
        return {
            'type' : 'ir.actions.act_window',
            'res_model' : 'travel.authority.wizards',
            'view_mode' : 'form',
            'target' : 'new'
        }
    def pay_now_amount(self):
        return {
            'type' : 'ir.actions.act_window',
            'res_model' : 'pay.amount.wizards',
            'view_mode' : 'form',
            'target' : 'new',
            'context': {
                'default_amount': self.total or 0.0,
                'default_reference': f"{self.name_seq} - {self.narration}" or '',
                'default_partner_id': self.user_id.partner_id.id
            },
        }
    def visited_report_action(self):
        return self.env.ref('outdoor_duty.action_visit_report_travel_authority').report_action(self)



class expenseTypeline(models.Model):
    _name = 'expense.types.line'
    _description = 'Expense Description'

    expense_id = fields.Many2one('expense.types', string='Type of Expense')
    descript = fields.Char(string='Desc. of Expense')
    days = fields.Integer(string='No of Days', default=1)
    rate = fields.Integer(string='Rate/day', default=0)
    sub_total = fields.Float(string='Total', compute='_compute_sub_total')
    travel_authority_id = fields.Many2one('travel.authority', string='Travel Authority')

    @api.depends('days','rate')
    def _compute_sub_total(self):
        for rec in self:
            rec.sub_total = rec.days*rec.rate


