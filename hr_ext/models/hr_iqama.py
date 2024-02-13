# -*- coding: utf-8 -*-

import re
from ummalqura.hijri_date import HijriDate
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrIqama(models.Model):
    _name = 'hr.iqama'
    _description = "Iqama"
    _rec_name = "iqama_name"

    iqama_name = fields.Char('Iqama/ID No.',required=True)
    employee = fields.Many2one('hr.employee',string="Employee",required=True)
    is_employee = fields.Boolean('Is employee')
    issue_date = fields.Date("Issue date")
    expiry_date = fields.Date("Expiry date")
    issue_date_ar = fields.Char("Issue date arabic")
    expiry_date_ar = fields.Char("Expiry date arabic")
    date_of_birth = fields.Date(related="employee.birthday",string="Date of Birth")
    job_pos = fields.Char("Job Position as per Iqama")
    act_job_pos = fields.Char(related="employee.job_id.name",string="Actual Job Position")
    arrival_date = fields.Date("Arrival Date in Saudi")
    place_of_issue = fields.Char("Place of Issue")
    department = fields.Many2one(related="employee.department_id",comodel_name='hr.department',string="Department")
    blood_group = fields.Selection([
        ('A+','A+'),
        ('B+','B+'),
        ('A-','A-'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),

    ],string="Blood Group")
    dependent = fields.Boolean("Dependent")
    family = fields.One2many('hr.iqama.family','hif',string="Family Iqama")
    Date_rec_gos = fields.Date("Date Recorded in Gos")
    m_i_r = fields.Float("MOL Iqama Renewal")
    gov_pay = fields.Float("Government Payment")
    e_lic = fields.Float("Eng. Licenses")
    other_payment = fields.Float("Other Payment(s)")
    tot_cost = fields.Float("Total Iqama Costs", compute="_cal_tot_cost")

    def for_import_data(self):
        """it serach all iqama and put there arabic dates"""
        rec = self.env['hr.iqama'].search([])
        for i in rec:
            if i.issue_date or i.expiry_date:
                i.get_arabic_dates()

    @api.onchange('issue_date','expiry_date')
    def get_arabic_dates(self):
        """it convert dates into arabic and assign to fields"""
        if self.issue_date:
            self.issue_date_ar = 'هـ' + HijriDate.get_hijri_date(self.issue_date)
        if self.expiry_date:
            self.expiry_date_ar = 'هـ' + HijriDate.get_hijri_date(self.expiry_date)


    @api.depends('m_i_r', 'gov_pay', 'e_lic', 'other_payment')
    def _cal_tot_cost(self):
        self.tot_cost = self.m_i_r + self.gov_pay + self.e_lic + self.other_payment

    @api.onchange('iqama_name')
    def iqama_regex(self):
        """it give the format to iqama number"""
        if(self.iqama_name):
            result = re.match('^(2)[0-9]?', self.iqama_name, flags=0)
            if (len(self.iqama_name) != 10):
                raise UserError(_('Invalid Entry. Entry should contain complete 10 numbers'))
            if(result):
                pass
            else:
                raise UserError(_('Invalid Iqama Entry'))

    @api.constrains('employee')
    def place_employee_iqama(self):
        if (self.employee.country_id.code != 'SA'):
            emp = self.env['hr.employee'].search([('id', '=', self.employee.id)])
            emp.update({'emp_iqama': self.id})
        else:
            raise UserError(_('Employee is a Saudi National'))

    _sql_constraints = [('iqama_name_uniq', 'unique (iqama_name)',
                         'Iqaama Number is already existed!')]

    def notify_iqama_expire(self):
        """
        this function run from corn job. it check the  default days from configuration and check iqama end date and send
        email to responsive person
        """
        iqama_ids = self.env['hr.iqama'].search([])
        # mail_list = []
        # msg_list = []
        # for user in set(self.env.ref("hr.group_hr_manager").users + self.env.ref("hr.group_hr_user").users):
        #     msg_list.append(user.partner_id)
        #     mail_list.append(user)
        for i in iqama_ids:
            params = self.env['ir.config_parameter'].sudo()
            before_days = params.get_param('iqama_expiry_days', default=0)
            email = params.get_param('iqama_expiry_email', default='')
            days = (i.expiry_date - fields.date.today()).days
            if days == int(before_days):
                template = self.env.ref('hr_ext.send_iqama_expire_template', False)
                template.sudo().send_mail(i.id, force_send=True,
                                          email_values={'email_to': email,
                                                        'email_from': self.env.user.login or
                                                                      self.env.user.partner_id.email})


class HrIqamaFamily(models.Model):
    _name = 'hr.iqama.family'
    _description = "Iqama Family"

    name = fields.Char("Name")
    hif = fields.Many2one('hr.iqama',string="Iqama Reference")
    nif = fields.Many2one('hr.nationality', string="NID Reference")
    hife = fields.Many2one('hr.employee', string="Employee Reference")
    iqama_number = fields.Char("Iqama Number")
    iqama_expiry = fields.Date("Iqama Expiry")
    iqama_issue_place = fields.Char("Iqama Issues Place")
    relation = fields.Many2one('relation',string="Relation")


class Relation(models.Model):
    _name = 'relation'
    _description = 'Family Relations '

    name = fields.Char("Relation Name", required=1)