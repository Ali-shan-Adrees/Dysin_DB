# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import re
from odoo.exceptions import ValidationError, AccessError
from datetime import date
from dateutil.relativedelta import relativedelta


class EmployeeGradeProfile(models.Model):
    _inherit = 'hr.employee'


    employee_code = fields.Char(
        string="Employee Code",
        copy=False,
        tracking=True
    )
    private_phone_no = fields.Char("Private Phone", tracking=True)
    private_email_no = fields.Char("Private Email", tracking=True)
    job_levels_id = fields.Many2one('job.levels',string="Job Level", tracking=True)

    # current_address = fields.Char(string="Current Address", required=True)
    city = fields.Char(string="City")
    # f_name = fields.Char(string="Father Name", required=True)
    joining_date = fields.Date(string="Date Of Joining", required=True)
    # doj = fields.Date(string="Date Of Joining", required=True)
    confirmation_date = fields.Date(string='Confirmation Date', tracking=True)
    # employee_status = fields.Selection([('1', 'Permanent'),('2', 'Contractual'),('3', 'Probation Period'),('4', 'TEMPORARY'),
    #     ('5', 'INTERNEE')],tracking=True, required=True, string='Job Status')
    job_status = fields.Selection([
        ('PERMANENT', 'PERMANENT'),
        ('PROBATION', 'PROBATION'),
        ('CONTRACT', 'CONTRACT'),
        ('INTERNEE', 'INTERNEE'),
    ], string='Job Status',required=True, tracking=True)
    education_certificate = fields.Selection([
        ('phd', 'PhD'),
        ('master', 'Master'),
        ('graduate', 'Graduate'),
        ('hssc', 'HSSC - (Intermediate)'),
        ('ssc', 'SSC - (Metric Or O Level)'),
    ], string='Degree', required=True, tracking=True)
    new_shift_type = fields.Many2one('new.shift.employee', string='Primary Shift', tracking=True)
    rest_days = fields.Many2many('days.week', string="Rest Days", tracking=True,
                                 default=lambda self: self.env['days.week'].search([('name', '=', 'SUNDAY')]))
    employee_account_title = fields.Char('Account Title', tracking=True)
    employee_account_number = fields.Char('Account Number', tracking=True)
    employee_bank_name = fields.Many2one("res.bank", "Bank Name")
    employee_address = fields.Char(string="Employee Address", tracking=True, required=True)
    employee_father = fields.Char(string="Father Name", tracking=True, required=True)
    employee_cnic_issue_date = fields.Date(string="CNIC Issue Date", tracking=True)
    employee_NTN_no = fields.Char(string="NTN No", tracking=True)
    education_detail_report = fields.One2many('education.detail', 'employee_id')
    date_of_leaving = fields.Date(string="Leaving Date", required=False, tracking=True)
    km_home_work = fields.Integer(string="Km Home-Work", required=False, tracking=True)
    blood_group = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ], string='Blood Group', tracking=True)
    child_name_1 = fields.Char(string="Name", tracking=True)
    child_DOB_1 = fields.Date(string="DOB", tracking=True)
    child_REL_1 = fields.Selection(
        [('FATHER', 'FATHER'), ('MOTHER', 'MOTHER'), ('WIFE', 'WIFE'), ('SON', 'SON'), ('DAUGHTER', 'DAUGHTER')],
        string="Relation", tracking=True)
    child_name_2 = fields.Char(string="Name", tracking=True)
    child_DOB_2 = fields.Date(string="DOB", tracking=True)
    child_REL_2 = fields.Selection(
        [('FATHER', 'FATHER'), ('MOTHER', 'MOTHER'), ('WIFE', 'WIFE'), ('SON', 'SON'), ('DAUGHTER', 'DAUGHTER')],
        string="Relation", tracking=True)
    child_name_3 = fields.Char(string="Name", tracking=True)
    child_DOB_3 = fields.Date(string="DOB", tracking=True)
    child_REL_3 = fields.Selection(
        [('FATHER', 'FATHER'), ('MOTHER', 'MOTHER'), ('WIFE', 'WIFE'), ('SON', 'SON'), ('DAUGHTER', 'DAUGHTER')],
        string="Relation", tracking=True)
    child_name_4 = fields.Char(string="Name", tracking=True)
    child_DOB_4 = fields.Date(string="DOB", tracking=True)
    child_REL_4 = fields.Selection(
        [('FATHER', 'FATHER'), ('MOTHER', 'MOTHER'), ('WIFE', 'WIFE'), ('SON', 'SON'), ('DAUGHTER', 'DAUGHTER')],
        string="Relation", tracking=True)
    child_name_5 = fields.Char(string="Name", tracking=True)
    child_DOB_5 = fields.Date(string="DOB", tracking=True)
    child_REL_5 = fields.Selection(
        [('FATHER', 'FATHER'), ('MOTHER', 'MOTHER'), ('WIFE', 'WIFE'), ('SON', 'SON'), ('DAUGHTER', 'DAUGHTER')],
        string="Relation", tracking=True)
    child_name_6 = fields.Char(string="Name", tracking=True)
    child_DOB_6 = fields.Date(string="DOB", tracking=True)
    child_REL_6 = fields.Selection(
        [('FATHER', 'FATHER'), ('MOTHER', 'MOTHER'), ('WIFE', 'WIFE'), ('SON', 'SON'), ('DAUGHTER', 'DAUGHTER')],
        string="Relation", tracking=True)
    child_name_7 = fields.Char(string="Name", tracking=True)
    child_DOB_7 = fields.Date(string="DOB", tracking=True)
    child_REL_7 = fields.Selection(
        [('FATHER', 'FATHER'), ('MOTHER', 'MOTHER'), ('WIFE', 'WIFE'), ('SON', 'SON'), ('DAUGHTER', 'DAUGHTER')],
        string="Relation", tracking=True)
    child_name_8 = fields.Char(string="Name", tracking=True)
    child_DOB_8 = fields.Date(string="DOB", tracking=True)
    child_REL_8 = fields.Selection(
        [('FATHER', 'FATHER'), ('MOTHER', 'MOTHER'), ('WIFE', 'WIFE'), ('SON', 'SON'), ('DAUGHTER', 'DAUGHTER')],
        string="Relation", tracking=True)
    child_name_9 = fields.Char(string="Name", tracking=True)
    child_DOB_9 = fields.Date(string="DOB", tracking=True)
    child_REL_9 = fields.Selection(
        [('FATHER', 'FATHER'), ('MOTHER', 'MOTHER'), ('WIFE', 'WIFE'), ('SON', 'SON'), ('DAUGHTER', 'DAUGHTER')],
        string="Relation", tracking=True)
    child_name_10 = fields.Char(string="Name", tracking=True)
    child_DOB_10 = fields.Date(string="DOB", tracking=True)
    child_REL_10 = fields.Selection(
        [('FATHER', 'FATHER'), ('MOTHER', 'MOTHER'), ('WIFE', 'WIFE'), ('SON', 'SON'), ('DAUGHTER', 'DAUGHTER')],
        string="Relation", tracking=True)
    child_name_11 = fields.Char(string="Name", tracking=True)
    child_DOB_11 = fields.Date(string="DOB", tracking=True)
    child_REL_11 = fields.Selection(
        [('FATHER', 'FATHER'), ('MOTHER', 'MOTHER'), ('WIFE', 'WIFE'), ('SON', 'SON'), ('DAUGHTER', 'DAUGHTER')],
        string="Relation", tracking=True)
    child_name_12 = fields.Char(string="Name", tracking=True)
    child_DOB_12 = fields.Date(string="DOB", tracking=True)
    child_REL_12 = fields.Selection(
        [('FATHER', 'FATHER'), ('MOTHER', 'MOTHER'), ('WIFE', 'WIFE'), ('SON', 'SON'), ('DAUGHTER', 'DAUGHTER')],
        string="Relation", tracking=True)
    probation_check = fields.Boolean()
    probation_check_5_months = fields.Boolean()
    insurance_number = fields.Char(string="Insurance Number", tracking=True)
    valid_till = fields.Date(string='Insurance Valid Till', tracking=True)
    insurance_plan = fields.Selection([('PlanA', 'Plan A'),
                                       ('PlanB', 'Plan B'),
                                       ('PlanC', 'Plan C'),
                                       ('PlanD', 'Plan D')], string='Insurance Plan', tracking=True)

    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True,
                                       relation="res.currency", tracking=True)
    insurance_amount = fields.Monetary(string='Insurance Amount', currency_field='company_currency', tracking=True)

    eobi_employee_card_no = fields.Char(string="EOBI Card No", tracking=True)
    eobi_employee_contribution = fields.Monetary(string='Employee Contribution', currency_field='company_currency',
                                                 tracking=True)
    eobi_employer_contribution = fields.Monetary(string='Employer Contribution', currency_field='company_currency',
                                                 tracking=True)

    petrol_liter = fields.Integer('Petrol (Liter)', tracking=True)
    mobile_package = fields.Char('Mobile Package', tracking=True)
    car_allocation = fields.Char('Car Allocation', tracking=True)
    system_required = fields.Selection([('Laptop', 'Laptop'), ('Desktop', 'Desktop'), ('None', 'None')],
                                       string='System', tracking=True)

    # Expense Account Linked with Employee
    advance_against_salary_acc_id = fields.Many2one('account.account', 'Advance Against Salary')
    # domain = "[('acc_level', '=', '5')]"
    employee_loan_acc_id = fields.Many2one('account.account', 'Loan To Employee')
    # Create Field For loan
    is_loan_applicable = fields.Boolean('Is Loan Applicable?')
    loan_amount = fields.Float('Loan Amount')
    installments = fields.Integer('No of Installments')
    installment_amount = fields.Float('Installment Amount', compute='compute_installment_amount')
    installment_start_date = fields.Date('Installment Start Date')
    installment_end_date = fields.Date('Installment End Date', compute='compute_end_date')
    is_birthday_this_month = fields.Boolean(
        compute='_compute_birthday_this_month',
        store=True
    )


    @api.model
    def create(self, vals):
        if vals.get('user_id'):
            user = self.env['res.users'].browse(vals['user_id'])
            vals.update(self._sync_user(user))
            vals['name'] = vals.get('name', user.name)

        temp = self.env['res.partner'].create({
            'name': vals.get('name'),
            'mobile': vals.get('mobile_phone'),
            'phone': vals.get('work_phone'),
            'email': vals.get('work_email'),
            'customer_vendor_type': "4",
        })
        vals["address_home_id"] = temp.id
        employee = super(EmployeeGradeProfile, self).create(vals)
        # url = '/web#%s' % url_encode({
        #     'action': self.env.ref('hr.plan_wizard_action').id,
        #     'active_id': employee.id,
        #     'active_model': 'hr.employee',
        #     'menu_id': self.env.ref('hr.menu_hr_root').id,
        # })
        # employee._message_log(
        #     body=_('<b>Congratulations!</b> May I recommend you to setup an <a href="%s">onboarding plan?</a>') % (url))
        # if employee.department_id:
        #     self.env['mail.channel'].sudo().search(
        #         [('subscription_department_ids', 'in', employee.department_id.id)])._subscribe_users()
        return employee

    @api.onchange('children')
    def _onchange_children_check(self):
        if self.children > 12 or self.children < 0:
            raise ValidationError('Please enter dependants between 0-12')


    @api.constrains('identification_id')
    def _check_identification_id(self):
        for record in self:
            if record.identification_id:
                if not re.match(r'^\d{5}-\d{7}-\d{1}$', record.identification_id):
                    raise ValidationError("CNIC must be in the format 12345-1234567-1.")

                # Check for uniqueness
                existing_employee_count = self.search_count([('identification_id', '=', record.identification_id)])
                if existing_employee_count > 1:
                    raise ValidationError("This CNIC number is already registered.")


    # Compute function for loan computation
    def compute_installment_amount(self):
        for rec in self:
            if rec.loan_amount > 0 and rec.installments > 0:
                rec.installment_amount = rec.loan_amount / rec.installments
            else:
                rec.installment_amount = 0
    # Compute end date for loan installment
    def compute_end_date(self):
        for rec in self:
            if rec.installment_start_date:
                rec.installment_end_date = rec.installment_start_date + relativedelta(months=rec.installments)
            else:
                rec.installment_end_date = None

    def _compute_birthday_this_month(self):
        current_month = date.today().month
        for emp in self:
            emp.is_birthday_this_month = bool(
                emp.birthday and emp.birthday.month == current_month
            )
