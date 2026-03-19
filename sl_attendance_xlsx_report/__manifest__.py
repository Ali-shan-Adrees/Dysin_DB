# -*- coding: utf-8 -*-
{
    'name': "Employee Attendance Excel Report",
    'summary': """Export employee attendance data in Excel with department-wise grouping. Filter by date, department, and employee using a simple wizard. Generate HR reports instantly in Odoo.""",
    'description': "This module allows HR teams and managers to export detailed employee attendance reports in Excel format (.xlsx) directly from Odoo. "
                   "Using a clean and user-friendly wizard, users can select:"
                   "Start and End Date,"
                   "Optional Department(s),"
                   "Optional Employee(s)",
    'license': 'OPL-1',
    'category': 'Human Resources',
    'author': 'Secure Logic Technology',
    'website': 'https://www.securelogic.pk',
    'version': '16.0.0.1',
    'price': 35,
    'currency': 'EUR',
    'depends': ['base', 'hr', 'hr_contract', 'hr_attendance', 'resource'],
    'data': [
        # 'security/security.xml',
        'security/ir.model.access.csv',
        'views/attendance_report_wizard_view.xml',
        'views/attendance_report_menu.xml',
        'views/monthly_attendance_report_wizard.xml',
        # 'views/attendance_report_group_view.xml',
        'data/attendance_email_template.xml',
        'data/attendance_report_action.xml',
        'report/attendance_custom_header_footer.xml',
        'report/monthly_attendance_report_template.xml',
    ],
    'images': ["static/description/banner.gif"],
    'live_test_url': 'https://www.youtube.com/@becomefuturestar',
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,

}
