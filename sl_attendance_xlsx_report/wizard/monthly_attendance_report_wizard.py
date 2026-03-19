from odoo import models, fields
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import pytz


class SLAttendanceReportWizard(models.TransientModel):
    _name = "sl.attendance.report.wizard"
    _description = "Attendance Report Wizard"

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    department_id = fields.Many2one("hr.department", string="Department")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    attendance_status = fields.Selection([
        ('posted', 'Posted'),
        ('unposted', 'Unposted')
    ], string="Attendance Status", required=True, default="posted")

    def action_print_pdf(self):
        if self.start_date > self.end_date:
            raise UserError("Start Date cannot be after End Date.")

        return self.env.ref(
            "sl_attendance_xlsx_report.sl_attendance_report_pdf_action"
        ).report_action(self)

    def _get_attendance_records(self):
        user_tz = self.env.user.tz or 'UTC'
        tz = pytz.timezone(user_tz)
        data = []

        # Get employees based on filters
        emp_domain = []
        if self.employee_id:
            emp_domain.append(('id', '=', self.employee_id.id))
        if self.department_id:
            emp_domain.append(('department_id', '=', self.department_id.id))

        employees = self.env['hr.employee'].search(emp_domain)

        # Generate all dates between start and end date
        start_date = fields.Date.from_string(self.start_date)
        end_date = fields.Date.from_string(self.end_date)
        date_range = [
            start_date + timedelta(days=i)
            for i in range((end_date - start_date).days + 1)
        ]

        if self.attendance_status == 'posted':
            # Fetch posted attendances
            domain = [
                ('check_in', '>=', self.start_date),
                ('check_in', '<=', self.end_date)
            ]
            if self.employee_id:
                domain.append(('employee_id', '=', self.employee_id.id))
            if self.department_id:
                domain.append(('employee_id.department_id', '=', self.department_id.id))

            attendances = self.env['hr.attendance'].search(domain, order="employee_id, check_in, id")

            # Group by employee and date
            grouped = {}
            for rec in attendances:
                check_in = rec.check_in.astimezone(tz) if rec.check_in else None
                check_out = rec.check_out.astimezone(tz) if rec.check_out else None
                key = (rec.employee_id.id, check_in.date() if check_in else None)
                grouped[key] = {
                    "employee": rec.employee_id.name,
                    "department": rec.employee_id.department_id.name or '',

                    "check_in": check_in,
                    "check_out": check_out,
                    "status": "Posted",
                }

            # Ensure all employees/dates are included
            for emp in employees:
                for d in date_range:
                    key = (emp.id, d)
                    data.append(grouped.get(key, {
                        "employee": emp.name,
                        "department": emp.department_id.name or '',
                        "check_in": None,
                        "check_out": None,
                        "status": "No Attendance",
                    }))

        else:
            # Unposted attendances (draft)
            domain = [
                ('name', '>=', self.start_date),
                ('name', '<=', self.end_date)
            ]
            if self.employee_id:
                domain.append(('employee_id', '=', self.employee_id.id))
            if self.department_id:
                domain.append(('employee_id.department_id', '=', self.department_id.id))

            draft_attendances = self.env['hr.draft.attendance'].search(domain, order="employee_id, name, id")

            grouped = {}
            for rec in draft_attendances:
                dt = rec.name if isinstance(rec.name, datetime) else fields.Datetime.from_string(rec.name)
                dt = dt.astimezone(tz)
                key = (rec.employee_id.id, dt.date())

                if key not in grouped:
                    grouped[key] = {
                        "employee": rec.employee_id.name,
                        "department": rec.employee_id.department_id.name or '',
                        "date": dt.date(),
                        "check_in": None,
                        "check_out": None,
                        "status": "Unposted",
                    }

                if rec.attendance_status == 'sign_in':
                    grouped[key]["check_in"] = dt
                elif rec.attendance_status == 'sign_out':
                    grouped[key]["check_out"] = dt

            # Ensure all employees/dates are included
            for emp in employees:
                for d in date_range:
                    key = (emp.id, d)
                    data.append(grouped.get(key, {
                        "employee": emp.name,
                        "department": emp.department_id.name or '',
                        "check_in": None,
                        "check_out": None,
                        "status": "No Attendance",
                    }))

        return data


class ReportAttendancePDF(models.AbstractModel):
    _name = "report.sl_attendance_xlsx_report.attendance_pdf"
    _description = "Attendance Report PDF"

    def _get_report_values(self, docids, data=None):
        docs = self.env["sl.attendance.report.wizard"].browse(docids)
        return {
            "doc_ids": docids,
            "doc_model": "sl.attendance.report.wizard",
            "docs": docs,
            "attendance_data": docs._get_attendance_records(),
        }
