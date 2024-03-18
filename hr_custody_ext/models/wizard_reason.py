# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WizardReason(models.TransientModel):
    """
        Hr custody contract refuse wizard.
            """
    _name = 'wizard.reason'
    _description = "Wizard Reason"

    def send_reason(self):
        context = self._context
        reject_obj = self.env[context.get('model_id')].search([('id', '=', context.get('reject_id'))])
        if 'renew' in context.keys():
            reject_obj.write({'state': 'approved',
                              'renew_reject': True,
                              'renew_rejected_reason': self.reason})
            if context.get('model_id') == 'hr.holidays':
                reject_obj.employee.property_ids =  [(3, reject_obj.return_property_id.id)]
                reject_obj.return_property_id.is_used = False
                reject_obj.return_property_id.state = 'free'
                reject_obj.return_property_id.employee_id = False
        else:
            if context.get('model_id') == 'hr.holidays':
                reject_obj.write({'rejected_reason': self.reason})
                reject_obj.action_refuse()
            else:
                reject_obj.write({'state': 'rejected',
                                  'rejected_reason': self.reason})
                if reject_obj.custody_type == 'normal':
                    reject_obj.employee.property_ids =  [(3, reject_obj.return_property_id.id)]
                    reject_obj.custody_name.is_used = False
                    reject_obj.custody_name.state = 'free'
                    reject_obj.custody_name.employee_id = False

    reason = fields.Text(string="Reason", help="Reason")
