# -*- coding: utf-8 -*-
{
	'name': "Attendance Posted Report",
	'summary': 'Generate Attendance Excel Reports with filters',
	'description': """
	   Generate Attendance Excel Reports with filters
		 """,
	'category': 'Human Resources',
	'author': "Dysin",
	'website': "https://www.dysin.com.pk",
	'version': '16.0.1.0',
	'depends': ['base','hr','hr_attendance','report_xlsx','sl_attendance_xlsx_report'],
	'images': ['staatic/description/icon.png'],
	'data': [
		'security/ir.model.access.csv',
		'views/views.xml',
		'report/report.xml',
		'wizard/wizard.xml',
	],
	'installable': True,
	'auto_install': False,
	'application': True,
	'license': 'LGPL-3',
}