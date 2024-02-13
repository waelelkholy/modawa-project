
# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from ummalqura.hijri_date import HijriDate
from odoo.exceptions import UserError, ValidationError
import os
from num2words import num2words
from datetime import datetime, timedelta
import base64
from odoo.tools import config
from os.path import dirname
from datetime import date


class HrContract(models.Model):
    _inherit = 'hr.contract'

    joining_date = fields.Date("Date of Join")
    contract_end_at = fields.Selection([(str(1), '1 Year'), (str(2), '2 Year')])
    probation_period = fields.Selection(
        [(str(30), '30 day'), (str(60), '60 day'), (str(90), '90 day'), (str(180), '180 day')])
    probation_end_date = fields.Date('Probation End Date')
    level = fields.Many2one('hr.policies',required=0)
    insurance_class = fields.Selection(related='level.insurance_class')

    air_ticket = fields.Selection(string='Air Ticket for Expats',related='level.air_ticket')
    class_air_ticket = fields.Selection(string='Class of Travel for Expats',related='level.class_air_ticket')

    re_entry_for_annual_vacation = fields.Selection(string='Exit Re-entry for Annual Vacation',related='level.re_entry_for_annual_vacation')
    notice_period = fields.Selection(string='Notice Period for all',related='level.notice_period')
    schooling_assistance = fields.Selection(string='Schooling Assistance',related='level.schooling_assistance')

    policies = fields.Boolean(default=False)
    gender = fields.Selection(related='employee_id.gender')
    religion = fields.Selection(string="Religion",related="employee_id.religion")
    contract_status = fields.Selection([('single', 'Single'), ('family', 'Family')], string="Contract Status")
    employee_no = fields.Char()
    employee_old_no = fields.Char()

    @api.onchange('contract_end_at','date_start')
    def onchange_contract_period(self):
        if self.contract_end_at and self.date_start:
            if self.contract_end_at == '1':
                self.date_end = self.date_start.replace(self.date_start.year + 1) - timedelta(1)
            if self.contract_end_at == '2':
                self.date_end = self.date_start.replace(self.date_start.year + 2) - timedelta(1)

    @api.onchange('joining_date', 'probation_period')
    def cal_probation_end_date(self):
        """
        this calculate the probation ending date
        """
        for rec in self:
            if rec.joining_date and rec.probation_period:
                rec.probation_end_date = rec.joining_date + timedelta(int(rec.probation_period))

    @api.onchange('employee_id')
    def get_employee_class(self):
        self.employee_no = self.employee_id.employee_number
        # self.employee_old_no = self.employee_id.old_employee_number
        if self.employee_id and self.employee_id.level:
            self.level = self.employee_id.level.id
            self.onchange_level()


    def notify_probation_contract(self):
        """
        this function run from corn job. it check the  default days from configuration and check contract which is on
        probation and its contract and default days are equal then email send
        """
        contracts = self.env['hr.contract'].search([('probation_period', '!=', False)])
        mail_list = []
        msg_list = []
        for user in set(self.env.ref("hr.group_hr_manager").users + self.env.ref("hr.group_hr_user").users):
            msg_list.append(user.partner_id)
            mail_list.append(user)
        for i in contracts:
            params = self.env['ir.config_parameter'].sudo()
            before_days = params.get_param('notify_probation_emp_contract', default=0)
            email = params.get_param('email_probation', default='')
            days = (i.probation_end_date - fields.date.today()).days
            if days == int(before_days):
                template = self.env.ref('hr_ext.send_probation_contract_template', False)
                template.sudo().send_mail(i.id, force_send=True,
                                          email_values={'email_to': email,
                                                        'email_from': self.env.user.login or
                                                                      self.env.user.partner_id.email})

    def run_policies(self):
        """
        this function generates Leaves allocation according to there level
        """
        if self.level:
            # Marriage
            if self.level.marriage_leave:
                marriage_leave_type = self.env['hr.leave.type'].search([('name', '=', 'marriage')])
                if not marriage_leave_type:
                    work_entry_type = self.env['hr.work.entry.type'].search([('name', '=', 'Legal Leaves 2021')])
                    marriage_leave_type = self.env['hr.leave.type'].create({
                        'name': 'marriage',
                        'validity_start': date(date.today().year, 1, 1),
                        'leave_validation_type': 'manager',
                        'work_entry_type_id': work_entry_type.id,
                    })
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " marriage allocation",
                        'number_of_days': self.level.marriage_leave,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': marriage_leave_type.id
                    })
                else:
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " marriage allocation",
                        'number_of_days': self.level.marriage_leave,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': marriage_leave_type.id,
                    })
            #  Death
            if self.level.death_leave:
                death_leave_type = self.env['hr.leave.type'].search([('name', '=', 'death')])
                if not death_leave_type:
                    work_entry_type = self.env['hr.work.entry.type'].search([('name', '=', 'Legal Leaves 2021')])
                    death_leave_type = self.env['hr.leave.type'].create({
                        'name': 'death',
                        'validity_start': date(date.today().year, 1, 1),
                        'leave_validation_type': 'manager',
                        'work_entry_type_id': work_entry_type.id,
                    })
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " Death allocation",
                        'number_of_days': self.level.death_leave,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': death_leave_type.id
                    })
                else:
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " Death allocation",
                        'number_of_days': self.level.death_leave,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': death_leave_type.id

                    })
            # Paternity (Male)
            if self.level.paternity_leave and self.employee_id.gender == 'male':
                paternity_leave_type = self.env['hr.leave.type'].search([('name', '=', 'Paternity')])
                if not paternity_leave_type:
                    work_entry_type = self.env['hr.work.entry.type'].search([('name', '=', 'Legal Leaves 2021')])
                    paternity_leave_type = self.env['hr.leave.type'].create({
                        'name': 'Paternity',
                        'validity_start': date(date.today().year, 1, 1),
                        'leave_validation_type': 'manager',
                        'work_entry_type_id': work_entry_type.id,
                    })
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " Paternity allocation",
                        'number_of_days': self.level.death_leave,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': paternity_leave_type.id
                    })
                else:
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " Paternity allocation",
                        'number_of_days': self.level.death_leave,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': paternity_leave_type.id
                    })
            # muslim widow
            if self.level.muslim_widow and self.employee_id.gender == 'female' and self.employee_id.religion == 'Muslim':
                muslim_widow_leave_type = self.env['hr.leave.type'].search([('name', '=', 'Muslim Widow')])
                if not muslim_widow_leave_type:
                    work_entry_type = self.env['hr.work.entry.type'].search([('name', '=', 'Legal Leaves 2021')])
                    muslim_widow_leave_type = self.env['hr.leave.type'].create({
                        'name': 'Muslim Widow',
                        'validity_start': date(date.today().year, 1, 1),
                        'leave_validation_type': 'manager',
                        'work_entry_type_id': work_entry_type.id,
                    })
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " Muslim Widow allocation",
                        'number_of_days': self.level.muslim_widow,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': muslim_widow_leave_type.id
                    })
                else:
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " Muslim Widow allocation",
                        'number_of_days': self.level.muslim_widow,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': muslim_widow_leave_type.id
                    })
            # Non - muslim widow
            if self.level.muslim_widow and self.employee_id.gender == 'female' and self.employee_id.religion == 'NonMuslim':
                non_muslim_widow_leave_type = self.env['hr.leave.type'].search([('name', '=', 'Non Muslim Widow')])
                if not non_muslim_widow_leave_type:
                    work_entry_type = self.env['hr.work.entry.type'].search([('name', '=', 'Legal Leaves 2021')])
                    non_muslim_widow_leave_type = self.env['hr.leave.type'].create({
                        'name': 'Non Muslim Widow',
                        'validity_start': date(date.today().year, 1, 1),
                        'leave_validation_type': 'manager',
                        'work_entry_type_id': work_entry_type.id,
                    })
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " Non Muslim Widow allocation",
                        'number_of_days': self.level.non_muslim_widow,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': non_muslim_widow_leave_type.id
                    })
                else:
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " Non Muslim Widow allocation",
                        'number_of_days': self.level.non_muslim_widow,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': non_muslim_widow_leave_type.id
                    })
            # Hajj
            if self.level.hajj and self.employee_id.religion == 'Muslim':
                hajj_leave_type = self.env['hr.leave.type'].search([('name', '=', 'Hajj')])
                if not hajj_leave_type:
                    work_entry_type = self.env['hr.work.entry.type'].search([('name', '=', 'Legal Leaves 2021')])
                    hajj_leave_type = self.env['hr.leave.type'].create({
                        'name': 'Hajj',
                        'validity_start': date(date.today().year, 1, 1),
                        'leave_validation_type': 'manager',
                        'work_entry_type_id': work_entry_type.id,
                    })
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " Hajj allocation",
                        'number_of_days': self.level.hajj,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': hajj_leave_type.id
                    })
                else:
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " Hajj allocation",
                        'number_of_days': self.level.hajj,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': hajj_leave_type.id,
                    })
            # Annual
            if self.level.annual:
                annual_leave_type = self.env['hr.leave.type'].search([('name', '=', 'Annual')])
                if not annual_leave_type:
                    work_entry_type = self.env['hr.work.entry.type'].search([('name', '=', 'Legal Leaves 2021')])
                    annual_leave_type = self.env['hr.leave.type'].create({
                        'name': 'Annual',
                        'validity_start': date(date.today().year, 1, 1),
                        'leave_validation_type': 'manager',
                        'work_entry_type_id': work_entry_type.id,
                    })
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " Annual allocation",
                        'allocation_type': 'accrual',
                        'date_from': self.joining_date if self.joining_date > date(2021, 9, 1) else date(2021, 9, 1),
                        'date_to': self.date_end if self.date_end else False,
                        'number_per_interval': self.level.annual / 12,
                        'number_of_days': self.level.annual / 12,
                        'unit_per_interval': 'days',
                        'interval_number': 1,
                        'interval_unit': 'months',
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': annual_leave_type.id
                    })
                else:
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " Annual allocation",
                        'allocation_type': 'accrual',
                        'date_from': self.joining_date if self.joining_date > date(2021, 9, 1) else date(2021, 9, 1),
                        'date_to': self.date_end if self.date_end else False,
                        'number_per_interval': self.level.annual / 12,
                        'number_of_days': self.level.annual / 12,
                        'unit_per_interval': 'days',
                        'interval_number': 1,
                        'interval_unit': 'months',
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': annual_leave_type.id,
                    })
            # Paid Maternity (Female)
            if self.level.paid_maternity_leave and self.employee_id.gender == 'female':
                paid_maternity_leave_type = self.env['hr.leave.type'].search([('name', '=', 'Paid Maternity')])
                if not paid_maternity_leave_type:
                    work_entry_type = self.env['hr.work.entry.type'].search([('name', '=', 'Legal Leaves 2021')])
                    paid_maternity_leave_type = self.env['hr.leave.type'].create({
                        'name': 'Paid Maternity',
                        'validity_start': date(date.today().year, 1, 1),
                        'leave_validation_type': 'manager',
                        'work_entry_type_id': work_entry_type.id,
                    })
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " Paid Maternity allocation",
                        'number_of_days': self.level.paid_maternity_leave,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': paid_maternity_leave_type.id
                    })
                else:
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " Paid Maternity allocation",
                        'number_of_days': self.level.paid_maternity_leave,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': paid_maternity_leave_type.id
                    })
            # Un Paid Maternity (Female)
            if self.level.unpaid_maternity_leave and self.employee_id.gender == 'female':
                unpaid_maternity_leave_type = self.env['hr.leave.type'].search([('name', '=', 'UnPaid Maternity')])
                if not unpaid_maternity_leave_type:
                    work_entry_type = self.env['hr.work.entry.type'].search([('name', '=', 'Unpaid')])
                    unpaid_maternity_leave_type = self.env['hr.leave.type'].create({
                        'name': 'UnPaid Maternity',
                        'validity_start': date(date.today().year, 1, 1),
                        'leave_validation_type': 'manager',
                        'work_entry_type_id': work_entry_type.id,
                    })
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " UnPaid Maternity allocation",
                        'number_of_days': self.level.unpaid_maternity_leave,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': unpaid_maternity_leave_type.id
                    })
                else:
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': self.employee_id.name + " UnPaid Maternity allocation",
                        'number_of_days': self.level.unpaid_maternity_leave,
                        'employee_id': self.employee_id.id,
                        'holiday_status_id': unpaid_maternity_leave_type.id
                    })
            #  Examination
            paid_maternity_leave_type = self.env['hr.leave.type'].search([('name', '=', 'Examination')])
            if not paid_maternity_leave_type:
                work_entry_type = self.env['hr.work.entry.type'].search([('name', '=', 'Legal Leaves 2021')])
                paid_maternity_leave_type = self.env['hr.leave.type'].create({
                    'name': 'Examination',
                    'validity_start': date(date.today().year, 1, 1),
                    'leave_validation_type': 'manager',
                    'work_entry_type_id': work_entry_type.id,
                })

            self.policies = True

    @api.onchange('employee_id')
    def make_contract_name(self):
        if self.employee_id:
            self.name = self.employee_id.name
        if self.employee_id and self.employee_id.hire_date:
            self.joining_date = self.employee_id.hire_date

    @api.onchange('level')
    def onchange_level(self):
        if self.level and self.level.notice_period:
            if self.level.notice_period:
                if self.level.notice_period == '2':
                    self.notice_days = 60
                if self.level.notice_period == '3':
                    self.notice_days = 90


    @api.constrains('level', 'wage')
    def check_level_and_wage(self):
        if self.level and self.wage:
            if not self.level.min_salary <= self.wage <= self.level.max_salary:
                raise UserError(_('Wage should be between Level Max and Min salary range'))

    #override to add name FORM AMPLOYEE NAME
    @api.model
    def create(self, vals):
        res = super(HrContract, self).create(vals)
        res.name = res.employee_id.name
        # if res.employee_id and res.employee_id.hire_date:
        #     res.joining_date = res.employee_id.hire_date
            # res.employee_id.hire_date = res.joining_date
        # if not res.joining_date:
        #     raise UserError(_('Joining Date is required'))
        return res

    # def write(self, vals):
    #     res = super(HrContract, self).write(vals)
    #     if self.employee_id and self.employee_id.hire_date:
    #         self.joining_date = self.employee_id.hire_date
    #         # self.employee_id.hire_date = self.joining_date
    #     # if not self.joining_date:
    #     #     raise UserError(_('Joining Date is required'))
    #     return res

    # Notification send for expiry contract
    def notify_contract_expiry(self):
        before_days = self.env['ir.config_parameter'].sudo().get_param('contract_expiry_days')
        email = self.env['ir.config_parameter'].sudo().get_param('contract_expiry_email')
        if email and before_days:
            for data in self.search([('date_end','!=',False)]):
                days = (data.date_end - fields.date.today()).days
                if days == int(before_days):
                    mail_content = "Hello Contract OF Employee :- "   + data.name + ",<br>is going to expire on " + \
                                   str(data.date_end) + ". Please renew it before expiry date"
                    main_content = {
                        'subject': _('Contracts-%s Expired On %s') % (data.name, data.date_end),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': email,
                    }
                    mail_id = self.env['mail.mail'].create(main_content).send()
