# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Data Extend',
    'version': '1.2',
    'sequence': 15,
    'summary': "Inherited employee model through this module",
    'description': 'Inherited employee module through this application',
    'website': 'https://www.smartbrain.tech',
    'depends': ['base','mail','hr', 'new_shift_employee_dysin'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
        # 'views/employee_grade_view.xml',
        # 'views/job_levels.xml',
        # 'views/hr_contract.xml',

    ],
    # 'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}