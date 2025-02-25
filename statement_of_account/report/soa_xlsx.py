import os
from odoo import models
import json
from datetime import datetime
import operator

dirname = os.path.dirname(__file__)


class SOAXlsx(models.AbstractModel):
    _name = 'report.statement_of_account.soa_template'
    _description = "Statement of Account XLSX Report"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, report_detail, wizard_data):
        partner_id = wizard_data.customer_id
        partner_type = wizard_data.partner_type
        partner_ids = []
        if not partner_id:
            partner_ids = self.env['res.partner'].search([])
        else:
            partner_ids = partner_id
        date_f = wizard_data.date_f
        date_t = wizard_data.date_t
        type = wizard_data.payment_type

        def date_format(date):
            return date.strftime("%m-%d-%Y")

        heading_format = workbook.add_format({
            "bold": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            'font_size': '9',
            'font_name': 'Metropolis',
        })
        line_heading_format = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#ccffcc',
            'font_size': '9',
            'font_name': 'Metropolis',
            "num_format": "#,##0.00",
        })
        line_data = workbook.add_format({
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            'font_size': '9',
            'font_name': 'Metropolis',
            "num_format": "#,##0.00",
        })
        Left_line_data = workbook.add_format({
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            'font_size': '9',
            'font_name': 'Metropolis',
            "num_format": "#,##0.00",
        })

        worksheet = workbook.add_worksheet('Statement of Account XLSX Report')

        worksheet.set_column('A:E', 15)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:L', 15)

        worksheet.set_row(6, 30)

        # worksheet.merge_range('A2:C2', 'Warehouse & Logistics Services Co.', heading_format)
        # worksheet.merge_range('A3:B6', '', heading_format)
        # logo_path = os.path.join(dirname, '../static/src/img/logo.png')
        # worksheet.insert_image('A3:B6', logo_path, {'x_scale': .12, 'y_scale': .07})
        worksheet.merge_range('A1:C1',
                              'Statement of Account : ' + str(date_format(date_f)) + ' To ' + str(date_format(date_t)),
                              heading_format)
        row = 3
        for customer_id in partner_ids:

            # Invoice and credit note Data
            # print(customer_id.id,date_f,date_t)
            invoice_refund_data = self.env['account.move'].search([('partner_id', '=', customer_id.id),
                                                                   ('invoice_date', '>=', date_f),
                                                                   ('invoice_date', '<=', date_t),
                                                                   ('move_type', 'in', ['out_invoice', 'out_refund','in_invoice','in_refund']),
                                                                   ('state', '=', 'posted'),
                                                                   # ('payment_state', 'not in', ['in_payment', 'paid'])
                                                                   ])
            # print(invoice_refund_data,444444444)
            total_inv_amt = 0
            total_debit = 0
            total_credit = 0
            total_payment_rec = 0
            total_balance = 0
            index = 0
            raw_data = []
            for invoice in invoice_refund_data:
                data = {
                    'name': invoice.name,
                    # 'old_inv_number': invoice.old_invoice_no,
                    'inv_date': invoice.invoice_date,
                    'inv_address': str(invoice.partner_id.street or '')+''+str(invoice.partner_id.street2 or ''),
                    # 'product_type': str(invoice.product_type.name or ''),
                    'customer_ref': str(invoice.ref or ''),
                    'job_no': '',
                    'project': '',
                    'inv_amt_untaxed': str(invoice.amount_untaxed or ' '),
                    'amount_tax': str(invoice.amount_tax or ' '),
                    'currency': str(invoice.currency_id.name or ' '),
                    'inv_amt': invoice.amount_total if invoice.move_type == 'out_invoice' else - invoice.amount_total,
                    'debit': invoice.amount_total if invoice.move_type in ['out_invoice', 'in_refund'] else 0,
                    'credit': invoice.amount_total if invoice.move_type in ['out_refund', 'in_invoice'] else 0,
                    'payment_rec': (invoice.amount_total - invoice.amount_residual) if invoice.move_type == 'out_invoice' else -(invoice.amount_total - invoice.amount_residual),
                    'bal':  invoice.amount_residual if invoice.move_type == 'out_invoice' else - invoice.amount_residual,
                }
                data['bal'] = data['debit'] - data['credit']
                raw_data.append(data)
                total_balance = total_balance + (data['debit'] - data['credit'])

                if invoice.move_type in ['out_invoice', 'in_refund']:
                    total_debit = total_debit + invoice.amount_total
                if invoice.move_type in ['out_refund', 'in_invoice']:
                    total_credit = total_credit + invoice.amount_total
                # if invoice.move_type == 'out_invoice':
                #     total_inv_amt += invoice.amount_total
                #     total_payment_rec += invoice.amount_total - invoice.amount_residual
                #     total_balance += invoice.amount_residual
                # else:
                #     total_inv_amt -= invoice.amount_total
                #     total_payment_rec -= invoice.amount_total - invoice.amount_residual
                #     total_balance -= invoice.amount_residual

            # if type == 'reconciled':
            #     payment_ids = self.env['account.payment'].search(
            #         [('is_reconciled', '=', True), ('date', '<=', date_t), ('date', '>=', date_f),
            #          ('partner_id', '=', customer_id.id), ('partner_type', '=', 'customer')])
            # else:
            payment_ids = self.env['account.payment'].search(
                [('date', '<=', date_t), ('date', '>=', date_f),('state','!=','cancel'),
                 ('partner_id', '=', customer_id.id)])
            for payment in payment_ids:
                remaining_amount = 0
                conciled_amount = 0
                # for i in payment.reconciled_invoice_ids:
                #     # print(i)
                #     # stud_obj = json.loads(i.invoice_payments_widget)
                #     for payments in i.invoice_payments_widget['content']:
                #         if payments['account_payment_id'] == payment.id:
                #             conciled_amount = conciled_amount + payments['amount']
                # remaining_amount = payment.amount - conciled_amount
                # if remaining_amount >= 1:
                data = {
                    'name': payment.name,
                    # 'old_inv_number': '',
                    'inv_date': payment.date,
                    'inv_address': '',
                    # 'product_type': '',
                    'customer_ref': '',
                    'job_no': '',
                    'project': '',
                    'inv_amt_untaxed': str(' '),
                    'amount_tax': str(' '),
                    'currency': str(payment.currency_id.name or ' '),
                    'debit': payment.amount if payment.payment_type == 'outbound' else 0,
                    'credit': payment.amount if payment.payment_type == 'inbound' else 0,
                    'payment_rec': - conciled_amount,
                    'bal': - remaining_amount,
                }
                data['bal'] = data['debit'] - data['credit']
                total_balance = total_balance + (data['debit'] - data['credit'])
                raw_data.append(data)
                if payment.payment_type == 'outbound':
                    total_debit = total_debit + payment.amount
                if payment.payment_type == 'inbound':
                    total_credit = total_credit + payment.amount
                # worksheet.write_string(row, 0, str(payment.name), line_data)
                # worksheet.write_string(row, 2, str(date_format(payment.date)), line_data)
                # worksheet.write_number(row, 8, - payment.amount, line_data)
                # total_inv_amt = payment.amount
                # worksheet.write_number(row, 9, - conciled_amount, line_data)
                # total_payment_rec -= conciled_amount
                # worksheet.write_number(row, 10, - remaining_amount, line_data)
                total_balance -= remaining_amount
            # row += 1

            # index = index + 1

            raw_data.sort(key=lambda x: x.get('inv_date'))
            if raw_data:
                worksheet.merge_range(row - 1, 0, row - 1, 3, 'Partner Name: ' + customer_id.name, heading_format)
                worksheet.merge_range(row - 1, 4, row - 1, 5, str(" "), heading_format)
                worksheet.write_string(row, 0, 'Invoice No', line_heading_format)
                # worksheet.write_string(row, 1, 'Old Invoice No', line_heading_format)
                worksheet.write_string(row, 1, 'Invoice Date', line_heading_format)
                # worksheet.write_string(row, 2, 'Invoice Address', line_heading_format)
                # worksheet.write_string(row, 2, 'Product Type', line_heading_format)
                worksheet.write_string(row, 2, 'Reference', line_heading_format)
                # worksheet.write_string(row, 3, 'Job No', line_heading_format)
                # worksheet.write_string(row, 4, 'Project Name', line_heading_format)
                worksheet.write_string(row, 3, 'Tax Excluded', line_heading_format)
                worksheet.write_string(row, 4, 'Tax Amount', line_heading_format)
                worksheet.write_string(row, 5, 'Currency', line_heading_format)
                worksheet.write_string(row, 6, 'Debit', line_heading_format)
                worksheet.write_string(row, 7, 'Credit', line_heading_format)
                # worksheet.write_string(row, 9, 'Payment Recd', line_heading_format)
                worksheet.write_string(row, 8, 'Balance SAR', line_heading_format)
                row = row + 1
                for i in raw_data:
                    worksheet.write_string(row, 0, str(i['name']), line_data)
                    # worksheet.write_string(row, 1, str(''), line_data)
                    worksheet.write_string(row, 1, str(date_format(i['inv_date'])), line_data)
                    # worksheet.write_string(row, 2, str(i['inv_address'] if i['inv_address'] else''), line_data)
                    # worksheet.write_string(row, 2, str(''), line_data)
                    worksheet.write_string(row, 2, str(i['customer_ref'] or ''), line_data)
                    # worksheet.write_string(row, 3, str(i['job_no'] or ''), line_data)
                    # worksheet.write_string(row, 4, str(i['project'] or ''), line_data)
                    worksheet.write_string(row, 3, str(i['inv_amt_untaxed'] or ''), line_data)
                    worksheet.write_string(row, 4, str(i['amount_tax'] or ''), line_data)
                    worksheet.write_string(row, 5, str(i['currency'] or ''), line_data)
                    worksheet.write_number(row, 6, i['debit'], line_data)
                    worksheet.write_number(row, 7, i['credit'], line_data)
                    # worksheet.write_number(row, 9, i['payment_rec'], line_data)
                    worksheet.write_number(row, 8, i['bal'], line_data)
                    row += 1

                worksheet.write_string(row, 0, '', line_heading_format)
                worksheet.write_string(row, 1, '', line_heading_format)
                worksheet.write_string(row, 2, '', line_heading_format)
                worksheet.write_string(row, 3, '', line_heading_format)
                # worksheet.write_string(row, 4, '', line_heading_format)
                # worksheet.write_string(row, 5, '', line_heading_format)
                worksheet.write_string(row, 4, 'Total', line_heading_format)
                worksheet.write_string(row, 5, '', line_heading_format)
                worksheet.write_number(row, 6, total_debit, line_heading_format)
                worksheet.write_number(row, 7, total_credit, line_heading_format)
                # worksheet.write_number(row, 9, total_payment_rec, line_heading_format)
                worksheet.write_number(row, 8, total_balance, line_heading_format)

                row += 2
            # worksheet.merge_range(row, 0, row, 2, 'Kindly arrange to settle the above invoices at the earliest.',
            #                       Left_line_data)
            # row += 1
            # worksheet.merge_range(row, 0, row, 4, 'Note :  In case of any discrepancies, please notify within 10 days from '
            #                                       'date of receipt.', Left_line_data)
            # row += 1
            # worksheet.merge_range(row, 0, row, 2, 'Please remit to "Warehousing & Logistics Services Co. (LSC)"',
            #                       Left_line_data)
            # row += 1
            # worksheet.merge_range(row, 0, row, 2, 'Bank: Banque Saudi Fransi', Left_line_data)
            # row += 1
            # worksheet.merge_range(row, 0, row, 2, 'IBAN Number: SA56 5500 0000 0535 6820 0142', Left_line_data)
            # row += 2
            # worksheet.merge_range(row, 0, row, 1, 'Kind Regards,', heading_format)
            # row += 2
            # worksheet.merge_range(row, 0, row, 1, 'Iftekhar Ahmed', heading_format)
            # row += 1
            # worksheet.merge_range(row, 0, row, 1, 'Receivable    & Collection Manager', Left_line_data)
            # row += 1
            # worksheet.merge_range(row, 0, row + 3, 1, '', Left_line_data)
            # logo_path = os.path.join(dirname, '../static/src/img/logo.png')
            # worksheet.insert_image(row, 0, logo_path, {'x_scale': .12, 'y_scale': .07})
            # row += 1
            # worksheet.merge_range(row, 0, row, 1, 'Warehousing and Logistics Services Co.', Left_line_data)
            # row += 4
            # worksheet.merge_range(row, 0, row, 1, 'FALCOM Building, P.O Box: 14650,', Left_line_data)
            # row += 1
            # worksheet.merge_range(row, 0, row, 1, 'Riyadh 11434,Kingdom of Saudi Arabia.', Left_line_data)
            # row += 1
            # worksheet.merge_range(row, 0, row, 1, 'iahmed@lsclogistics.com', Left_line_data)
