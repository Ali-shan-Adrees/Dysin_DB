# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    previous_od_days = fields.Integer(string='How many days would you like to add to the old outdoor duty? ', default=7, config_parameter = 'outdoor_duty.previous_od_days')
    ta_audit_mandatory = fields.Boolean(string='Is Pre Audit is mandatory ? ', default=False, config_parameter = 'outdoor_duty.ta_audit_mandatory')
