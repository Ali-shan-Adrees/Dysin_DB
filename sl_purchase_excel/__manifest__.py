# -*- coding: utf-8 -*-
{
    'name': "Purchase Excel Report",
    'summary': """
        Purchase Excel Report
        """,
    'description': """
       Purchase Excel Report
    """,
    'version': '16.0.1.0.0',
    'category': 'Purchase',
    'author': "Dysin",
    'website': "https://www.dysin.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'images': ['static/description/icon.png'],
    'depends': ['purchase', 'report_xlsx'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard.xml',
        'report/report.xml',
        'views/views.xml',
    ],
}
