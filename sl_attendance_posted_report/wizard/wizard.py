# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class AttendanceReportWizard(models.TransientModel):
    _name = 'sl.attendance.report.wizard'
    _description = 'Attendance Report Wizard'

    date_from = fields.Datetime(string="Start Date", required=True)
    date_to = fields.Datetime(string="End Date", default=fields.Date.today)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    department_id = fields.Many2one('hr.department', string="Department")

    def action_generate_excel(self):
        return self.env.ref('sl_attendance_posted_report.hr_attendance_xlsx_report').report_action(self)
