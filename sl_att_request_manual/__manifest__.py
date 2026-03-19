# -*- coding: utf-8 -*-
{
    'name': "Attendence Manual Request",

    'summary': """
       Attendence Manual Request""",

    'description': """
     Attendence Manual Request in Odoo ERP
    """,
    'author': "Dysin",
    'website': "https://www.dysin.com.pk",
    'version': '16.0.1.0',
    'depends': ['base','hr','mail','hr_attendance','sl_manual_cpl'],
    'images': ["static/description/icon.png"],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/sequence.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
