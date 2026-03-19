from odoo import models
import xlsxwriter
from datetime import datetime

class HrAttendanceXlsx(models.AbstractModel):
    _name = 'report.sl_attendance_posted_report.hr_attendance_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet("Attendance Report")

        bold = workbook.add_format({'bold': True})
        border = workbook.add_format({'border':1})
        header_format = workbook.add_format({'bold': True, 'border':1, 'bg_color':'#D9D9D9'})

        headers = [
            'Employee Code', 'Employee Name', 'Department',
            'Check In', 'Check Out', 'In Time', 'Out Time',

        ]
        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_format)

        domain = [('check_in', '>=', wizard.date_from), ('check_in', '<=', wizard.date_to)]
        if wizard.employee_id:
            domain.append(('employee_id', '=', wizard.employee_id.id))
        if wizard.department_id:
            domain.append(('employee_id.department_id', '=', wizard.department_id.id))

        attendances = self.env['hr.attendance'].search(domain, order='check_in')

        for row, att in enumerate(attendances, start=1):
            in_time = att.check_in.time() if att.check_in else ''
            out_time = att.check_out.time() if att.check_out else ''

            sheet.write(row, 0, att.employee_id.barcode or att.employee_id.id, border)
            sheet.write(row, 1, att.employee_id.name, border)
            sheet.write(row, 2, att.employee_id.department_id.name, border)
            sheet.write(row, 3, att.check_in.strftime("%Y-%m-%d") if att.check_in else '', border)
            sheet.write(row, 4, att.check_out.strftime("%Y-%m-%d") if att.check_out else '', border)
            sheet.write(row, 5, str(in_time) if in_time else '', border)
            sheet.write(row, 6, str(out_time) if out_time else '', border)