# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrLoan(models.Model):
    _name = 'loan.type'
    _description = "Loan Type"


    name = fields.Char(string="Loan Type", required=True)
    max_loan_amount_percentage = fields.Float(string="Maximum loan Amount (%)")
    max_deduction = fields.Float(string="Maximum Deduction Amount(%)")