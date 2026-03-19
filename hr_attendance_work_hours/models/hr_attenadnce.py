# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta, time
from pytz import timezone
#
# class ResourceCalendarAttendance(models.Model):
#     _inherit = "resource.calendar.attendance"
#
#     grace_period = fields.Float('Grace Period')
#
#
#
class HRAttendance(models.Model):
    _inherit = 'hr.attendance'
#
    in_work_hours = fields.Float('In Work Hours', compute='_compute_attendance_work_hours')
    out_work_hours = fields.Float('Out Work Hours', compute='_compute_attendance_work_hours')
    late_minutes = fields.Float('Late Minutes', compute='_compute_late_early_hours')
    late_minutes_gp = fields.Float('Late Minutes - Grace Period', compute='_compute_late_early_hours')
    early_check_out = fields.Float('Early Checkout', compute='_compute_late_early_hours')
    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Time', compute='_compute_resource_calendar_id', store=True)
    check_in_status = fields.Selection([
        ('la', 'LA'),('sla', 'SLA'),('hda', 'HDA'),('od', 'OD'),('ab', 'AB'),('ok', 'OK')],
        string="Arrival Status", readonly=True,
        help='1. LA=Late Arrival, 2. SLA=Short Leave Arrival, 3. HDA=Half Day Arrival, 4.AB=Absent')
    check_out_status = fields.Selection([
        ('ed', 'ED'), ('sld', 'SLD'), ('hdd', 'HDD'), ('od', 'OD'),('ab', 'AB'), ('ok', 'OK')],
        string="Departure Status",
        readonly=True,
        help='1. ED=Early Departure, 2. SLD=Short Leave departure, 3. HDD=Half Day Departure, 4.OD=Outdoor Duty, 5. AB=Absent, 6. OK=Full Day Present In Office')
    day_status = fields.Selection([('p', 'P'),('a', 'A')], string='Day Status', help='1. P= Present, 2. A= Absent', readonly=True)

#
    @api.depends('employee_id')
    def _compute_resource_calendar_id(self):
        for rec in self:
            contracts = rec.employee_id.contract_ids.filtered(lambda x: x.state in ['open'])
            if contracts:
                rec.resource_calendar_id = contracts[0].resource_calendar_id
            else:
                rec.resource_calendar_id = rec.employee_id.resource_calendar_id


    @api.depends('check_in','check_out','resource_calendar_id')
    def _compute_attendance_work_hours(self):
        for rec in self:
            if rec.resource_calendar_id and rec.check_in and rec.check_out:
                hours = rec.employee_id._get_work_days_data_batch(rec.check_in, rec.check_out,compute_leaves=False, calendar=rec.resource_calendar_id)
                rec.in_work_hours = hours[rec.employee_id.id]['hours']
                rec.out_work_hours = rec.worked_hours-rec.in_work_hours if rec.worked_hours-rec.in_work_hours >= 0 else 0

                calendar = rec.resource_calendar_id
                tz = rec.employee_id.tz or rec.resource_calendar_id.tz
                user_timezone = timezone(tz)
                local_timezone = timezone('UTC')

                in_local_date = local_timezone.localize(rec.check_in).astimezone(timezone(tz))
                out_local_date = local_timezone.localize(rec.check_out).astimezone(timezone(tz))
                leaves = rec.employee_id._get_leave_days_data_batch(in_local_date,out_local_date,calendar=calendar, domain = [('time_type', 'in', ['leave', 'other'])])
                if leaves and leaves.get(rec.employee_id.id):
                    rec.in_work_hours = hours[rec.employee_id.id]['hours'] - leaves.get(rec.employee_id.id).get('hours')
                    rec.out_work_hours = rec.worked_hours-rec.in_work_hours + leaves.get(rec.employee_id.id).get('hours') if rec.worked_hours-rec.in_work_hours + leaves.get(rec.employee_id.id).get('hours') >= 0 else 0

            else:
                rec.in_work_hours = 0
                rec.out_work_hours = 0

    def convert_time_to_float(self, time):
        return time.hour + time.minute / 60

    # @api.depends('check_in','check_out','resource_calendar_id')
    # def _compute_late_early_hours(self):
    #     for rec in self:
    #         calendar = rec.resource_calendar_id
    #         if calendar and rec.check_in and rec.check_out:
    #             tz = rec.employee_id.tz or rec.resource_calendar_id.tz
    #             user_timezone = timezone(tz)
    #             local_timezone = timezone('UTC')
    #             local_date = local_timezone.localize(rec.check_in).astimezone(timezone(tz))
    #             number_of_day = str(local_date.weekday())
    #             days_from_hours = calendar.attendance_ids.filtered(lambda x:x.dayofweek == number_of_day)
    #             hours_converted = self.convert_time_to_float(local_date)
    #             late_mins = grace_period = 0
    #             hours_converted = hours_converted
    #             day_start = rec.check_in.strftime('%Y-%m-%d 00:00:00.%f')
    #             day_end = rec.check_in.strftime('%Y-%m-%d 23:59:59.%f')
    #             for day in days_from_hours:
    #                 in_hour = int(day.hour_from)
    #                 out_hour = int(day.hour_to)
    #
    #                 in_min = int((in_hour-int(in_hour)) * 60)
    #                 out_min = int((out_hour-int(out_hour)) * 60)
    #                 out_hour1 = int(days_from_hours[0].hour_to)
    #                 out_min1 = int((days_from_hours[0].hour_to-int(days_from_hours[0].hour_to)) * 60)
    #                 check_out = user_timezone.localize(rec.check_out.replace(hour=out_hour, minute=out_min)).astimezone(timezone('UTC'))
    #                 check_out1 = user_timezone.localize(rec.check_out.replace(hour=out_hour1, minute=out_min1)).astimezone(timezone('UTC'))
    #                 work_day_start = user_timezone.localize(rec.check_in.replace(hour=in_hour, minute=in_min)).astimezone(timezone('UTC')) - timedelta(seconds=2)
    #
    #                 prev_shift = self.search([('check_in','>',day_start),
    #                                           ('check_in','<',work_day_start),
    #                                           ('check_out','>=',work_day_start),
    #                                           ('employee_id','=',rec.employee_id.id)])
    #                 matched_recs = self.search([('check_in','>',work_day_start),
    #                                             ('check_in','<',check_out),
    #                                             ('check_out','<=',day_end),
    #                                             ('employee_id','=',rec.employee_id.id)], order='check_in asc')
    #                 matched_recs1 = self.search([('check_in','>',check_out1),
    #                                              ('check_out','<=',day_end),
    #                                              ('employee_id','=',rec.employee_id.id)], order='check_in asc')
    #                 leaves_work_day_start = user_timezone.localize(rec.check_in.replace(hour=in_hour, minute=in_min))
    #                 leaves = rec.employee_id._get_leave_days_data_batch(leaves_work_day_start,local_date,calendar=calendar, domain = [('time_type', 'in', ['leave', 'other'])])
    #                 if day.hour_from < hours_converted and day.hour_to > hours_converted and matched_recs and rec.id == matched_recs.ids[0]:
    #                     late_mins = hours_converted-day.hour_from
    #                     grace_period = day.grace_period
    #                     if prev_shift:
    #                         late_mins = 0
    #                 elif day.hour_from < hours_converted and day.hour_to > hours_converted and matched_recs1 and rec.id == matched_recs1.ids[0]:
    #                     late_mins = hours_converted-day.hour_from
    #                     grace_period = day.grace_period
    #                     if prev_shift:
    #                         late_mins = 0
    #                 leave = leaves.get(rec.employee_id.id)
    #                 if leave.get('hours', 0)  > 0 and late_mins >0:
    #                     late_mins -= round(leave.get('hours'),2)
    #             rec.late_minutes = late_mins > 0 and late_mins or 0
    #             rec.late_minutes_gp = rec.late_minutes if  round(rec.late_minutes,2) >= round(grace_period,2) else 0
    #
    #
    #             check_in =  rec.check_in
    #             local_date_to = local_timezone.localize(rec.check_out).astimezone(timezone(self.env.user.tz))
    #             local_date_to = local_date_to.replace(second=0, microsecond=0)
    #             hours_to_converted = self.convert_time_to_float(local_date_to)
    #             hours_to_converted = hours_to_converted
    #             not_ordered_days_to_hours = calendar.attendance_ids.filtered(lambda x:x.dayofweek == number_of_day)
    #             days_to_hours = self.env['resource.calendar.attendance'].search([('id','in',not_ordered_days_to_hours.ids)], order='hour_from')
    #             early_checkout = 0
    #             flag = True
    #             for day in days_to_hours:
    #                 out_hour = day.hour_to
    #                 out_min = int((out_hour-int(out_hour)) * 60)
    #                 check_out = user_timezone.localize(rec.check_out.replace(hour=out_hour1, minute=out_min)).astimezone(timezone('UTC'))
    #                 att_after_checkout = self.search([('check_in','>',check_in),
    #                                                   ('check_in','<',check_out),
    #                                                   ('employee_id','=',rec.employee_id.id)])
    #                 if not att_after_checkout:
    #                     matched_early_recs = self.search([('check_in','>',day_start),
    #                                                       ('check_out','<',check_out),
    #                                                       ('employee_id','=',rec.employee_id.id)], order='check_in asc')
    #                     work_day_end =user_timezone.localize(rec.check_out.replace(hour=int(out_hour), minute=out_min))
    #                     matched_rec = self.search([('check_in','>',day_start),
    #                                                ('check_in','<=',work_day_end),
    #                                                ('check_out','<=',work_day_end),
    #                                                ('employee_id','=',rec.employee_id.id)], order='check_in asc')
    #                     shift_records = self.search([('check_in','>',day_start),
    #                                                ('check_in','<=',work_day_end),
    #                                                ('check_out','<=',check_out),
    #                                                ('employee_id','=',rec.employee_id.id)], order='check_in desc')
    #                     leaves = rec.employee_id._get_leave_days_data_batch(local_date_to,work_day_end,calendar=calendar, domain = [('time_type', 'in', ['leave', 'other'])])
    #                     leave = leaves.get(rec.employee_id.id)
    #                     if hours_to_converted < day.hour_to and hours_to_converted > day.hour_from and ((matched_rec and rec.id == matched_rec.ids[-1]) or shift_records and rec.id == shift_records.ids[0]):
    #                         early_checkout = day.hour_to-hours_to_converted
    #                         if leave.get('hours', False) and leave.get('hours') > 0:
    #                             early_checkout = day.hour_to-hours_to_converted-round(leave.get('hours'),2) if (day.hour_to-hours_to_converted-leave.get('hours')) > 0 else 0
    #                     elif hours_to_converted < day.hour_to and hours_to_converted >= day.hour_from and ((matched_rec and rec.id == matched_rec.ids[-1]) or shift_records and rec.id == shift_records.ids[0]):
    #                         early_checkout = day.hour_to-hours_to_converted
    #                         flag = False
    #                         if leave.get('hours', False) and leave.get('hours') > 0:
    #                             early_checkout = day.hour_to-hours_to_converted-round(leave.get('hours'),2) if (day.hour_to-hours_to_converted-leave.get('hours')) > 0 else 0
    #                     elif hours_to_converted < day.hour_to and hours_to_converted > day.hour_from and matched_early_recs and rec.id == matched_early_recs.ids[-1] and not flag:
    #                         early_checkout = day.hour_to-hours_to_converted
    #                         if leave.get('hours', False) and leave.get('hours') > 0:
    #                             early_checkout = day.hour_to-hours_to_converted-round(leave.get('hours'),2) if (day.hour_to-hours_to_converted-leave.get('hours')) > 0 else 0
    #             rec.early_check_out = early_checkout if early_checkout > 0 else 0
    #
    #
    #         else:
    #             rec.early_check_out = 0
    #             rec.late_minutes = 0
    #             rec.late_minutes_gp = 0
    #
    # @api.model
    # def create(self, vals):
    #     employee = None
    #     if vals.get('employee_id'):
    #         employee = self.env['hr.employee'].browse(vals['employee_id'])
    #
    #     if employee and vals.get('check_in'):
    #         vals['check_in_status'] = self._get_check_in_status(vals['check_in'], employee)
    #
    #     if employee and vals.get('check_out'):
    #         vals['check_out_status'] = self._get_check_out_status(vals['check_out'], employee)
    #
    #     return super().create(vals)
    #
    # def write(self, vals):
    #     for rec in self:
    #         employee = self.env['hr.employee'].browse(
    #             vals.get('employee_id', rec.employee_id.id)
    #         )
    #
    #         if vals.get('check_in'):
    #             vals['check_in_status'] = rec._get_check_in_status(vals['check_in'], employee)
    #
    #         if vals.get('check_out'):
    #             vals['check_out_status'] = rec._get_check_out_status(vals['check_out'], employee)
    #
    #     return super().write(vals)
    #
    #
    # def _get_check_in_status(self, check_in, employee):
    #     # Convert to datetime if it's a string
    #     if isinstance(check_in, str):
    #         check_in = fields.Datetime.from_string(check_in)
    #
    #         # Get user timezone or default to UTC
    #     user_tz = self.env.user.tz or 'UTC'
    #     local_tz = timezone(user_tz)
    #     # Convert UTC datetime to local time
    #     local_dt = check_in.astimezone(local_tz)
    #     check_time = local_dt.time()
    #     shift_id = employee.new_shift_type
    #
    #     print('Shift Id', shift_id.check_in_la_start)
    #     print('TEST', type(shift_id.check_in_la_start))
    #
    #     def to_time(val):
    #         return datetime.strptime(val, "%H:%M:%S").time() if val else None
    #
    #     check_in_la_start = to_time(shift_id.check_in_la_start)
    #     check_in_la_end = to_time(shift_id.check_in_la_end)
    #
    #     check_in_sla_start = to_time(shift_id.check_in_sla_start)
    #     check_in_sla_end = to_time(shift_id.check_in_sla_end)
    #
    #     check_in_hda_start = to_time(shift_id.check_in_hda_start)
    #     check_in_hda_end = to_time(shift_id.check_in_hda_end)
    #
    #     # Now compare using local business hour ranges
    #     if check_in_la_start <= check_time <= check_in_la_end:
    #         return 'la'
    #     elif check_in_sla_start <= check_time <= check_in_sla_end:
    #         return 'sla'
    #     elif check_in_hda_start <= check_time <= check_in_hda_end:
    #         return 'hda'
    #     else:
    #         return 'ok'
    #
    # def _get_check_out_status(self, check_out, employee):
    #     # Convert to datetime if it's a string
    #     if isinstance(check_out, str):
    #         check_out = fields.Datetime.from_string(check_out)
    #
    #         # Get user timezone or default to UTC
    #     user_tz = self.env.user.tz or 'UTC'
    #     local_tz = timezone(user_tz)
    #     # Convert UTC datetime to local time
    #     local_dt = check_out.astimezone(local_tz)
    #     check_out_time = local_dt.time()
    #     shift_id = employee.new_shift_type
    #
    #     def to_time(val):
    #         return datetime.strptime(val, "%H:%M:%S").time() if val else None
    #
    #
    #     check_out_ed_start = to_time(shift_id.check_out_ed_start)
    #     check_out_ed_end = to_time(shift_id.check_out_ed_end)
    #     # check_out_ed_start = datetime.strptime(check_out_ed_start, "%H:%M:%S").time()
    #     # check_out_ed_end = datetime.strptime(check_out_ed_end, "%H:%M:%S").time()
    #
    #     check_out_sld_start = to_time(shift_id.check_out_sld_start)
    #     check_out_sld_end = to_time(shift_id.check_out_sld_end)
    #     # check_out_sld_start = datetime.strptime(check_out_sld_start, "%H:%M:%S").time()
    #     # check_out_sld_end = datetime.strptime(check_out_sld_end, "%H:%M:%S").time()
    #
    #     check_out_hdd_start = to_time(shift_id.check_out_hdd_start)
    #     check_out_hdd_end = to_time(shift_id.check_out_hdd_end)
    #     # check_out_hdd_start = datetime.strptime(check_out_hdd_start, "%H:%M:%S").time()
    #     # check_out_hdd_end = datetime.strptime(check_out_hdd_end, "%H:%M:%S").time()
    #
    #     # Now compare using local business hour ranges
    #     if check_out_ed_start <= check_out_time <= check_out_ed_end:
    #         return 'ed'
    #     elif check_out_sld_start <= check_out_time <= check_out_sld_end:
    #         return 'sld'
    #     elif check_out_hdd_start <= check_out_time <= check_out_hdd_end:
    #         return 'hdd'
    #     else:
    #         return 'ok'