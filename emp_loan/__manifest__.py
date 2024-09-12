# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Loan Management',
    'version': '15.0.29',
    'summary': 'Manage Loan Requests',
    'description': """
        Helps you to manage Loan Requests of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': 'Awais ali',
    'website': "https://www.upwork.com/freelancers/~018ff6830780ff04b4",
    'depends': ['base', 'hr_payroll', 'hr', 'account','hr_ext'],
    'data': [
        # data
        'data/hr_loan_seq.xml',
        'data/notification_send_to_manager.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        #wizard
        'wizard/forward_next_month.xml',
        'wizard/cash_payment_register.xml',
        'wizard/reject_reason_view.xml',
        'views/hr_loan.xml',
        'views/loan_type.xml',
        'views/hr_payslip.xml',
        'views/res_config.xml',
        # 'views/hr_loan_configuration_view.xml',

    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',

}
#result = -payslip.loan_amount