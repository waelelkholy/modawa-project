# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class HrAsset(models.Model):
    _name = 'hr.asset'
    _description = "Employee Assets"
    _rec_name = "type_asset"

    asset_type = fields.Char("Assets Type", required=1)
    issue_date = fields.Date("Issue Date")
    approved_by = fields.Many2one('hr.employee', string="Approved by")
    type_asset = fields.Many2one('hr.asset.type', string="Asset Type")


class HrAssetType(models.Model):
    _name = 'hr.asset.type'
    _description = "Employee Asset Type"

    name = fields.Char("Name", required=1)
