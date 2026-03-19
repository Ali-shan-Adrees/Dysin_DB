# -*- coding: utf-8 -*-

from odoo import models, fields, api


class sl_hr_department(models.Model):
    _inherit = 'hr.department'
    _description = 'HR Department'

    department_admin_id = fields.Many2one('res.users',"Department Admin")
    regional_admin_ids = fields.Many2many('res.users', string="Hr/Admin Att Allow")

class ResUsers(models.Model):
    _inherit = 'res.users'
    allowed_department_ids = fields.Many2many(
        'hr.department',
        'res_users_department_rel',
        'user_id',
        'department_id',
        string="Allowed Departments"
    )
