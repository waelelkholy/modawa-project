# -*- coding: utf-8 -*-
{
    'name': "Sale Ext",

    'summary': """ it customize Sale module """,

    'description': """
        Long description of module's purpose
    """,
    'version': '15.0.19',
    'category': 'Generic Modules/Sale',
    'author': 'Awais ali',
    'website': "https://www.upwork.com/freelancers/~018ff6830780ff04b4",
    'depends': ['base', 'sale', 'sale_mrp'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
    ],
    'license': 'LGPL-3',

}
