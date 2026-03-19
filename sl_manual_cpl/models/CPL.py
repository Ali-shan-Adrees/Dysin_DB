from importlib.metadata import requires

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from num2words import num2words
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
class EmployeeCpl(models.Model):
    _name = "sl.manual.cpl"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name_seq'
    _order = 'id DESC'
    _description = 'CPL'
    name_seq = fields.Char(string='CPL No.', required=True, copy=False, readonly=True, index=True,
                           default=lambda self: _('New'))
    date = fields.Date(string="Date", default=fields.Date.context_today, states={'done': [('readonly', True)]})
    cpl_date = fields.Date(string="CPL Requested Date", required=True, states={'done': [('readonly', True)]})
    user_id = fields.Many2one('res.users', 'Requested By', default=lambda self: self.env.user, readonly=True)
    hod = fields.Many2one('res.users', string='Approved By HOD', readonly=True)
    approve_admin = fields.Many2one('res.users', string='Approved By Admin', readonly=True)


    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id

    employee_id = fields.Many2one('hr.employee', string="Request By", default=_get_employee_id, required=True,
                                  states={'done': [('readonly', True)]})
    coach_id = fields.Many2one(related='employee_id.coach_id', store=True)
    department_id = fields.Many2one(related='employee_id.department_id', store=True)
    job_id = fields.Many2one(related='employee_id.job_id', store=True)
    manager_id = fields.Many2one(related='department_id.manager_id', string='Head of Department', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('hod', 'HOD'),
        ('admin', 'Admin'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], default='draft', tracking=True, required=True)

    remarks = fields.Text(string='Note', required=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, readonly=True)


    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('employee.cpl.sequence') or _('New')
        result = super(EmployeeCpl, self).create(vals)
        return result

    @api.constrains('employee_id', 'cpl_date', 'state')
    def _check_duplicate_cpl(self):
        for rec in self:
            if not rec.employee_id or not rec.cpl_date:
                continue

            duplicate = self.search([
                ('id', '!=', rec.id),
                ('employee_id', '=', rec.employee_id.id),
                ('cpl_date', '=', rec.cpl_date),
                ('state', '!=', 'cancel')
            ], limit=1)

            if duplicate:
                raise ValidationError(
                    _("CPL already exists for this employee on %s.")
                    % rec.cpl_date
                )

    def action_submit_user(self):
        for rec in self:
            rec.state = 'hod'

    def action_approve_hod(self):
        for rec in self:
            rec.state = 'admin'
            rec.hod = self.env.user


    def action_approve_admin(self):
        HrLeaveAllocation = self.env['hr.leave.allocation']
        HrLeaveType = self.env['hr.leave.type']

        for rec in self:
            # 1️⃣ Get CPL Leave Type
            leave_type = HrLeaveType.search([
                ('name', '=', 'Compensatory Leaves'),
                ('company_id', 'in', [rec.company_id.id, False])
            ], limit=1)

            if not leave_type:
                raise ValidationError(_("Leave Type 'Compensatory Leaves' not found."))

            # 2️⃣ Create Leave Allocation (1 Day)
            allocation = HrLeaveAllocation.create({
                'name': _('CPL Allocation - %s') % rec.employee_id.name,
                'employee_id': rec.employee_id.id,
                'holiday_status_id': leave_type.id,
                'allocation_type': 'regular',
                'number_of_days': 1,
                'date_from': rec.cpl_date,
                'date_to': date(rec.cpl_date.year, 12, 31),

            })

            # 3️⃣ Approve Allocation
            allocation.action_confirm()
            allocation.action_validate()

            # 4️⃣ Update CPL Request
            rec.state = 'done'
            rec.approve_admin = self.env.user

    def action_approve_cancel(self):
        for rec in self:
            rec.state = 'cancel'

