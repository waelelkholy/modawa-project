# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class HrPassport(models.Model):
    _name = 'hr.passport'
    _description = "Passport"
    _rec_name = "passport_number"

    employee = fields.Many2one('hr.employee', string="Employee")
    passport_name = fields.Char("Name as Passport")
    passport_number = fields.Char("Passport Number",required=True)
    passport_issue_date = fields.Date("Passport Expiry date")
    expiry_date = fields.Date("Expiry date")
    is_employee = fields.Boolean("Is a Employee")
    passport_issue_country = fields.Char("Passport issue country")
    passport_issue_place = fields.Char("Passport issue Place")
    passport_status = fields.Selection([('we', 'With Employee'), ('wc', 'With Company')], string="Passport Status")
    is_dependent = fields.Boolean("Is a Dependent")
    d_passport_name = fields.Char("Dependent Name as Passport")
    passport_relation = fields.Selection([('wife', 'Wife'),
                                           ('son', 'Son'),
                                           ('daug', 'Daughter'),
                                           ], string="Passport Relation")
    d_emp = fields.Many2one('hr.employee')
    iqama_no = fields.Char(related="employee.emp_iqama.iqama_name")
    nationality_id = fields.Many2one('res.country', string="Nationality")
    date_of_birth = fields.Date(string="Date of Birth")
    gender = fields.Selection([('male', 'Male'),('Female', 'Female')], string="Gender")

    @api.onchange('is_dependent','employee')
    def _onchange_is_dependent(self):
        """it check the checkbox of dependent and bring employee """
        if self.is_dependent:
            if self.employee:
                self.d_emp = self.employee
            self.is_employee = False

    @api.onchange('is_employee')
    def check_boolean(self):
        """it check employee passport and set on passport fields """
        if self.is_employee:
            self.passport_name = self._context.get('default_passport_name')
            self.is_dependent = False
            self.d_emp = False
        else:
            self.passport_name = ''

    @api.constrains('is_dependent','is_employee')
    def check_passport_type_type(self):
        if not self.is_employee and not self.is_dependent:
            raise UserError(_('Select the Checkbox is a Employee or is a Dependent'))

    @api.constrains('employee')
    def place_employee_passport(self):
        pas = self.env['hr.passport'].search([('employee', '=', self.employee.id),('is_employee', '=', True)])
        if pas:
            if len(pas) > 1:
                raise UserError(_('This Employee Already Has Passport information !'))
            else:
                if self.is_employee:
                    __ = self.env['hr.employee'].search([('id', '=', self.employee.id)]).update(
                        {'passport': self.id})


    _sql_constraints = [('passport_number_uniq', 'unique (passport_number)',
                         'Passport Number is already existed!')]

    def notify_passport_expire(self):
        """
        this function run from corn job. it check the  default days from configuration and check Passport end date and send
        email to responsive person
        """
        iqama_ids = self.env['hr.passport'].search([])
        for i in iqama_ids:
            params = self.env['ir.config_parameter'].sudo()
            before_days = params.get_param('insurance_expiry_days', default=0)
            email = params.get_param('insurance_expiry_email', default='')
            if i.expiry_date:
                days = (i.expiry_date - fields.date.today()).days
                if days == int(before_days):
                    template = self.env.ref('hr_ext.send_passport_expire_template', False)
                    template.sudo().send_mail(i.id, force_send=True,
                                              email_values={'email_to': email,
                                                            'email_from': self.env.user.login or
                                                                          self.env.user.partner_id.email})

