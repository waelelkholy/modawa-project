# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrBanks(models.Model):
    _name = 'hr.banks'
    _description = "Employee Banks"
    _rec_name = "acc_number"

    acc_number = fields.Char("Account Number",required=True)
    bank_name = fields.Char("Bank Name")
    employee = fields.Many2one('hr.employee', string="Employee")
    title = fields.Char("Title of Account")
    swift_code = fields.Char("Swift Code")

    _sql_constraints = [('acc_number_uniq', 'unique (acc_number)',
                         'Account Number is already existed!')]

    @api.constrains('employee')
    def place_employee_bank_change(self):
        """
        when create bank record then it update also on employee
        """
        _ = self.env['hr.employee'].search([('id', '=', self.employee.id)]).update(
            {'bank_id': self.id})

    @api.constrains('acc_number')
    def place_employee_bank(self):
        """
        ristric bank account on 12 digits
        """
        if (len(self.acc_number) > 24 or len(self.acc_number) < 12):
            raise UserError(_('Invalid Entry. Entry should contain minimum 12 numbers and maximum 24'))

    # def write(self, values):
    #     if self.env.user.has_group('hr_ext.group_bank_admin'):
    #         return super(HrBanks, self).write(values)
    #     else:
    #         raise UserError(_("You can't edit bank details"))
