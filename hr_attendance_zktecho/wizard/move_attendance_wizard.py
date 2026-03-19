# -*- coding: utf-8 -*-

import operator
import logging
from odoo import api, fields, models, _
from odoo.exceptions import except_orm, UserError

_logger = logging.getLogger('move_attendance')

class move_attendance_wizard(models.TransientModel):
    _name = "move.draft.attendance.wizard"
    _description = 'Move Draft Attendance Wizard'
    
    date1 = fields.Datetime('From', required=True)
    date2 = fields.Datetime('To', required=True)
    employee_ids = fields.Many2many('hr.employee', 'move_att_employee_rel', 'employee_id', 'wiz_id')
    
    def move_confirm(self):
        HrAttendance = self.env['hr.attendance']
        DraftAttendance = self.env['hr.draft.attendance']

        for emp in self.employee_ids:
            # Get draft attendances in range for employee
            drafts = DraftAttendance.search([
                ('employee_id', '=', emp.id),
                ('name', '>=', self.date1),
                ('name', '<=', self.date2),
            ], order="name asc")

            if not drafts:
                continue

            # Group by date
            date_wise = {}
            for draft in drafts:
                if draft.date not in date_wise:
                    date_wise[draft.date] = []
                date_wise[draft.date].append(draft)

            # Process each day
            for day, records in date_wise.items():
                sign_ins = [r.name for r in records if r.attendance_status == 'sign_in']
                sign_outs = [r.name for r in records if r.attendance_status == 'sign_out']

                if not sign_ins or not sign_outs:
                    continue  # Skip if no proper in/out

                sign_in_time = min(sign_ins)
                sign_out_time = max(sign_outs)

                if sign_in_time >= sign_out_time:
                    continue  # Invalid case

                # Avoid duplicate creation
                exists = HrAttendance.search([
                    ('employee_id', '=', emp.id),
                    ('check_in', '=', sign_in_time),
                    ('check_out', '=', sign_out_time)
                ], limit=1)

                if not exists:
                    device = self.env['employee.attendance.devices'].search([
                        ('name', '=', emp.id)
                    ], limit=1)

                    HrAttendance.create({
                        'employee_id': emp.id,
                        'check_in': sign_in_time,
                        'check_out': sign_out_time,
                        'device_id': device.device_id.id if device else False,
                    })
                for rec in records:
                    print('TEST Moved')
                    rec.moved = True


