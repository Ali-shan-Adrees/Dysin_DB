# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, time
from pytz import timezone, UTC
#
class HrDraftAttendance(models.Model):
    _name = 'hr.draft.attendance'
    _description = 'Draft Attendance'
    _inherit = ['mail.thread']
    _order = 'name desc'

    name = fields.Datetime('Datetime', tracking=True)
    date = fields.Date('Date', tracking=True)
    day_name = fields.Char('Day', tracking=True)
    attendance_status = fields.Selection([
        ('sign_in', 'Sign In'), ('sign_out', 'Sign Out'), ('sign_none', 'None')],
        'Attendance State', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    lock_attendance = fields.Boolean('Lock Attendance', tracking=True)
    biometric_attendance_id = fields.Integer('Biometric Attendance ID', tracking=True)
    is_missing = fields.Boolean('Missing', default=False, tracking=True)
    moved = fields.Boolean(default=False)
    moved_to = fields.Many2one('hr.attendance', string='Moved to HR Attendance')
    check_in_status = fields.Selection([
        ('la', 'LA'), ('sla', 'SLA'), ('hda', 'HDA'), ('od', 'OD'), ('ab', 'AB'), ('ok', 'OK')],
        string="Arrival Status", readonly=True)
    check_out_status = fields.Selection([
        ('ed', 'ED'), ('sld', 'SLD'), ('hdd', 'HDD'), ('od', 'OD'), ('ab', 'AB'), ('ok', 'OK')],
        string="Departure Status", readonly=True)
    day_status = fields.Selection([
        ('p', 'P'), ('a', 'A'), ('sla', 'SLA'), ('hda', 'HDA')],
        string='Day Status', readonly=True)

    def unlink(self):
        for rec in self:
            if rec.moved:
                raise UserError(_("You can't delete Moved Attendance"))
        return super(HrDraftAttendance, self).unlink()

    def create(self, vals):
        vals = self._compute_attendance_status(vals)
        return super().create(vals)

    def write(self, vals):
        for record in self:
            updated_vals = vals.copy()
            updated_vals = record._compute_attendance_status(updated_vals, current_status=record.attendance_status)
            super(HrDraftAttendance, record).write(updated_vals)
        return True

    def _compute_attendance_status(self, vals, current_status=None):
        name = vals.get('name')
        status = vals.get('attendance_status', current_status)

        if name:
            if status == 'sign_in':
                vals['check_in_status'] = self._get_check_in_status(name)
            elif status == 'sign_out':
                vals['check_out_status'] = self._get_check_out_status(name)
        return vals

    def _get_check_in_status(self, check_in):
        check_in = self._ensure_datetime(check_in)
        if not check_in:
            return 'ok'  # or default status

        check_time = self._convert_to_local_time(check_in)

        shift_id = self.employee_id.new_shift_type
        if not shift_id:
            return 'ok'

        late_time_start = self.to_time(shift_id.check_in_la_start)
        late_time_end = self.to_time(shift_id.check_in_la_end)
        sla_start = self.to_time(shift_id.check_in_sla_start)
        sla_end = self.to_time(shift_id.check_in_sla_end)
        hda_start = self.to_time(shift_id.check_in_hda_start)
        hda_end = self.to_time(shift_id.check_in_hda_end)
        full_off_day = self.one_second_increment(hda_end) if hda_end else None

        if late_time_start and late_time_end and late_time_start <= check_time <= late_time_end:
            return 'la'
        elif sla_start and sla_end and sla_start <= check_time <= sla_end:
            return 'sla'
        elif hda_start and hda_end and hda_start <= check_time <= hda_end:
            return 'hda'
        elif full_off_day and full_off_day <= check_time <= time(21, 30, 59):
            return 'ab'
        else:
            return 'ok'

    def _get_check_out_status(self, check_out):
        check_out = self._ensure_datetime(check_out)
        if not check_out:
            return 'ok'

        check_time = self._convert_to_local_time(check_out)
        shift_id = self.employee_id.new_shift_type
        if not shift_id:
            return 'ok'

        sld_start = self.to_time(shift_id.check_out_sld_start)
        sld_end = self.to_time(shift_id.check_out_sld_end)
        hdd_start = self.to_time(shift_id.check_out_hdd_start)
        hdd_end = self.to_time(shift_id.check_out_hdd_end)
        full_day_off = self.to_time(shift_id.check_out_full_day_off)
        off_time = self.one_second_increment(sld_end) if sld_end else None

        if full_day_off and time(9, 0, 0) <= check_time <= full_day_off:
            return 'ab'
        elif hdd_start and hdd_end and hdd_start <= check_time <= hdd_end:
            return 'hdd'
        elif sld_start and sld_end and sld_start <= check_time <= sld_end:
            return 'sld'
        elif off_time and check_time >= off_time:
            return 'ok'
        else:
            return 'ab'

    def _ensure_datetime(self, value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return fields.Datetime.from_string(value)
        return None

    def _convert_to_local_time(self, dt):
        """Convert UTC datetime to user's timezone and return a time object."""
        user_tz = self.env.user.tz or 'UTC'
        if not dt:
            return datetime.now(timezone(user_tz)).time()
        if dt.tzinfo is None:
            dt = UTC.localize(dt)
        return dt.astimezone(timezone(user_tz)).time()

    def to_time(self, time_str):
        if isinstance(time_str, time):
            return time_str
        if not time_str:
            return None
        if isinstance(time_str, str):
            return datetime.strptime(time_str, "%H:%M:%S").time()
        return None

    def one_second_increment(self, check_in_time):
        if not check_in_time:
            check_in_time = time(0, 0, 0)
        return (datetime.combine(datetime.today(), check_in_time) + timedelta(seconds=1)).time()

    def one_second_decrement(self, check_time):
        if not check_time:
            check_time = time(0, 0, 0)
        return (datetime.combine(datetime.today(), check_time) - timedelta(seconds=1)).time()

    @api.onchange('check_in_status', 'check_out_status')
    def onchange_check_in_out(self):
        if self.check_in_status == 'sla' or self.check_out_status == 'sld':
            self.day_status = 'sla'
        elif self.check_in_status == 'hda' or self.check_out_status == 'hdd':
            self.day_status = 'hda'
#
class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    last_draft_attendance_id = fields.Many2one('hr.draft.attendance', compute='_compute_last_draft_attendance_id', search='_search_last_draft_attendance_id')
    attendance_devices = fields.One2many('employee.attendance.devices',  string='Attendance Devices')
#
    def _search_last_draft_attendance_id(self, operator, value):
        records = self.search([])
        if operator == 'in':
            records = records.filtered(lambda r: r.last_draft_attendance_id.id in value)
        elif operator == '=':
            records = records.filtered(lambda r: r.last_draft_attendance_id.id == value)
        else:
            raise NotImplementedError()
        return [('id', 'in', records.ids)]

    def _compute_last_draft_attendance_id(self):
        for employee in self:
            draft_atts = self.env['hr.draft.attendance'].search([('employee_id','=',employee.id)], order='name desc')
            employee.last_draft_attendance_id = draft_atts.ids

    @api.depends('last_draft_attendance_id.attendance_status', 'last_draft_attendance_id', 'last_attendance_id.check_in', 'last_attendance_id.check_out', 'last_attendance_id')
    def _compute_attendance_state(self):
        for employee in self:
            if employee.last_attendance_id and not self.env['hr.draft.attendance'].search([('moved_to','=',employee.last_attendance_id.id),
                                                                                           ('employee_id','=',employee.id)]):
                att = employee.last_attendance_id.sudo()
                employee.attendance_state = att and not att.check_out and 'checked_in' or 'checked_out'
            else:
                attendance_state = 'checked_out'
                if employee.last_draft_attendance_id and employee.last_draft_attendance_id.attendance_status == 'sign_in':
                    attendance_state = 'checked_in'
                employee.attendance_state = attendance_state

class EmployeeAttendanceDevices(models.Model):
    _name = 'employee.attendance.devices'
    _description = 'Employee Attendance Devices'

    name = fields.Many2one(comodel_name='hr.employee', string='Employee', readonly=True)
    attendance_id = fields.Char("Attendance ID", required=True)
    device_id = fields.Many2one(comodel_name='biomteric.device.info', string='Biometric Device', required=True, ondelete='restrict')

    @api.constrains('attendance_id', 'device_id', 'name')
    def _check_unique_constraint(self):
        for rec in self:
            record = self.search([('attendance_id', '=', rec.attendance_id), ('device_id', '=', rec.device_id.id)])
            if len(record) > 1:
                raise ValidationError('Employee with Id ('+ str(rec.attendance_id)+') exists on Device ('+ str(rec.device_id.name)+') !')
            record = self.search([('name', '=', rec.name.id), ('device_id', '=', rec.device_id.id)])
            if len(record) > 1:
                raise ValidationError('Configuration for Device ('+ str(rec.device_id.name)+') of Employee  ('+ str(rec.name.name)+') already exists!')
