# -*- coding: utf-8 -*-

from odoo import api, fields, models

class LoanRejectReason(models.TransientModel):
    _name = 'loan.reject.reason'
    _description = 'Loan Reject Reason'

    name = fields.Text(string="Canecl/Reject Reason")

    #when click on reject button
    def action_reject_apply(self):
        loan_id = self.env['hr.loan'].browse(self.env.context.get('active_ids'))
        loan_id.write({'state' : 'cancelled', 'cancel_reason' : self.name})
        loan_id.loan_lines.unlink()
        return True