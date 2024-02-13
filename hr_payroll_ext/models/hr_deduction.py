
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class PayrollDeduction(models.Model):
    _name = 'payroll.deduction'
    _rec_name = 'employee_id'
    _description = "Payroll Deduction"

    employee_id = fields.Many2one('hr.employee',required=1)
    date = fields.Date(required=1)
    deduction_type = fields.Many2one('deduction.type',required=1)
    deduct_price = fields.Float(required=1)
    state = fields.Selection([('draft', 'draft'), ('approve', 'approve')], default='draft')

    def approve_deduction(self):
        self.state = 'approve'

    #override method to make restict on it
    def unlink(self):
        for data in self:
            if data.state not in ['draft']:
                raise UserError(
                    _('You can delete only draft status records...'),
                )
        return super(PayrollDeduction, self).unlink()

class DeductionType(models.Model):
    _name = 'deduction.type'
    _description = "Deduction Type"

    name = fields.Char(required=1)
    short_code = fields.Char(required=1)