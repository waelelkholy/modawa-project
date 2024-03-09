# -*- coding: utf-8 -*-

{
    'name': 'Founder Stock Expiry Report / Notification',
    'version': '15.0.1',
    'summary': 'Product Stock Expiry Report / Notification via email',
    'description': 'Product Stock Expiry Report / Notification via email',
    'category': 'Warehouse',
    'author': 'Awais ali',
    'website': "https://www.upwork.com/freelancers/~018ff6830780ff04b4",
    'license': 'LGPL-3',
    'depends': ['stock', 'product_expiry'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_stock_expiry_wiz_view.xml',
        'views/product_view.xml',
        'views/stock_config_settings_view.xml',
        'report/report_product_stock_expiry.xml',
        'report/report_action_view.xml',
        'data/product_stock_expiration_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}
