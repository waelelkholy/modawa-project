
# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrPayslip(models.Model):
    # Private attributes
    _inherit = 'hr.payslip'
    

    # Default methods
    @api.model
    def default_get(self, fields):
        """it'll give you all loan line which is in given time interval of payslip"""
        res = super(HrPayslip, self).default_get(fields)
        if res.get('date_from') and res.get('employee_id'):
            lone = self.env['hr.loan.line'].search \
                ([('date' ,'>=' ,res.get('date_from')) ,('date' ,'<=' ,res.get('date_to'))
                 ,('loan_id.state' ,'=' ,'posted'),
                                                    ('status' ,'=' ,'pending') ,('employee_id' ,'=' ,int(res.get('employee_id')))])
            if lone:
                res['loan_line_id'] = lone.ids
                res['loan_amount'] = sum(x.amount for x in lone)
        return res

    # Fields declaration
    loan_line_id = fields.Many2many('hr.loan.line', 'hr_loan_line_pay_rel','payslip_id','line_id', string="This Month Loan")

    loan_amount = fields.Float('Loan Amount')

    # CRUD methods (and name_get, name_search, ...) overrides
    @api.model
    def create(self, val):
        if val.get('date_from') and val.get('employee_id'):
            lone = self.env['hr.loan.line'].search \
                ([('date' ,'>=' ,val.get('date_from')) ,('date' ,'<=' ,val.get('date_to'))
                 ,('loan_id.state' ,'=' ,'posted'),
                                                    ('status' ,'=' ,'pending') ,('employee_id' ,'=' ,int(val.get('employee_id')))])
            if lone:
                val['loan_line_id'] = [(6, 0, lone.ids)]
                val['loan_amount'] = sum(x.amount for x in lone)
        return super(HrPayslip, self).create(val)

    def action_payslip_done(self):
        """its inherited function. we add in to update status of loan lines"""
        res = super(HrPayslip, self).action_payslip_done()
        if self.loan_line_id:
            self.loan_line_id.update({
                'status': 'done',
                'payslip_id': self.id
            })
        return res
