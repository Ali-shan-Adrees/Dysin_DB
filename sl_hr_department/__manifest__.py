# -*- coding: utf-8 -*-
{
    'name': "HR Department",
    'summary': """
       HR Department Customization""",
    'description': """
        HR Department Customization
    """,
    'author': "Dysin",
    'website': "https://www.dysin.com.pk",
    'category': 'HR',
    'version': '16.0.1.0',
    'depends': ['base','hr',],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
