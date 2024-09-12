# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from lxml import etree
from odoo import api, fields, models, _, SUPERUSER_ID
import ast
import logging
_logger = logging.getLogger(__name__)


READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'sale', 'done', 'cancel'}
}

class SaleOrder(models.Model):
    # Private attributes
    _inherit = 'sale.order'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=True, readonly=False, change_default=True, index=True,
        tracking=1,
        states=READONLY_FIELD_STATES,
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id)),('customer_rank','>',0)]")
    check_user = fields.Boolean(compute='check_user_group')

    @api.depends('user_id')
    def check_user_group(self):
        for rec in self:
            if self.env.user.has_group('saleperson_ext.group_sale_person'):
                rec.check_user = True
            else:
                rec.check_user = False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        context = self._context
        res = super(SaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                     submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            if self.env.user.has_group('saleperson_ext.group_sale_person'):
                for node in doc.iter(tag="form"):
                    node.attrib['edit'] = 'false'
                    orders = self.sudo().env['ir.model.fields'].search([
                                                                        ('model_id.model', '=',
                                                                         'sale.order')])
                    for i in orders:
                        for xpath in doc.xpath("//field[@name='" + i.name + "']"):
                            # if i.name not in ['partner_id','partner_shipping_id']:
                            #     xpath.attrib['readonly'] = True

                            if 'options' in xpath.attrib:
                                f_op = ast.literal_eval(xpath.attrib['options'])
                                f_op['no_open'] = True
                                xpath.attrib['options'] = str(f_op)
                            else:
                                xpath.attrib['options'] = "{'no_open': True,'no_create': True}"
                            res['arch'] = etree.tostring(doc, encoding='unicode')

        return res