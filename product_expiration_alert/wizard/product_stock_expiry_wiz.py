# -*- coding: utf-8 -*-

from odoo import api, fields, models
import xlwt
from io import BytesIO
import base64
import datetime

class ProductStockExpiration(models.TransientModel):
    _name = "product.stock.expiration"
    _description = "Product Stock Expiration wizard"

    report_days = fields.Integer(string="Generate Report For(Next Days)", required=True, help="Number of days product will be expire in stock")
    include_expire_stock = fields.Boolean(string="Include Expire Stock", help="Past and Future product stock expire report form select Include Expire Stock.")
    report_type = fields.Selection([
        ('all', 'All'),
        ('location', 'Location'),
        ], string='Report Type', default='all', help="Filter based on location wise and all stock product expiration report")
    location_ids = fields.Many2many("stock.location", string="Filter by Locations", help="Check Product Stock for Expiration from selected Locations only. if its blank it checks in all Locations")

    # Generate Product Stock Expiration report
    def print_product_stock_expiration_report(self):
        data = {}
        data['form'] = (self.read(['report_days', 'include_expire_stock', 'report_type', 'location_ids'])[0])
        return self.env.ref('product_expiration_alert.action_report_product_stock_expiration').report_action(self, data=data, config=False)

    @api.model
    def default_get(self, fields):
        rec = super(ProductStockExpiration, self).default_get(fields)
        company_id = self.env.user.company_id
        rec['report_days'] = company_id.report_days
        rec['include_expire_stock'] = company_id.include_expire_stock
        rec['report_type'] = company_id.report_type
        rec['location_ids'] = [(6, 0, company_id.location_ids.ids)]
        return rec

    # Generate Product Stock Expiration Excel report
    def product_stock_expiration_excel_report(self):
        filename = 'Product Stock Expiration Report''.xls'
        workbook = xlwt.Workbook(encoding="UTF-8")

        worksheet = workbook.add_sheet('Product Stock Expiry Report')
        font = xlwt.Font()
        font.bold = True
        GREEN_TABLE_HEADER = xlwt.easyxf(
                 'font: bold 1, name Tahoma, height 250;'
                 'align: vertical center, horizontal center, wrap on;'
                 'borders: top double, bottom double, left double, right double;'
                 )
        style = xlwt.easyxf('font:height 400, bold True, name Arial; align: horiz center, vert center;borders: top medium,right medium,bottom medium,left medium')
        for_left_center = xlwt.easyxf("font: color black; align: horiz left")
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style = xlwt.easyxf('align: wrap yes')
        style.num_format_str = '0.00'

        worksheet.row(0).height = 320
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 3000
        worksheet.col(2).width = 6000
        worksheet.col(3).width = 5000

        borders = xlwt.Borders()
        borders.bottom = xlwt.Borders.MEDIUM
        border_style = xlwt.XFStyle()
        border_style.borders = borders

        product_stock_expiration_title = 'Product Stock Expiry Report'
        worksheet.write_merge(0, 1, 0, 3, product_stock_expiration_title, GREEN_TABLE_HEADER)

        row = 2
        worksheet.write(row, 0, 'PRODUCT NAME' or '', for_left_center)
        worksheet.write(row, 1, 'QUANTITY' or '', for_left_center)
        worksheet.write(row, 2, 'LOTS/SERIAL NUMBER' or '', for_left_center)
        worksheet.write(row, 3, 'EXPIRY DATE' or '', for_left_center)

        return_list = {}
        StockProductionObj = self.env['stock.lot']
        return_list['report_days'] = self.report_days
        current_date = datetime.date.today() + datetime.timedelta(days=self.report_days)
        domain = [('use_date', '<', str(current_date))]
        if not self.include_expire_stock:
            domain += [('use_date', '>', str(fields.Datetime.now()))]
        if self.report_type == 'location':
            domain += [('quant_ids.location_id', 'in', self.location_ids.ids)]
        lot_ids = StockProductionObj.search(domain)

        seq = 0
        for lot_id in lot_ids.filtered(lambda lot_id: lot_id.product_qty > 0):
            seq = seq + 1
            row = row + 1
            worksheet.write(row, 0, lot_id.product_id.display_name or '', for_left_center)
            worksheet.write(row, 1, lot_id.product_qty or 0, for_left_center)
            worksheet.write(row, 2, lot_id.name or '', for_left_center)
            worksheet.write(row, 3, str(lot_id.use_date) or '', for_left_center)

        fp = BytesIO()
        workbook.save(fp)
        stock_expiration_excel_id = self.env['stock.expiration.report.excel.extended'].create({'excel_file': base64.b64encode(fp.getvalue()), 'file_name': filename})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_xls_report/%s' % (stock_expiration_excel_id.id),
            'target': 'new',
        }

class ProductStockReportExcelExtended(models.Model):
    _name = "stock.expiration.report.excel.extended"
    _description = "Product Stock Expiration Excel File"

    excel_file = fields.Binary('Download Report :- ')
    file_name = fields.Char('Excel File', size=64)
