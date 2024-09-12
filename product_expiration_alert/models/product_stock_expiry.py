# -*- encoding: utf-8 -*-

from odoo import api, models, fields
import time
import datetime
from odoo.exceptions import UserError

class IrCron(models.Model):
    _inherit = 'ir.cron'

    # Get product Stock Expiration Email
    def get_product_stock_expiration_email(self):
        report_days = self.env.user.company_id.report_days
        include_expire_stock = self.env.user.company_id.include_expire_stock
        location_ids = self.env.user.company_id.location_ids
        report_type = self.env.user.company_id.report_type
        return_list = {}
        StockProductionObj = self.env['stock.lot']
        return_list['type'] = report_type
        return_list['report_days'] = report_days

        current_date = datetime.date.today() + datetime.timedelta(days=report_days)
        domain = [('use_date', '<', str(current_date))]
        if not include_expire_stock:
            domain += [('use_date', '>', str(fields.Datetime.now()))]
        if report_type == 'location':
            domain += [('quant_ids.location_id', 'in', location_ids)]
        lot_ids = StockProductionObj.search(domain)
        return lot_ids

    @api.model
    def product_stock_expiration_send_email(self):
        if self.get_product_stock_expiration_email():
            user_ids = self.env.user.company_id.notification_user_ids
            if user_ids:
                ctx = {}
                email_list = [user.email for user in user_ids if user.email]
                if email_list:
                    ctx['email_to'] = ','.join([email for email in email_list if email])
                    ctx['email_from'] = self.env.user.email
                    ctx['send_email'] = True
                    template = self.env.ref('product_expiration_alert.email_template_product_stock_expiration')
                    mail_id = template.with_context(ctx).send_mail(self.env.user.id, force_send=True, raise_exception=False)
                    return mail_id
