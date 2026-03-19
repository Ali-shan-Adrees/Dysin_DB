from importlib.metadata import requires

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from num2words import num2words
from datetime import timedelta, time, datetime
from datetime import date
from dateutil.relativedelta import relativedelta

class ManualAttendance(models.Model):
    _name = "manual.attendance"
    _description = "Manual Attendance Request"
    _rec_name = 'name_seq'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name_seq = fields.Char(
        string="Request No",
        default=lambda self: _("New"),
        readonly=True,
        copy=False,
        tracking=True
    )


    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id.id)
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        default=lambda self: self.env.user.employee_id.id
    )

    user_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user,
        readonly=True
    )

    department_id = fields.Many2one(
        "hr.department",
        related="employee_id.department_id",
        store=True
    )

    manager_id = fields.Many2one(
        "hr.employee",
        related="employee_id.parent_id",
        store=True,
    )

    coach_id = fields.Many2one(
        'hr.employee',
        related='employee_id.coach_id',
        store=True,
    )
    check_in = fields.Datetime(
        string="Check In Date",
        required=True,
        tracking=True,
        default=lambda self: fields.Datetime.now().replace(hour=4, minute=0, second=0, microsecond=0)
    )
    check_out = fields.Datetime(string="Check Out Date", required=True)

    @api.onchange('check_in')
    def _onchange_check_in(self):
        for rec in self:
            if rec.check_in:
                check_in_date = rec.check_in.date()
                dt = datetime.combine(check_in_date, time(18, 0, 0))
                rec.check_out = dt - timedelta(hours=5)

    date = fields.Date(
        string="Attendance Date",
        required=True,
        default=fields.Date.context_today
    )
    remarks = fields.Text(string="Remarks")

    hod = fields.Many2one('res.users', string='Approved By HOD', readonly=True)
    approve_admin = fields.Many2one('res.users', string='Approved By Admin', readonly=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("hod", "HOD"),
        ("admin", "Admin"),
        ("done", "Approved"),
        ("cancel", "Cancelled"),
    ], default="draft", tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name_seq', 'New') == 'New':
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('manual.attendance') or 'New'
        return super(ManualAttendance, self).create(vals)

    def action_submit(self):
        self.state = "hod"

    def action_approve_hod(self):
        for rec in self:
            rec.state = "admin"
            rec.hod = self.env.user

    def action_approve_admin(self):
        for rec in self:
            rec.state = "done"
            rec.approve_admin = self.env.user

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_duplicate_attendance(self):
        HrAttendance = self.env['hr.attendance']

        for rec in self:
            if not rec.check_in or not rec.check_out:
                continue

            check_in_date = rec.check_in.date()

            start_dt = datetime.combine(check_in_date, datetime.min.time())
            end_dt = datetime.combine(check_in_date, datetime.max.time())

            existing_attendance = HrAttendance.search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_in', '>=', start_dt),
                ('check_in', '<=', end_dt),
                ('check_out', '!=', False),
            ], limit=1)

            if existing_attendance:
                raise ValidationError(
                    "Attendance already exists for this employee on this date."
                )

    def action_approve_cancel(self):
        self.state = "cancel"
    def action_set_draft(self):
        self.state = "draft"

class EmployeeGradeProfile(models.Model):
    _inherit = 'hr.employee'

    # expense_manager_id = fields.Many2one("hr.employee", string="Expense Manager")
    employee_code = fields.Char(
        string="Employee Code",
        copy=False,
        tracking=True,
        default=lambda self: "EMP/%s" % (self.env['hr.employee'].search_count([]) + 1)
    )