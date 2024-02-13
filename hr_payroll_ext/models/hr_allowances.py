
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class PayrollAllowance(models.Model):
    # Private attributes
    _name = 'payroll.allowance'
    _rec_name = 'employee_id'
    _description = "Payroll Allowance"

    # Fields declaration
    employee_id = fields.Many2one('hr.employee',required=1)
    date = fields.Date(required=1)
    allowance_type = fields.Many2one('allowance.type',required=1)
    allowance_price = fields.Float(required=1)
    state = fields.Selection([('draft', 'draft'), ('approve', 'approve')], default='draft')

    #override method to make restict on it
    def unlink(self):
        for data in self:
            if data.state not in ['draft']:
                raise UserError(
                    _('You can delete only draft status records...'),
                )
        return super(PayrollAllowance, self).unlink()

    def approve_allowance(self):
        self.state = 'approve'


class AllowanceType(models.Model):
    # Private attributes
    _name = 'allowance.type'
    _description = "Allowance Type"

    # Fields declaration
    name = fields.Char(required=1)
    short_code = fields.Char(required=1)