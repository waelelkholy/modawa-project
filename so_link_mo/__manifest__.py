# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'So link to Mo',
    'version': '16.0.1',
    'summary': 'Sale order link to MO',
    'description': """
        Sale Order link with Manufacturing
        """,
    'category': 'Generic Modules/Sale Order to Manufacturing',
    'author': 'Awais ali',
    'website': "https://www.upwork.com/freelancers/~018ff6830780ff04b4",
    'depends': ['base', 'sale', 'mrp'],
    'data': [
        # data
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/mrp_production.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',

}
#result = -payslip.loan_amount