# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class HrInsurance(models.Model):
    _name = 'hr.insurance'
    _description = "Insurance"
    _rec_name = "insurance_member_non_emp"

    insurance_company = fields.Char("Insurance Company name", required=True)
    insurance_member_emp = fields.Char(string="Member name")
    insurance_member_non_emp = fields.Many2one('hr.employee',
                                               string="Member(Employee) name")  # automatically gets emp name if insurance is emp only
    start_date = fields.Date("Start date")
    end_date = fields.Date("End date")
    is_employee = fields.Boolean("Is a Employee")
    premium = fields.Float("Premium")
    insurance_relation = fields.Selection([('wife','Wife'),
                                              ('son', 'Son'),
                                              ('daug', 'Daughter'),
                                              ('emp', 'Employee'),

                                              ],string="Insurance Relation")
    classes = fields.Selection([('vip', 'VIP'), ('a', 'A'), ('b', 'B'), ('c', 'C')])
    card_code = fields.Char("Card Code")
    gender = fields.Selection([('M','Male'),('F','Female')],string="Gender")

    iqama_no = fields.Char()
    iqama_expiry_date = fields.Date()
    policy_number = fields.Char(string="Policy Number")
    iqama_no_emp = fields.Char()
    iqama_expiry_date_emp = fields.Date()
    contract_id = fields.Many2one('hr.contract',related='insurance_member_non_emp.contract_id')
    hr_insurance_batch_id = fields.Many2one('hr.insurance.batch', string="Insurance Batch ID")

    # placeofbirth = fields.Char("Place of Birth")

    # @api.onchange('is_employee')
    # def check_boolean(self):
    #     if self.is_employee:
    @api.onchange('is_employee')
    def onchange_isemployee(self):
        """it return the old employee name and attach partner when we change related user"""
        if self.is_employee:
            self.iqama_no = False
            self.iqama_expiry_date = False
        else:
            self.iqama_no_emp = False
            self.iqama_expiry_date_emp = False

    @api.constrains('premium')
    def check_premium(self):
        if self.premium < 0:
            raise UserError(_('Premium should be positive'))

    @api.onchange('insurance_member_non_emp')
    def get_iqama_info(self):
        """check employee insurance and update iqama info"""
        if self.insurance_member_non_emp:
            self.iqama_no_emp = self.insurance_member_non_emp.emp_iqama.iqama_name
            self.iqama_expiry_date_emp = self.insurance_member_non_emp.emp_iqama.expiry_date
            if self.insurance_member_non_emp.contract_id and self.insurance_member_non_emp.contract_id.level:
                if self.insurance_member_non_emp.contract_id.level.insurance_class:
                    self.classes = self.insurance_member_non_emp.contract_id.level.insurance_class


    def notify_insurance_expire(self):
        """
        this function run from corn job. it check the  default days from configuration and check insurance end date and send
        email to responsive person
        """
        iqama_ids = self.env['hr.insurance'].search([])
        for i in iqama_ids:
            params = self.env['ir.config_parameter'].sudo()
            before_days = params.get_param('passport_expiry_days', default=0)
            email = params.get_param('passport_expiry_email', default='')
            days = (i.end_date - fields.date.today()).days
            if days == int(before_days):
                template = self.env.ref('hr_ext.send_insurance_expire_template', False)
                template.sudo().send_mail(i.id, force_send=True,
                                          email_values={'email_to': email,
                                                        'email_from': self.env.user.login or
                                                                      self.env.user.partner_id.email})








