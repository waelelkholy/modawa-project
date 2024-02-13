# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, tools

class HrAmountConfiguration(models.Model):
    _name = 'loan.amount.configuration'
    _description = "Loan Amount configuration"
    _rec_name = 'max_loan_amount_percentage'

    loan_type_id = fields.Many2one('loan.type', string="Loan Type")
    max_loan_amount_percentage = fields.Float(string="Maximum loan Amount (%)")
    max_deduction = fields.Float(string="Maximum Deduction Amount(%)")