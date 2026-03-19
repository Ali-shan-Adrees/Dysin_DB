from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from odoo.tools.populate import compute


class update_contract_form(models.Model):
    _inherit = 'hr.contract'

    # Payroll Fields
    total_salary = fields.Monetary('Total Salary', inverse='_inverse_total_salary', default=0.0, tracking=True)
    Basic_salary = fields.Monetary('Basic Salary', store=True, tracking=True, readonly=True)
    Allowance = fields.Monetary('Allowance', store=True, tracking=True, readonly=True)
    Allowance_fuel = fields.Monetary('Fuel Allowance', tracking=True)
    Allowance_mobile = fields.Monetary('Mobile Allowance', tracking=True)
    Allowance_car = fields.Monetary('Car Allowance', tracking=True)
    medical_allowance = fields.Monetary('Medical Allowance', store=True, tracking=True)
    food_allowance = fields.Monetary('Food Allowance', store=True, tracking=True)
    adhoc_allowance = fields.Monetary('Adhoc', store=True, tracking=True)
    other_allowance = fields.Monetary('Other Allowance', store=True, tracking=True)
    personal_allowance = fields.Monetary('Personal Allowance', store=True, tracking=True)
    meal_allowance = fields.Monetary('Meal Allowance', store=True, tracking=True)
    Allowance_house = fields.Monetary('House Rent Allowance', store=True, default=0.0, tracking=True)
    gazette_comp = fields.Monetary('Gazette Holiday Compensation', default=0.0, tracking=True)
    special_allowance = fields.Monetary('Special Allowance', default=0.0, tracking=True)
    arrears = fields.Monetary('Arrears', tracking=True)
    gross_finals = fields.Monetary('Gross', compute='_compute_gross_salary', default=0.0, tracking=True)

    cash_salary = fields.Monetary('Cash Salary', default=0.0, tracking=True)
    bank_salary = fields.Monetary('Bank Salary', default=0.0, tracking=True)
    Deduction_Tax = fields.Monetary('Tax', default=0.0, tracking=True)
    Deduction_EOBI = fields.Monetary('EOBI', default=0.0, tracking=True)
    Deduction_PF = fields.Monetary('PF', default=0.0, tracking=True)
    Deduction_Advance = fields.Monetary('Advance', default=0.0, tracking=True)
    Deduction_MobileBills = fields.Monetary('Mobile Bill Over Limit', default=0.0, tracking=True)
    deduction_lates = fields.Monetary('Late Deductions', default=0.0, tracking=True)
    deduction_absent = fields.Monetary('Absent Deductions', default=0.0, tracking=True)
    deduction_short_leave = fields.Monetary(string='Short Leave Deductions', default=0.0, tracking=True)
    deduction_half_leave = fields.Monetary(string='Half Leave Deductions', default=0.0, tracking=True)
    Deduction_Finals = fields.Monetary('Total Deduction', default=0.0, compute="_compute_deduction_final", store=True, tracking=True)
    Net_finals = fields.Monetary('Net Salary', compute='_compute_net_final', store=True, default=0.0, tracking=True)
    deduction_check = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Attendance Deduction', default='Yes', tracking=True)
    Deduction_Loan = fields.Monetary('Loan', tracking=True)


    def _inverse_total_salary(self):
        for rec in self:
            if rec.total_salary:
                rec.Basic_salary = rec.total_salary*0.5
                rec.Allowance = (rec.total_salary*0.5) - 450
                rec.adhoc_allowance = 450
            else:
                rec.Basic_salary = 0.0
                rec.Allowance = 0.0
    @api.depends('Basic_salary', 'Allowance', 'Allowance_fuel', 'Allowance_mobile', 'Allowance_car', 'medical_allowance', 'meal_allowance', 'Allowance_house', 'gazette_comp', 'special_allowance', 'other_allowance', 'adhoc_allowance', 'personal_allowance')
    def _compute_gross_salary(self):
        for record in self:
            basic_salary = record.Basic_salary or 0.0
            allowance = record.Allowance or 0.0
            fuel_alw = record.Allowance_fuel or 0.0
            mobile_alw = record.Allowance_mobile or 0.0
            car_alw = record.Allowance_car or 0.0
            medical_alw = record.medical_allowance or 0.0
            meal_alw = record.meal_allowance or 0.0
            house_rent_alw = record.Allowance_house or 0.0
            gazette_comp_alw = record.gazette_comp or 0.0
            special_alw = record.special_allowance or 0.0
            arrears_alw = record.arrears or 0.0
            other_alw = record.other_allowance or 0.0
            adhoc_alw = record.adhoc_allowance or 0.0
            food_alw = record.food_allowance or 0.0
            personal_alw = record.personal_allowance or 0.0
            total_gross = (
                    basic_salary +
                    allowance +
                    fuel_alw +
                    mobile_alw +
                    car_alw +
                    medical_alw +
                    meal_alw +
                    house_rent_alw +
                    gazette_comp_alw +
                    special_alw +
                    arrears_alw +
                    other_alw +
                    adhoc_alw +
                    food_alw +
                    personal_alw
            )
            record.gross_finals = total_gross

    @api.depends('Deduction_Tax', 'Deduction_EOBI', 'Deduction_PF', 'Deduction_Advance', 'Deduction_MobileBills', 'deduction_lates', 'deduction_absent', 'deduction_short_leave', 'deduction_half_leave', 'Deduction_Loan')
    def _compute_deduction_final(self):
        for res in self:
            tax_ded = res.Deduction_Tax or 0.0
            eobi_ded = res.Deduction_EOBI or 0.0
            pf_ded = res.Deduction_PF or 0.0    #Providant Fund
            advance_salary_ded = res.Deduction_Advance or 0.0
            mobile_bill_over_limit_ded = res.Deduction_MobileBills or 0.0
            lates_ded = res.deduction_lates or 0.0
            absent_ded = res.deduction_absent or 0.0
            short_leave_ded  = res.deduction_short_leave or 0.0
            half_day_leave_ded = res.deduction_half_leave or 0.0
            loan_ded = res.Deduction_Loan or 0.0

            total_deduction = (
                    tax_ded +
                    eobi_ded +
                    pf_ded +
                    advance_salary_ded +
                    mobile_bill_over_limit_ded +
                    lates_ded +
                    absent_ded +
                    short_leave_ded +
                    half_day_leave_ded +
                    loan_ded
            )
            print(total_deduction)

            res.Deduction_Finals = total_deduction







    def _compute_loan_amount(self):
        for rec in self:
            today_date = date.today()
            previous_date = today_date.replace(day=1) - relativedelta(months=1)
            rec.Deduction_Loan = 2


    @api.depends('gross_finals', 'Deduction_Finals')
    def _compute_net_final(self):
        for rec in self:
            gross_salary = rec.gross_finals or 0.0
            total_ded = rec.Deduction_Finals or 0.0
            rec.Net_finals = gross_salary - total_ded



    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.name = self.employee_id.name + "'s Contract"
            self.job_id = self.employee_id.job_id
            self.department_id = self.employee_id.department_id
            self.resource_calendar_id = self.employee_id.resource_calendar_id
            self.company_id = self.employee_id.company_id
            self.date_start = self.employee_id.joining_date
