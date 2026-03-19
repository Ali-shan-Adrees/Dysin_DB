from odoo import models, fields, api, _
from datetime import datetime, timedelta, date

class AttendanceReportWizard(models.TransientModel):
    _name = 'attendance.report.wizard'
    _description = 'Attendance Report Wizard'

    start_date = fields.Date(required=True, default=date.today().replace(day=1))
    end_date = fields.Date(required=True, default=date.today())
    employee_id = fields.Many2one('hr.employee', string="Employee")
    department_id = fields.Many2one('hr.department', string="Department")
    status = fields.Selection([('draft', 'Draft'), ('post', 'Posted')], string='Att Status', required=True)

    def _daterange_dates(self, start_dt, end_dt):
        """Return list of date objects from start_date to end_date inclusive."""
        days = []
        cur = start_dt
        while cur <= end_dt:
            days.append(cur)
            cur += timedelta(days=1)
            print('Days', days)
        return days

    def _count_weekends(self, start_dt, end_dt):
        """Count Saturdays and Sundays in range (inclusive)."""
        count = 0
        for d in self._daterange_dates(start_dt, end_dt):
            if d.weekday() in (5, 6):  # 5=Saturday, 6=Sunday
                count += 1
        return count

    def _count_public_holidays(self, start_dt, end_dt, company=None):
        """
        Try to find public holidays. This depends on your implementation.
        Default: attempt to use model 'hr.leave.public.holiday' or fallback to 0.
        Adjust this to your module's public holiday model if different.
        """
        try:
            PublicHoliday = self.env['resource.calendar.leaves']
        except Exception:
            # fallback: try other known names or return 0
            return 0

        domain = [('date', '>=', start_dt), ('date', '<=', end_dt)]
        # if model has company or country you may filter
        holidays = PublicHoliday.search(domain)
        print('Public Holiday', holidays)
        return len(holidays)

    def _get_employees(self):
        """Return employee recordset based on wizard filters."""
        Employee = self.env['hr.employee']
        domain = []
        if self.employee_id:
            return self.employee_id
        if self.department_id:
            domain = [('department_id', '=', self.department_id.id)]
        # only active employees by default
        domain += [('active', '=', True)]
        return Employee.search(domain, order='department_id, name')

    def _employee_attendance_present_dates(self, employee, start_dt, end_dt):
        """
        Return a set of dates (date objects) where employee has at least one hr.attendance.check_in
        between start_dt and end_dt.
        """
        Att = self.env['hr.attendance']
        # search check_in within datetime boundaries; convert date -> datetime beginning and end
        start_dt_dt = datetime.combine(start_dt, datetime.min.time())
        end_dt_dt = datetime.combine(end_dt, datetime.max.time())
        atts = Att.search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', start_dt_dt),
            ('check_in', '<=', end_dt_dt),
        ])
        dates = set()
        for a in atts:
            if a.check_in:
                dates.add(fields.Date.to_date(a.check_in))
        return dates

    def _employee_leaves_summary(self, employee, start_dt, end_dt):
        """
        Return dict: {'total_leaves': int, 'unpaid_leaves': int}
        Counts leaves from hr.leave that overlap the date range and are validated.
        """
        Leave = self.env['hr.leave']
        # Search leaves that overlap the period. hr.leave usually has date_from, date_to (datetimes)
        # We'll use overlapping condition: (date_from <= end) AND (date_to >= start)
        start_dt_dt = datetime.combine(start_dt, datetime.min.time())
        end_dt_dt = datetime.combine(end_dt, datetime.max.time())
        domain = [
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate'),
            ('date_from', '<=', end_dt_dt),
            ('date_to', '>=', start_dt_dt),
        ]
        leaves = Leave.search(domain)

        total_days = 0.0
        unpaid_days = 0.0

        for l in leaves:
            # compute overlapping days between leave and our window
            leave_start = fields.Datetime.to_datetime(l.date_from)
            leave_end = fields.Datetime.to_datetime(l.date_to)
            # normalize to date boundaries
            overlap_start = max(leave_start, start_dt_dt)
            overlap_end = min(leave_end, end_dt_dt)
            # convert to date and count days (approx): add 1 day for inclusive if time spans >= 24h
            days = (overlap_end.date() - overlap_start.date()).days + 1
            if days < 0:
                continue
            total_days += days

            # determine if unpaid
            is_unpaid = False
            # heuristic 1: holiday_status_id has 'is_paid' boolean
            if hasattr(l, 'holiday_status_id') and l.holiday_status_id:
                if hasattr(l.holiday_status_id, 'is_paid'):
                    is_unpaid = not bool(l.holiday_status_id.is_paid)
            # heuristic 2: leave record itself has 'unpaid' boolean
            if not is_unpaid and hasattr(l, 'unpaid'):
                is_unpaid = bool(l.unpaid)
            # heuristic 3: fallback to type name contains 'unpaid'
            if not is_unpaid and l.holiday_status_id and l.holiday_status_id.name:
                if 'unpaid' in (l.holiday_status_id.name or '').lower():
                    is_unpaid = True

            if is_unpaid:
                unpaid_days += days

        return {
            'total_leaves': int(total_days),
            'unpaid_leaves': int(unpaid_days),
        }

    def _build_report_data(self):
        """Return structured data grouped by department for the report template."""
        start_dt = fields.Date.to_date(self.start_date)
        end_dt = fields.Date.to_date(self.end_date)
        days_total = (end_dt - start_dt).days + 1
        weekends = self._count_weekends(start_dt, end_dt)
        public_holidays = self._count_public_holidays(start_dt, end_dt)
        employees = self._get_employees()

        # Group by department: {department: [employee rows]}
        grouped = {}
        for emp in employees:
            # present dates (set)
            present_dates = self._employee_attendance_present_dates(emp, start_dt, end_dt)
            present_count = len(present_dates)

            # leaves
            leave_summary = self._employee_leaves_summary(emp, start_dt, end_dt)
            total_leaves = leave_summary['total_leaves']
            unpaid_leaves = leave_summary['unpaid_leaves']

            # total holidays = weekends + public holidays (we count full period same for all employees)
            total_holidays = weekends + public_holidays

            # working days (exclude holidays)
            working_days = days_total - total_holidays
            # absent = working_days - (present + total_leaves) ; lower bound 0
            absent = working_days - (present_count + total_leaves)
            if absent < 0:
                absent = 0

            row = {
                'employee_id': emp.id,
                'employee_code': getattr(emp, 'employee_code', ''),
                'name': emp.name,
                'designation': emp.job_id.name if emp.job_id else '',
                'present': present_count,
                'total_leaves': total_leaves,
                'total_holidays': total_holidays,
                'unpaid_leaves': unpaid_leaves,
                'absent': int(absent),
            }

            dept = emp.department_id or self.env['hr.department'].browse([False])
            dept_key = (dept.id or 0, dept.name or 'No Department')
            grouped.setdefault(dept_key, []).append(row)

        # Build clean structure for template: list of departments with rows
        data = []
        for (dept_id, dept_name), rows in grouped.items():
            data.append({
                'department_id': dept_id,
                'department_name': dept_name,
                'employees': rows,
            })

        return {
            'start_date': start_dt,
            'end_date': end_dt,
            'days_total': days_total,
            'public_holidays': public_holidays,
            'weekends': weekends,
            'departments': data,
        }

    def action_print_report(self):
        """Return QWeb PDF action. The template name is 'attendance.report_pdf' (adjust if you change)."""
        data = self._build_report_data()
        # pass data through context or use report_action with data argument (preferred)
        return self.env.ref('sl_attendance_xlsx_report.attendance_report_pdf').report_action(self, data={'report_data': data})

    def action_download_excel(self):
        return self.env.ref('sl_attendance_xlsx_report.action_download_attendance_excel').report_action(self)
