# -*- coding: utf-8 -*-
{
    'name': "HR EXT",

    'summary': """
         HR EXT""",

    'description': """
        This modules contains all features such as iqama, nationality etc features
    """,

    'author': 'Awais ali',
    'website': "https://www.upwork.com/freelancers/~018ff6830780ff04b4",
    'version': '15.0.47',
    'category': 'hr',
    'depends': ['base', 'hr','provision_accouting','account','hr_contract', 'hr_employee_updation','hr_holidays'],
    'data': [
        'security/user_group.xml',
        'security/hr_leave_ir_rule.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/schedule.xml',
        # 'data/data.xml',
        'wizard/insurance_batch_view.xml',
        # 'wizard/hr_work_entry_regeneration_wizard_views.xml',
        'views/hr_contract_ext_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_contract_type.xml',
        'views/hr_iqama_view.xml',
        'views/hr_passport_view.xml',
        'views/hr_doc_type.xml',
        'views/hr_insurance_view.xml',
        'views/hr_employee_access.xml',
        'views/hr_education_type.xml',
        'views/hr_access_type.xml',
        'views/hr_nationality_detail.xml',
        'views/hr_id_type.xml',
        'views/hr_employee_banks.xml',
        # 'views/reference_letter_bank.xml',
        'views/hr_sponsor.xml',
        'views/hr_config.xml',
        'mail_format/probation_contract.xml',
        'mail_format/iqama_expire.xml',
        'mail_format/insurance_expire.xml',
        'mail_format/passport_expire.xml',
        'views/hr_policies.xml',
        'views/hr_leaves.xml',
        'views/hr_grading.xml',
        'views/hr_job_view.xml',
        'views/hr_insurance_batch_view.xml',
    ],
    'license': 'LGPL-3',
}
