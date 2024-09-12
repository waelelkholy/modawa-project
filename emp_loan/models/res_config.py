from odoo import api, fields, models
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    loan_payment_journal = fields.Many2one(comodel_name="account.journal", string="Loan Payment Journal")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            loan_payment_journal=int(params.get_param('loan_payment_journal', default=False)),
        )
        return res

    @api.model
    def set_values(self):
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('loan_payment_journal', self.loan_payment_journal.id)
        super(ResConfigSettings, self).set_values()
