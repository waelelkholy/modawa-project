# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProvisionRule(models.Model):
    _name = 'provision.rule'
    _description = "Provision Rule"

    name = fields.Char('Name')
    type = fields.Selection([('EOS','EOS'),('Tickets','Tickets'),('Vacation','Vacation'),('Car Policy','Car Policy'),('Exit Re-Entry','Exit Re-Entry'),('Medical Insurance','Medical Insurance')])
    active = fields.Boolean('Active',default=True)
