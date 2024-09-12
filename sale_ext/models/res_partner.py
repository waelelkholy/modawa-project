# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    # Private attributes
    _inherit = 'res.partner'

    no_more_orders = fields.Boolean()