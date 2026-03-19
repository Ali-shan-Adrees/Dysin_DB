from odoo import models, fields, api
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    payable_days = fields.Float(string="Payable Days", compute="_compute_payable_days", store=True)

    # ----------------------------------------------------
    # COMPUTE PAYABLE DAYS (NO WRITE ANYWHERE)
    # ----------------------------------------------------
    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_payable_days(self):
        for slip in self:
            slip.payable_days = slip._calculate_payable_days()

    # ----------------------------------------------------
    # CORE LOGIC
    # ----------------------------------------------------
    def _calculate_payable_days(self):
        self.ensure_one()

        date_from = self.date_from
        date_to = self.date_to
        employee = self.employee_id
        calendar = employee.resource_calendar_id

        payable_days = 0.0

        # 1️⃣ PRESENT DAYS (distinct days)
        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', date_from),
            ('check_in', '<=', date_to),
        ])
        present_days = len(set(a.check_in.date() for a in attendances))
        print("Present day", present_days)
        payable_days += present_days

        # 2️⃣ PAID LEAVES
        paid_leaves = self.env['hr.leave'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate'),
            ('holiday_status_id.is_paid', '=', True),
            ('request_date_from', '<=', date_to),
            ('request_date_to', '>=', date_from),
        ])
        print("Paid Leaves", sum(l.number_of_days for l in paid_leaves))
        payable_days += sum(l.number_of_days for l in paid_leaves)

        # 3️⃣ HALF DAY LEAVES
        half_days = self.env['hr.leave'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate'),
            ('holiday_status_id.request_unit', '=', 'half_day'),
            ('request_date_from', '<=', date_to),
            ('request_date_to', '>=', date_from),
        ])
        print("half Days", sum(l.number_of_days * 0.5 for l in half_days) )
        payable_days += sum(l.number_of_days * 0.5 for l in half_days)

        # 4️⃣ SHORT LEAVE (hours → days)
        short_leaves = self.env['hr.leave'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate'),
            ('holiday_status_id.request_unit', '=', 'hour'),
            ('request_date_from', '<=', date_to),
            ('request_date_to', '>=', date_from),
        ])
        print("Short Leave", sum(l.number_of_hours / 8 for l in short_leaves))
        payable_days -= sum(l.number_of_hours / 8 for l in short_leaves)

        # 5️⃣ PUBLIC HOLIDAYS
        print("Public Holidays", self._count_working_calendar_leaves(calendar, date_from, date_to))
        payable_days += self._count_working_calendar_leaves(calendar, date_from, date_to)

        return max(payable_days, 0.0)

    def _count_working_calendar_leaves(self, calendar, date_from, date_to):
        """
           Count UNIQUE calendar leave days (prevents double counting)
           """
        if not calendar:
            return 0.0

        leave_dates = set()

        leaves = self.env['resource.calendar.leaves'].search([
            '|',
            ('calendar_id', '=', calendar.id),
            ('calendar_id', '=', False),
            ('date_from', '<=', date_to),
            ('date_to', '>=', date_from),
        ])

        for leave in leaves:
            start = max(leave.date_from.date(), date_from)
            end = min(leave.date_to.date(), date_to)

            current = start
            while current <= end:
                leave_dates.add(current)
                current += timedelta(days=1)

        return float(len(leave_dates))

    # def _get_worked_day_lines(self, domain=None):
    #     res = super()._get_worked_day_lines(domain)
    #
    #     for slip in self:
    #         if slip.payable_days:
    #             res.append((0, 0, {
    #                 'name': 'Payable Days',
    #                 'code': 'PAYDAYS',
    #                 'number_of_days': slip.payable_days,
    #                 'number_of_hours': slip.payable_days * 9,
    #                 'contract_id': slip.contract_id.id,
    #             }))
    #     return res
