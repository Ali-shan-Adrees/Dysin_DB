# -*- coding: utf-8 -*-
{
    'name': "Capital Investment Request",
    'summary': """
        Capital Investment Request""",
    'description': """
       Capital Investment Request
    """,
    'author': "Dysin",
    'website': "https://www.dysin.com.pk",
    'category': 'Accounting',
    'version': '16.0.1.0.0',
    'depends': ['base','mail','hr','sl_hr_department'],
    'images': ['static/description/icon.png'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
