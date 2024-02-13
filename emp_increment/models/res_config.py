# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    employee_increment_user_ids = fields.Many2many('res.users', 'employee_increment_rel', 'company_id', 'user_id',string="Increment Notification Users", help="Notification will send to this users when create new Employee Increment in System.")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_employee_increment = fields.Boolean(string="Is Employee Increment Approval", config_parameter='emp_increment.is_employee_increment')
    employee_increment_user_ids = fields.Many2many(related='company_id.employee_increment_user_ids', string="Notification Users", help="Notification will send to this users when create new Employee Increment in System.", readonly=False)