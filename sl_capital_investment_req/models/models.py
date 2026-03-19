from importlib.metadata import requires

from odoo import models, fields, api
from odoo.exceptions import UserError
class CapitalInvestment(models.Model):
	_name = 'sl.capital.investment'
	_description = 'Capital Investment Request'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	user_id = fields.Many2one('res.users', string="Owner", default=lambda self: self.env.user)
	department_admin_id = fields.Many2one(
		'res.users',
		string="Department Head",
		related='user_id.employee_id.department_id.department_admin_id',
		store=True,
		readonly=True
	)
	date = fields.Date(string="Date", default=fields.Date.today)
	name = fields.Char(
		string="CIR No",
		copy=False,
		readonly=True,
	)
	ba_bsd = fields.Char(string="BA/BSD")
	project = fields.Char(string="Project")

	description = fields.Text(string="Description")

	# Description Type - Boolean Fields
	is_addition = fields.Boolean(string="Addition")
	is_replacement = fields.Boolean(string="Replacement")
	is_expansion = fields.Boolean(string="Expansion")
	is_modernization = fields.Boolean(string="Modernization")

	# Asset Category - Boolean Fields
	is_land_building = fields.Boolean(string="Land & Building")
	is_plant_equipment = fields.Boolean(string="Plant & Equipments")
	is_office_equipment = fields.Boolean(string="Office Equipments")
	is_vehicle = fields.Boolean(string="Vehicles")
	is_furniture = fields.Boolean(string="Furniture & Fixtures")
	is_tools = fields.Boolean(string="Tools")
	item_des = fields.Char(string="Item Description")
	item_type = fields.Char(string="Item Type")
	model = fields.Char(string="Model")

	local = fields.Boolean(string="Local")
	imported = fields.Boolean(string="Imported")

	estimated_cost = fields.Float(string="Estimated Cost")
	resale_value = fields.Float(string="Resale Value")
	net_cost = fields.Float(string="Net Cost", compute="_compute_net_cost", store=True)

	depreciation_years = fields.Integer(string="Depreciation Years")
	cost_per_annum = fields.Float(string="Cost Per Annum", compute="_compute_cost_per_annum", store=True)
	# Justification - Boolean Fields
	is_new_business = fields.Boolean(string="New Business Development")
	is_cost_saving = fields.Boolean(string="Cost Saving")
	is_system_improvement = fields.Boolean(string="Systems Improvement")
	is_higher_productivity = fields.Boolean(string="Higher Productivity")
	is_others = fields.Boolean(string="Others")

	budget_reference = fields.Char(string="Budget Reference No")
	budget_status = fields.Selection([
		('budgeted', 'Budgeted'),
		('unbudgeted', 'Unbudgeted')
	], string="Budget Status")

	capex_budget = fields.Float(string="CAPEX Budget")
	approved_to_date = fields.Float(string="Approved To Date")
	available_balance = fields.Float(string="Available Balance")
	this_cir = fields.Float(string="This CIR")
	remaining_balance = fields.Float(string="Remaining Balance")

	state = fields.Selection([
		('draft', 'Draft'),
		('dept_head', 'Dept Head Approval'),
		('cfo', 'CFO Approval'),
		('ceo', 'CEO Approval'),
		('approved', 'Approved'),
		('rejected', 'Rejected')
	], default='draft', tracking=True)
	cir_org = fields.Char(string="CIR Originator")
	dep_head = fields.Char(string="Department Head")
	dep_head = fields.Many2one('res.users', string="Department Head")
	ba_bsd_fc = fields.Char(string="BA/BSD FC")
	ba_bsd_head = fields.Char(string="BA/BSD Head")
	aprove_cfo = fields.Boolean(string="Approved")
	aprove_ceo = fields.Boolean(string="Approved")
	not_aprove_cfo = fields.Boolean(string="Not Approved")
	not_aprove_ceo = fields.Boolean(string="Not Approved")
	cfo_approved_by = fields.Many2one(
		'res.users',
		string="Approved By CFO",
		readonly=True,
		copy=False
	)
	ceo_approved_by = fields.Many2one(
		'res.users',
		string="Approved By CEO",
		readonly=True,
		copy=False
	)

	ceo_approved_date = fields.Date(
		string="CEO Approval Date",
		readonly=True,
		copy=False
	)
	cfo_approved_date = fields.Date(
		string="CFO Approval Date",
		readonly=True,
		copy=False
	)
	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code(
				'sl.capital.investment'
			) or 'New'
		return super(CapitalInvestment, self).create(vals)

	def action_submit(self):
		self.state = 'dept_head'
	def action_dept_head_approve(self):
		self.state = 'cfo'

	def action_cfo_approve(self):
		for rec in self:
			if not self.env.user.has_group('sl_capital_investment_req.group_cir_cfo'):
				raise UserError("Only CFO can approve.")
			rec.write({
				'state': 'ceo',
				'aprove_cfo' : True,
				'cfo_approved_by': self.env.user.id,
				'cfo_approved_date': fields.Datetime.now(),
			})
	def action_ceo_approve(self):
		for rec in self:
			if not self.env.user.has_group('sl_capital_investment_req.group_cir_hr'):
				raise UserError("Only CEO can approve.")
			rec.write({
				'state': 'approved',
				'aprove_cfo': True,
				'ceo_approved_by': self.env.user.id,
				'ceo_approved_date': fields.Datetime.now(),
			})
	def action_reject(self):
		self.state = 'rejected'