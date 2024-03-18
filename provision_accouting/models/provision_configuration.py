# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProvisionConfiguration(models.Model):
    _name = 'provision.configuration'
    _description = "Provision Configuration"

    name = fields.Char('Name')
    rule_id = fields.Many2one('provision.rule','Rule')
    debit_account_id = fields.Many2one('account.account','Debit Account')
    credit_account_id = fields.Many2one('account.account','Credit Account')
    journal_id = fields.Many2one('account.journal','Journal')
    type = fields.Selection(related="rule_id.type",string="Type")
    eos_config_line = fields.One2many('eos.config','eos_config_id','EOS Config')
    struct_id = fields.Many2one('hr.payroll.structure',string='Salary Structure')
    salary_rule_ids = fields.Many2many('hr.salary.rule','provision_configuration_hr_salary_rule_rel','salary_rule_id','provision_id',string='Salary Rules')
    active = fields.Boolean('Active',default=True)
    
    #add constraints to add validation on it...
    @api.constrains('rule_id','struct_id')
    def _check_data(self):
        search_relevant_record_id = self.search([('rule_id','=',self.rule_id.id),('struct_id','=',self.struct_id.id),
                                                ('id','!=',self.id)])
        if search_relevant_record_id:
            raise UserError(_("Same Provision Rules and Salary Structure Already Exists.....!"))

class EosConfig(models.Model):
    _name = 'eos.config'
    _description = 'EOS Configuration'
    
    eos_config_id = fields.Many2one('provision.configuration','Eos Config')
    sign = fields.Selection([('l','Less Than'),('g','Greater Than')])
    year = fields.Integer('Year')
    salary = fields.Selection([('half','Half Salary'),('full','Full Salary')])
    