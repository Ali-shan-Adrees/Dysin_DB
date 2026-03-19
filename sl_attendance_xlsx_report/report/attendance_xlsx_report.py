from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import timedelta, datetime, time
from collections import defaultdict
import pytz
from odoo import models


class AttendanceXlsxReport(models.AbstractModel):
    _name = 'report.custom_attendance.attendance_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data , wizard):
        if wizard.status == 'post':
            sheet = workbook.add_worksheet("Posted Attendance")

            # ================= STYLES =================
            title_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 15})
            month_format = workbook.add_format({'bold': True, 'align': 'center'})
            header_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
            left_format = workbook.add_format({'align': 'left', 'border': 1})
            red_format = workbook.add_format({'align': 'center', 'border': 1, 'bg_color': '#FF9999'})
            green_format = workbook.add_format({'align': 'center', 'border': 1, 'bg_color': '#92D050'})
            leave_format = workbook.add_format({'align': 'center', 'border': 1, 'bg_color': '#FFD966'})
            weekend_format = workbook.add_format(
                {'align': 'center', 'border': 1, 'italic': True, 'bg_color': '#D9D9D9'})
            holiday_format = workbook.add_format({'align': 'center', 'border': 1, 'bg_color': '#F4B084'})
            ta_format = workbook.add_format({'align': 'center', 'border': 1, 'bg_color': '#9BC2E6'})
            od_format = workbook.add_format({'align': 'center', 'border': 1, 'bg_color': '#C6E0B4'})

            # ================= DATES =================
            start_date = wizard.start_date
            end_date = wizard.end_date
            num_days = (end_date - start_date).days + 1
            days = [start_date + timedelta(days=i) for i in range(num_days)]

            total_cols = len(days) + 8  # S.No + Emp + Dept + Days + TA + OD + P + A + L

            # ================= TITLE =================
            sheet.merge_range(0, 0, 0, total_cols - 1, "Attendance Report", title_format)
            sheet.merge_range(1, 0, 1, total_cols - 1, start_date.strftime("%B %Y"), month_format)

            # ================= LEGEND (TOP) =================
            legend_row = 3
            sheet.write(legend_row, 1, "Legend", header_format)
            sheet.write(legend_row, 2, "P", green_format)
            sheet.write(legend_row, 3, "Present")
            sheet.write(legend_row, 4, "A", red_format)
            sheet.write(legend_row, 5, "Absent")
            sheet.write(legend_row, 6, "L", leave_format)
            sheet.write(legend_row, 7, "Leave")
            sheet.write(legend_row, 8, "TA", ta_format)
            sheet.write(legend_row, 9, "Travel Authority")
            sheet.write(legend_row, 10, "OD", od_format)
            sheet.write(legend_row, 12, "Outdoor Duty")
            sheet.write(legend_row, 13, "PH", holiday_format)
            sheet.write(legend_row, 14, "Public Holiday")
            sheet.write(legend_row, 15, "SAT/SUN", weekend_format)
            sheet.write(legend_row, 16, "Weekend")
            # sheet.merge_range(legend_row, legend_row, 2, 3, "", title_format)

            # ================= HEADER =================
            header_row = legend_row + 2
            sheet.write(header_row, 0, "S.No", header_format)
            sheet.write(header_row, 1, "Emp Code", header_format)
            sheet.write(header_row, 2, "Employee", header_format)
            sheet.write(header_row, 3, "Department", header_format)

            # Day columns (4 to 4+len(days)-1)
            for col, day in enumerate(days, start=4):
                sheet.write(header_row, col, day.day, header_format)

            # ✅ Total columns start AFTER all days
            total_start_col = 4 + len(days)

            sheet.write(header_row, total_start_col, "Total T.A", header_format)
            sheet.write(header_row, total_start_col + 1, "Total OD", header_format)
            sheet.write(header_row, total_start_col + 2, "Total P", header_format)
            sheet.write(header_row, total_start_col + 3, "Total A", header_format)
            sheet.write(header_row, total_start_col + 4, "Total L", header_format)

            # Calculate total columns for merge
            total_cols = total_start_col + 5

            sheet.freeze_panes(header_row + 1, 3)
            # ================= ATTENDANCE =================
            attendance_map = defaultdict(lambda: defaultdict(bool))
            attendances = self.env['hr.attendance'].search([
                ('check_in', '>=', start_date),
                ('check_in', '<=', end_date),
            ])
            for att in attendances:
                attendance_map[att.employee_id.id][att.check_in.date()] = True

            # ================= LEAVES =================
            leave_map = defaultdict(set)
            leaves = self.env['hr.leave'].search([
                ('state', '=', 'validate'),
                ('request_date_from', '<=', end_date),
                ('request_date_to', '>=', start_date),
            ])
            for leave in leaves:
                current = leave.request_date_from
                while current <= leave.request_date_to:
                    leave_map[leave.employee_id.id].add(current)
                    current += timedelta(days=1)

            # ================= TA =================
            ta_map = defaultdict(set)
            tas = self.env['travel.authority'].search([
                ('state', '=', 'done'),
                ('departure', '<=', datetime.combine(end_date, time.max)),
                ('arrival', '>=', datetime.combine(start_date, time.min)),
            ])
            for ta in tas:
                current = ta.departure.date()
                end = ta.arrival.date()
                while current <= end:
                    ta_map[ta.employee_id.id].add(current)
                    current += timedelta(days=1)

            # ================= OD =================
            od_map = defaultdict(set)
            ods = self.env['outdoor.duty'].search([
                ('state', '=', 'done'),
                ('travelling_date', '>=', datetime.combine(start_date, time.min)),
                ('travelling_date', '<=', datetime.combine(end_date, time.max)),
            ])
            for od in ods:
                od_map[od.employee_id.id].add(od.travelling_date.date())

            # ================= HOLIDAYS =================
            public_holidays = set()
            holidays = self.env['resource.calendar.leaves'].search([
                ('date_from', '<=', end_date),
                ('date_to', '>=', start_date),
                ('resource_id', '=', False),
            ])
            for h in holidays:
                d = h.date_from.date()
                while d <= h.date_to.date():
                    public_holidays.add(d)
                    d += timedelta(days=1)

            # ================= EMPLOYEES (DEPARTMENT ORDER) =================
            employees = self.env['hr.employee'].search([], order='department_id, name')

            row = header_row + 1
            sr_no = 1
            current_department = None

            for emp in employees:
                if emp.department_id != current_department:
                    current_department = emp.department_id
                    sheet.merge_range(
                        row, 0, row, total_cols - 1,
                                     current_department.name or 'No Department',
                        header_format
                    )
                    row += 1

                sheet.write(row, 0, sr_no, left_format)
                sheet.write(row, 1, emp.identification_id or '', left_format)
                sheet.write(row, 2, emp.name, left_format)
                sheet.write(row, 3, emp.department_id.name or '', left_format)

                total_p = total_a = total_l = total_ta = total_od = 0

                for col, day in enumerate(days, start=4):
                    if day in public_holidays:
                        sheet.write(row, col, 'PH', holiday_format)
                    elif day.weekday() in (5, 6):
                        sheet.write(row, col, 'SAT' if day.weekday() == 5 else 'SUN', weekend_format)
                    elif day in leave_map[emp.id]:
                        sheet.write(row, col, 'L', leave_format)
                        total_l += 1
                    elif day in ta_map[emp.id]:
                        sheet.write(row, col, 'TA', ta_format)
                        total_ta += 1
                        total_p += 1
                    elif day in od_map[emp.id]:
                        sheet.write(row, col, 'OD', od_format)
                        total_od += 1
                        total_p += 1
                    elif attendance_map[emp.id][day]:
                        sheet.write(row, col, 'P', green_format)
                        total_p += 1
                    else:
                        sheet.write(row, col, 'A', red_format)
                        total_a += 1

                # ✅ FIXED: Write totals at correct columns
                sheet.write(row, total_start_col, total_ta, ta_format)
                sheet.write(row, total_start_col + 1, total_od, od_format)
                sheet.write(row, total_start_col + 2, total_p, green_format)
                sheet.write(row, total_start_col + 3, total_a, red_format)
                sheet.write(row, total_start_col + 4, total_l, leave_format)

                sr_no += 1
                row += 1

        else:
            sheet = workbook.add_worksheet("Attendance Report")
            header_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
            title_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 15})
            sheet.merge_range(0, 0, 1, 8, "Attendance Report", title_format)

            # Set column widths
            sheet.set_column(0, 0, 5)  # Sr. #
            sheet.set_column(1, 1, 20)  # Employee
            sheet.set_column(2, 2, 20)  # Department
            sheet.set_column(3, 3, 12)  # Date
            sheet.set_column(4, 4, 15)  # Check In Time
            sheet.set_column(5, 5, 15)  # Check In Status
            sheet.set_column(6, 6, 15)  # Check Out Time
            sheet.set_column(7, 7, 17)  # Check Out Status
            sheet.set_column(8, 8, 15)  # Day Status
            sheet.set_column(9, 9, 20)  # Attendance Status

            # Headers
            headers = [
                    "Sr. #","Employee Code", "Employee","Designation", "Department", "Location", "Date",
                "Check In Time",
                "Check Out Time"
            ]
            # "Attendance Status"
            for col, head in enumerate(headers):
                sheet.write(2, col, head, header_format)

            # Wizard filters
            start_date = wizard.start_date
            end_date = wizard.end_date

            # Build domain for employees
            emp_domain = [('active', '=', True)]
            if wizard.employee_id:
                emp_domain.append(('id', '=', wizard.employee_id.id))
            if wizard.department_id:
                emp_domain.append(('department_id', '=', wizard.department_id.id))

            employees = self.env['hr.employee'].search(emp_domain, order='name')

            # Fetch attendances in date range
            att_domain = [('name', '>=', start_date), ('name', '<=', end_date)]
            attendances = self.env['hr.draft.attendance'].search(att_domain, order='employee_id, name')

            # Build map for quick lookup: {(employee_id, date): record(s)}
            attendance_map = {}
            for att in attendances:
                key = (att.employee_id.id, att.name.date())
                if key not in attendance_map:
                    attendance_map[key] = {'sign_in': None, 'sign_out': None}
                if att.attendance_status == 'sign_in':
                    attendance_map[key]['sign_in'] = att
                elif att.attendance_status == 'sign_out':
                    attendance_map[key]['sign_out'] = att

            # Iterate through all employees and date range
            row = 3
            sr_no = 1

            for emp in employees:
                current_date = start_date
                while current_date <= end_date:
                    key = (emp.id, current_date)
                    data = attendance_map.get(key, {})

                    check_in_time = ''
                    check_out_time = ''
                    day_status = ''
                    attendance_status = ''

                    if 'sign_in' in data and data['sign_in']:
                        att_in = data['sign_in']
                        user_tz = pytz.timezone(self.env.user.tz or 'UTC')
                        utc_time = att_in.name.replace(tzinfo=pytz.utc)
                        local_time = utc_time.astimezone(user_tz)
                        check_in_time = local_time.strftime('%H:%M:%S')
                        day_status = att_in.day_status or ''
                        attendance_status = att_in.attendance_status or 'Present'

                    if 'sign_out' in data and data['sign_out']:
                        att_out = data['sign_out']
                        utc_time = att_out.name.replace(tzinfo=pytz.utc)
                        local_time = utc_time.astimezone(user_tz)
                        check_out_time = local_time.strftime('%H:%M:%S')

                    # Write row
                    sheet.write(row, 0, sr_no)
                    sheet.write(row, 1, emp.employee_code or '')
                    sheet.write(row, 2, emp.name)
                    sheet.write(row, 3, emp.job_id.name or '')
                    sheet.write(row, 4, emp.department_id.name or '')
                    sheet.write(row, 5, emp.work_location_id.name or '')
                    sheet.write(row, 6, str(current_date))
                    sheet.write(row, 7, check_in_time)
                    sheet.write(row, 8, check_out_time)

                    row += 1
                    sr_no += 1
                    current_date += timedelta(days=1)
