# -*- coding: utf-8 -*-
{
    'name': "Hr Payroll Ext",

    'summary': """ it customize payroll module """,

    'description': """
        Long description of module's purpose
    """,
    'version': '15.0.19',
    'category': 'Generic Modules/Human Resources/payroll',
    'author': 'Awais ali',
    'website': "https://www.upwork.com/freelancers/~018ff6830780ff04b4",
    'depends': ['base', 'hr_payroll','hr_ext', 'hr_contract_allowances'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payslip_view.xml',
        'views/hr_deduction.xml',
        'views/hr_allowances.xml',
        'views/payroll_menu.xml',
        # 'views/payroll_email_template.xml',
    ],
    'license': 'LGPL-3',

}
