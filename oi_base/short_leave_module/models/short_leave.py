from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError

class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    @api.model
    def create_monthly_short_leave_allocation(self):
        short_leave_type = self.env.ref('short_leave_module.short_leave_type')

        employees = self.env['hr.employee'].search([('active', '=', True)])
        today = fields.Date.today()
        first_of_month = today.replace(day=1)

        for employee in employees:
            existing_alloc = self.env['hr.leave.allocation'].search([
                ('employee_id', '=', employee.id),
                ('holiday_status_id', '=', short_leave_type.id),
                ('create_date', '>=', first_of_month),
            ])
            if not existing_alloc:
                self.create({
                    'name': 'Monthly Short Leave Allocation',
                    'employee_id': employee.id,
                    'holiday_status_id': short_leave_type.id,
                    'number_of_days': 2,
                    'allocation_type': 'regular',
                    'state': 'validate',
                })

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.constrains('request_date_from', 'request_date_to')
    def _check_short_leave_duration(self):
        for leave in self:
            if leave.holiday_status_id.code == 'short_leave':
                if leave.request_date_from and leave.request_date_to:
                    delta = leave.request_date_to - leave.request_date_from
                    hours = delta.total_seconds() / 3600
                    if hours > 2:
                        raise ValidationError("Short leave duration cannot exceed 2 hours.")
