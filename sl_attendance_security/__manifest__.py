# -*- coding: utf-8 -*-
{
    'name': "Attendance Security",
    'summary': """
    Attendance Security
      """,
    'description': """
        Attendance Security
    """,
    'author': "Dysin",
    'website': "https://www.dysin.com.pk",
    'category': 'Security',
     'version': '16.0.1.0',
    'depends': [
        'hr',
        'hr_attendance',
        'hr_attendance_zktecho',
        'sl_hr_department'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'security/security.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}

