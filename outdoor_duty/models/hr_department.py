from odoo import models, fields


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    coordinator_id = fields.Many2one('res.users', string="Department Coordinator")