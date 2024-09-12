# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class ProvisionCloseConfirm(models.TransientModel):
    _name = "provision.close.confirm"
    _description = "Provision Close Confirm"
    
    # Get Default provision_close_id
    @api.model
    def default_get(self,fields):
        res = super(ProvisionCloseConfirm,self).default_get(fields)
        active_id = self._context.get('active_id',False)
        if active_id:
            res['provision_close_id'] = self.env['provision.close'].browse(active_id).id
        return res
    
    provision_close_id = fields.Many2one('provision.close',string='Close')
    
    # Action provision_close_id Confirm
    def action_confirm(self):
        if self.provision_close_id:
            self.provision_close_id.sudo().action_close_provision()