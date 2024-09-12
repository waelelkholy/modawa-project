# -*- coding: utf-8 -*-
{
    'name': 'HRMS Custody',
    'version': '15.0.19',
    'summary': """Manage the company properties when it is in the custody of an employee""",
    'description': 'Manage the company properties when it is in the custody of an employee',
    'category': 'Generic Modules/Human Resources',
    'author': 'Awais ali',
    'website': "https://www.upwork.com/freelancers/~018ff6830780ff04b4",
    'depends': ['hr', 'mail', 'hr_employee_updation','hr_ext','product'],
    'data': [
        'security/custody_security.xml',
        'security/ir.model.access.csv',
        'views/wizard_reason_view.xml',
        'views/custody_view.xml',
        'views/hr_custody_notification.xml',
        'views/hr_employee_view.xml',
        'views/notification_mail.xml',
        'reports/custody_report.xml',
        'wizard/return_date_view.xml',
    ],
    'demo': ['data/demo_data.xml'],
    'license': 'LGPL-3',
}
