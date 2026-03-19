# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Att / CPL',
    'version': '1.0',
    'sequence': 50,
    'summary': "Compensatry Leave Request in Odoo ERP",
    'description': 'Compensatry Leave Request in Odoo ERP',
    'website': 'https://www.securelogic.pk',
    'depends': ['base', 'mail', 'hr_holidays'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/view_cpl.xml',
        'data/sequence.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
