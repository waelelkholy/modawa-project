# -*- coding: utf-8 -*-
{
    'name' : 'Provision Accounting',
    'version' : '15.0.2',
    'summary': 'Provision Accounting',
    'description': """
        Provision Accounting
        
        =======================================================
        =======================================================
        
        Odoo Version 15.0.1
        
        =======================================================
        
        """,
    'category': '',
    'author': 'Awais ali',
    'website': "https://www.upwork.com/freelancers/~018ff6830780ff04b4",
    'depends' : ['base','account','hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'security/user_group.xml',
        'data/provision_rule_data.xml',
        'data/ir_cron_data.xml',
        'wizard/employee_import_file_view.xml',
        'wizard/provision_create_view.xml',
        'wizard/provision_close_view.xml',
        'wizard/mass_provision_close_view.xml',
        'wizard/provision_close_confirm_view.xml',
        # 'views/account_asset_templates.xml',
        'views/provision_rule_view.xml',
        'views/provision_configuration_view.xml',
        'views/hr_employee_view.xml',
        'views/account_provision_view.xml'
    ],
    'assets': 
    {
        'web.assets_backend': [
            'provision_accouting/static/src/scss/account_asset.scss',
            'provision_accouting/static/src/js/account_asset.js',
        ],
        'web.qunit_suite_tests': [
            'provision_accouting/static/tests/account_asset_tests.js'
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
