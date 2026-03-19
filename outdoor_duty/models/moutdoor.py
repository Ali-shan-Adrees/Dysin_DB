from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
class outdoor_duty(models.Model):
    _name = "outdoor.duty"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'
    _order = 'id DESC'
    _description = 'Outdoor Request'
    name_seq = fields.Char(string='OD Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))

    job_no = fields.Char(string="Job No", states={'done': [('readonly', True)]})
    work_location = fields.Char(string="Visit location", required=True, states={'done': [('readonly', True)]})
    purpose = fields.Char(string="Purpose of visit", states={'done': [('readonly', True)]})
    emp_no = fields.Char(string="Employee No", related='employee_id.barcode', store=True)
    travel_from = fields.Char(string="Travel From", required=True)
    user_id = fields.Many2one('res.users','User', default=lambda self: self.env.user, readonly=True)
    team = fields.Many2many('res.users', string='Team members', states={'done': [('readonly', True)]})
    hod = fields.Many2one('res.users', string='Approved By HOD', readonly=True)
    sub_hod = fields.Many2one('res.users', string='Approved By Sub HOD', readonly=True)
    admin = fields.Many2one('res.users', string='Approved By Admin', readonly=True)
    travelling_date = fields.Datetime(string="Departure Date Time", required=True, default=fields.Date.context_today, states={'done': [('readonly', True)]})
    date = fields.Date(string="Date", default=fields.Date.context_today, states={'done': [('readonly', True)]})
    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_get_employee_id, required=True, states={'done': [('readonly', True)]})
    coach_id = fields.Many2one(related='employee_id.coach_id', store=True)
    department_id = fields.Many2one(related='employee_id.department_id', store=True)
    manager_id = fields.Many2one(related='department_id.manager_id', store=True)
    job_id = fields.Many2one(related='employee_id.job_id')
    work_email = fields.Char(related='employee_id.work_email')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('subhod', 'Sub HOD'),
        ('in_progress', 'HOD'),
        ('admin', 'Admin'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], default='draft', tracking=True, required=True)
    claim = fields.Selection([
        ('yes', 'Yes'),
        ('no','No')
    ],default='no', string='Warranty Claim', states={'done': [('readonly', True)]})
    invoice_to_customer = fields.Selection([
        ('yes','Yes'),
        ('no','No')
    ], default='yes', string='Invoice to Customer', states={'done': [('readonly', True)]})
    free_of_cost = fields.Selection([
        ('yes','Yes'),
        ('no','No')
    ], default='no', string='Free Of Cost', states={'done': [('readonly', True)]})
    vehicle = fields.Char(string='Inviduals accompanying the vehicle', states={'done': [('readonly', True)]})
    destination = fields.Char(string="Destination", states={'done': [('readonly', True)]})
    vehicle_retained = fields.Boolean(default=True, string='Vehicle to be retained', states={'done': [('readonly', True)]})
    vehicle_not_retained = fields.Boolean(default=False, string='Not Retained', states={'done': [('readonly', True)]})
    date_required = fields.Datetime(string='Date Required', states={'done': [('readonly', True)]})
    arrival_date = fields.Datetime(string='Estimated Arrival Date', states={'done': [('readonly', True)]})
    expected_arrival_date = fields.Datetime(string='Expected Arrival Date', required=True, states={'done': [('readonly', True)]})
    vehicle_no = fields.Char(string='Vehicle No', states={'done': [('readonly', True)]})
    driver = fields.Char(string='Driver Name', states={'done': [('readonly', True)]})
    m_reading_out = fields.Integer(string='Meter Reading Out', states={'done': [('readonly', True)]})
    m_reading_in = fields.Integer(string='Meter Reading In', states={'done': [('readonly', True)]})
    out_time = fields.Datetime(string='Out Time', states={'done': [('readonly', True)]})
    in_time = fields.Datetime(string='In Time', states={'done': [('readonly', True)]})
    attachment_out = fields.Binary(string='Meter Reading Out', attachment=True)
    attachment_in = fields.Binary(string='Meter Reading In', attachment=True)
    # reading = fields.Many2many('ir.attachment', string='Add meter reading shot')
    total_duration = fields.Integer(string='Total Duration', compute='_compute_duration', readonly=True)
    company_id = fields.Many2one('res.company', string="Company",default=lambda self: self.env.company, readonly=True)
    visit_details = fields.Text(string='Report')
    report_status = fields.Boolean(string='Report', default=False, readonly=True)
    audit_status = fields.Boolean(string='Audit', default=False, readonly=True)
    claim_status = fields.Boolean(default=False, string='Claim Status', readonly=True)
    narration = fields.Text(string='Narration', states={'done': [('readonly', True)]})
    outdoor_duty_ids = fields.One2many('od.visit.report.line', 'outdoor_duty_id', string='Visit Report Line', readonly=True)

    @api.depends('employee_id')
    def _compute_get_current_user(self):
        for rec in self:
            rec.user_id = self.env.user

    @api.depends('in_time')
    def _compute_duration(self):
        for rec in self:
            if rec.out_time and rec.in_time:
                dif = rec.in_time-rec.out_time
                diff_in_hours = dif.total_seconds() / 3600
                rec.total_duration = diff_in_hours
            else:
                rec.total_duration = 0


    def action_submit_user(self):
        for rec in self:
            rec.state = 'subhod'

    def action_approved_by_sub_hod(self):
        for rec in self:
            rec.state = 'in_progress'
            rec.sub_hod = self.env.user

    def action_approved_by_hod(self):
        for rec in self:
            rec.state = 'admin'
            rec.hod = self.env.user


    def action_done_admin(self):
        for rec in self:
            rec.state = 'done'
            rec.admin = self.env.user
            # weekdays = [5, 6]
            # cpl_lines = [(5, 0, 0)]
            # for dt in rec.daterange(rec.travelling_date, rec.expected_arrival_date):
            #     if dt.weekday() in weekdays:  # to print only the weekdates
            #         if dt.strftime("%A").lower():
            #             line_val = {
            #                 'date': dt.strftime("%Y-%m-%d"),
            #                 'dayName': dt.strftime("%A").lower(),
            #                 'totalDays': 1,
            #             }
            #             cpl_lines.append((0, 0, line_val))
            #
            # if len(cpl_lines) > 1:
            #     name_seq = self.env['ir.sequence'].next_by_code('leave.cpl.sequence')
            #     move = {
            #         'name_seq': name_seq,
            #         'date': rec.date,
            #         'employee_id': rec.employee_id.id,
            #         'subject': rec.purpose,
            #         'leaves_types': 'cpl',
            #         'od_id': rec.id,
            #         'note': rec.purpose,
            #         'cpl_line_ids': cpl_lines
            #     }
            # if len(cpl_lines) > 1:
            #     self.env['leave.cpl'].create(move)

    # def daterange(self, date1, date2):
    #     for n in range(int((date2 - date1).days) + 1):
    #         yield date1 + timedelta(n)

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'
    def action_audit_process(self):
        for rec in self:
            rec.audit_status = True

    def name_get(self):
        result = []
        for rec in self:
            name = '('+rec.name_seq+')'
            result.append((rec.id, name))
        return result


    def confirm_multi_outdoorduties(self):
        for record in self:
            if record.state == 'in_progress':
                record.action_approved_by_hod()



    @api.model
    def create(self, vals):
        today = date.today()
        travelling_date = vals['travelling_date']
        date_obj = datetime.strptime(travelling_date, '%Y-%m-%d %H:%M:%S').date()
        delta = today - date_obj
        total_days = delta.days
        para_days = self.env['ir.config_parameter'].get_param('outdoor_duty.previous_od_days')
        # print('Fetch Days : ', para_days)
        if total_days >= int(para_days):
            raise UserError(_(f"Sorry You can create only {para_days} days old (OD) request"))
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('outdoor.duty.sequence') or _('New')
        result = super(outdoor_duty, self).create(vals)
        return result

    @api.onchange('travelling_date')
    def onchange_date(self):
        today = date.today()
        travelling_date = self.travelling_date.strftime('%Y-%m-%d %H:%M:%S')
        date_obj = datetime.strptime(travelling_date, '%Y-%m-%d %H:%M:%S').date()
        delta = today - date_obj
        total_days = delta.days
        para_days = self.env['ir.config_parameter'].get_param('outdoor_duty.previous_od_days')
        if total_days >= int(para_days):
            raise UserError(_(f"Please can not select {para_days} days old date from now.."))


    def action_for_report(self):
        return {
            'type' : 'ir.actions.act_window',
            'res_model' : 'attach.report.wizards',
            'view_mode' : 'form',
            'target' : 'new'
        }

    def visited_report_action(self):
        return self.env.ref('outdoor_duty.action_visit_report_od').report_action(self)

    # @api.multi
    # def write(self, vals):
    #     today = datetime.now()
    #     d1 = self.travelling_date
    #     # d = datetime.datetime.strptime(d1, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d')
    #     print("Current Date Time = ", today)
    #     print("Travelling Date = ", d1)
    #
    #     delta = today - d1
    #     print("Total Delta Days", delta)
    #
    #     total_days = delta.days + 1
    #     print("Total Days", total_days)
    #
    #     if total_days >= 8:
    #         raise UserError(_("Sorry You can create only 7 days old OD"))
    #     else:
    #         return super().write(vals)



