# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'OD Request',
    'version': '16.0.1.2',
    'sequence': 14,
    'author': 'Smart Brain Technology',
    'category': 'Sales',
    'summary': "OD module will create outdoor duty slip",
    'description': 'This module will help too all employees when they are going to outstation for company work. '
               'Simple create request and send to your own manager. Manager will accept or reject if he will accept '
               'your OD will automatically show at gate keeper.',

    'website': 'https://www.smartbrain.tech',
    'price': 12.99,
    'currency': 'EUR',
    'depends': ['base','mail','hr', 'crm', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu.xml',
        'views/od_view.xml',
        # 'views/full_image_modal.xml',
        'views/travel_authority.xml',
        'views/res_config_settings_views.xml',
        'report/header_footer_template.xml',
        'report/visit_travel_authority_header_footer.xml',
        'report/od_template_report.xml',
        'report/travel_authority_template_report.xml',
        'report/visit_report_template.xml',
        'report/od_action_report.xml',
        'report/travel_authority_visit_report_template.xml',
        'wizard/attach_report_wizard_view.xml',
        'wizard/travel_authority_wizards_view.xml',
        'wizard/payment_wizards_view.xml'
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'outdoor_duty/static/src/css/style.css',
    #         'outdoor_duty/static/src/js/full_image_modal.js',
    #
    #     ],
    # },
    'images': ['static/description/image/banner.png'],
    # 'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}