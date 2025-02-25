# -*- coding: utf-8 -*-
{
    'name': "Statement of Account Report",
    'summary': """
    Statement of Account Report
    """,
    'author': 'Awais ali',
    'website': "https://www.upwork.com/freelancers/~018ff6830780ff04b4",
    'category': 'Accounting',
    'version': '16.0',
    'depends': ['base', 'report_xlsx', 'account_accountant', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'wizard/soa_view.xml',
    ],
}