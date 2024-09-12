# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class HrSponsor(models.Model):
    _name = 'hr.sponsor'
    _description = "Sponsor"
    _rec_name = "name"

    name = fields.Char("Name", required=True)
    sponsor_id = fields.Integer('Sponsor Id')
    Phone = fields.Integer('Phone')
    email = fields.Char('Email')
    # establ_labor_off_no = fields.Char("Establishment Labor Office No")
