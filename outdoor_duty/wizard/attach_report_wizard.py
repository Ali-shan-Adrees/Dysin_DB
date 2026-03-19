from  odoo import api,models, fields

class attachReportWizards(models.TransientModel):
    _name = 'attach.report.wizards'
    disccription = fields.Text(string='Visit details', copy=False)
    partner_id = fields.Many2one('res.partner', string='Sales Person')
    visit_type = fields.Selection([
        ('1', 'Select Visit Type'),
        ('2', 'New Query'),
        ('3', 'Follow up'),
        ('4', 'Lead'),
        ('5', 'Qualified Lead'),
        ('8', 'Other'),
    ], string='Visit Type', default='', required=True)
    visit_team = fields.Selection([
        ('1', 'Sales Team'),
        ('2', 'CSD Team'),
        ('3', 'Administration'),

    ], string='Department Type', default='2')
    visit_date = fields.Datetime(string='Visit Date')
    visit_end_date = fields.Datetime(string='Visit End Date')
    sales_team = fields.Many2one('crm.team', string='Sale Team')
    od_ref = fields.Many2one('outdoor.duty', string='OD Reference')
    ta_ref = fields.Many2one('travel.authority', string='T.A Reference')
    total_visit_hour = fields.Integer(string='Visit Hour')
    lead_id = fields.Many2one('crm.lead', string="Lead/Opportunity")

    @api.model
    def default_get(self, fields):
        """
        Populate wizard fields with default values from the active record.
        """
        defaults = super(attachReportWizards, self).default_get(fields)
        active_id = self.env.context.get('active_id')  # Get the active record ID
        if active_id:
            outdoor_id = self.env['outdoor.duty'].browse(active_id)  # Get the active Lead/Opportunity
            defaults.update({
                'partner_id': outdoor_id.user_id.partner_id.id,
                # 'sales_team': outdoor_id.sales_team.id,
                'od_ref': outdoor_id.id,
                'visit_date': outdoor_id.travelling_date,  # Default to current date
                'visit_end_date': outdoor_id.expected_arrival_date,  # Default to current date

            })
        return defaults


    def submit_visit_report(self):
        # print("Yeah Clicked")
        self.env['outdoor.duty'].browse(self._context.get('active_ids')).update({'visit_details':self.disccription,
                                                                                 'report_status':True})
        for record in self:
            # Create a new visit report line in the associated Lead/Opportunity
            if record.lead_id:
                record.lead_id.write({
                    'visit_line_ids': [(0, 0, {
                        'partner_id': record.partner_id.id,
                        'sales_team': record.sales_team.id,
                        'visit_date': record.visit_date,
                        'visit_end_date': record.visit_end_date,
                        'od_ref': record.od_ref.id,
                        'ta_ref': record.ta_ref.id,
                        'description': record.disccription,
                        'total_visit_hour': record.total_visit_hour,
                    })]
                })
            if record.od_ref:
                record.od_ref.write({
                    'outdoor_duty_ids': [(0, 0, {
                        'partner_id': record.partner_id.id,
                        'sales_team': record.sales_team.id,
                        'visit_type': record.visit_type,
                        'lead_id': record.lead_id.id,
                        'visit_date': record.visit_date,
                        'visit_end_date': record.visit_end_date,
                        'outdoor_duty_id': record.od_ref.id,
                        'description': record.disccription,
                    })]
                })
        return True
