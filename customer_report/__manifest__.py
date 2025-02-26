# -*- coding: utf-8 -*-
{
    'name': "Customer statement Report",
    'summary': """
    Customer Statement Report
    """,
    'author': 'Awais ali',
    'website': "https://www.upwork.com/freelancers/~018ff6830780ff04b4",
    'category': 'Accounting',
    'version': '16.0',
    'depends': ['base', 'report_xlsx', 'account_accountant', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'wizard/customer_report_wizard.xml',
    ],
}