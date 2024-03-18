# -*- coding: utf-8 -*-
{
    'name': "emp_increment",

    'summary': """
        Employee increment""",

    'description': """
        Employee increment
    """,

    'author': 'Awais ali',
    'website': "https://www.upwork.com/freelancers/~018ff6830780ff04b4",

    'category': 'HR',
    'version': '15.0.17',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_contract_allowances','hr_ext', 'provision_accouting'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/schedule.xml',
        'wizard/reject_reason_view.xml',
        'views/res_config.xml',
        'views/emp_increment_views.xml',
        'views/hr_employee.xml',
        'reports/employee_increment.xml',
        'reports/reports.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
