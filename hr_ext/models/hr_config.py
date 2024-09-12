# -*- coding:utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    notify_probation_emp_contract = fields.Integer(string="Notify Before End of probation Contract")
    email_probation = fields.Char("Email Address For Probation")

    iqama_expiry_days = fields.Integer(string="Notify Before Expire Iqama")
    iqama_expiry_email = fields.Char("Email Address For Expire Iqama")

    passport_expiry_days = fields.Integer(string="Notify Before expire passport")
    passport_expiry_email = fields.Char("Email Address For expire passport")

    insurance_expiry_days = fields.Integer(string="Notify Before expire Insurance")
    insurance_expiry_email = fields.Char("Email Address For expire Insurance")

    resignation_expiry_days = fields.Integer(string="Notify Before expire Resignation")
    resignation_expiry_email = fields.Char("Email Address For Resignation Email")

    contract_expiry_days = fields.Integer(string="Notify Before Expire Contract")
    contract_expiry_email = fields.Char(string="Email Address For Expired Contract")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            notify_probation_emp_contract=int(params.get_param('notify_probation_emp_contract', default=0)),
            email_probation=params.get_param('email_probation', default=''),
            iqama_expiry_days=int(params.get_param('iqama_expiry_days', default=0)),
            iqama_expiry_email=params.get_param('iqama_expiry_email', default=''),
            passport_expiry_days=int(params.get_param('passport_expiry_days', default=0)),
            passport_expiry_email=params.get_param('passport_expiry_email', default=''),
            insurance_expiry_days=int(params.get_param('insurance_expiry_days', default=0)),
            insurance_expiry_email=params.get_param('insurance_expiry_email', default=''),
            resignation_expiry_days=int(params.get_param('resignation_expiry_days', default=0)),
            resignation_expiry_email=params.get_param('resignation_expiry_email', default=''),
            contract_expiry_days=int(params.get_param('contract_expiry_days', default=0)),
            contract_expiry_email=params.get_param('contract_expiry_email', default=''),            
        )
        return res

    @api.model
    def set_values(self):
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('notify_probation_emp_contract', self.notify_probation_emp_contract)
        params.set_param('email_probation', self.email_probation)

        params.set_param('iqama_expiry_days', self.iqama_expiry_days)
        params.set_param('iqama_expiry_email', self.iqama_expiry_email)

        params.set_param('passport_expiry_days', self.passport_expiry_days)
        params.set_param('passport_expiry_email', self.passport_expiry_email)

        params.set_param('insurance_expiry_days', self.insurance_expiry_days)
        params.set_param('insurance_expiry_email', self.insurance_expiry_email)

        params.set_param('resignation_expiry_days', self.resignation_expiry_days)
        params.set_param('resignation_expiry_email', self.resignation_expiry_email)

        params.set_param('contract_expiry_days', self.contract_expiry_days)
        params.set_param('contract_expiry_email', self.contract_expiry_email)

        super(ResConfigSettings, self).set_values()
