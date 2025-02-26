import os
from odoo import models
import json
from datetime import datetime
import operator

dirname = os.path.dirname(__file__)


class CRXlsx(models.AbstractModel):
    _name = 'report.customer_report.cr_report_template'
    _description = "Statement of Account XLSX Report"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, report_detail, wizard_data):

        def date_format(date):
            return date.strftime("%m-%d-%Y")

        # desgin Format
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

        worksheet = workbook.add_worksheet('Partner XLSX Report')

        partner_id = wizard_data.customer_id
        date_f = wizard_data.date_f
        date_t = wizard_data.date_t
        selected_partners = wizard_data.customer_id
        worksheet.set_column('A:E', 15)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:L', 15)
        if selected_partners:
            partners = selected_partners.ids
        else:
            partners = self.env['res.partner'].search([]).ids

        domain = [("partner_id", "in", partners), ("move_id.state", "=", "posted")]

        # Opening Balance (Before Date From)
        opening_domain = domain + [("date", "<", date_f)]
        opening_lines = self.env["account.move.line"].search(opening_domain)
        opening_balances = {
            partner: sum(line.debit - line.credit for line in opening_lines.filtered(lambda l: l.partner_id.id == partner))
            for partner in partners
        }

        # Transactions in Date Range
        transaction_domain = domain + [("date", ">=", date_f), ("date", "<=", date_t)]
        transactions = self.env["account.move.line"].search(transaction_domain)

        report_data = {}
        for partner in partners:
            partner_transactions = transactions.filtered(lambda l: l.partner_id.id == partner)
            debit = sum(partner_transactions.mapped("debit"))
            credit = sum(partner_transactions.mapped("credit"))
            opening_balance = opening_balances.get(partner, 0)
            closing_balance = opening_balances.get(partner, 0) + (debit - credit)

            # Only include partners that have non-zero Opening Balance, Debit, or Credit
            if opening_balance != 0 or debit != 0 or credit != 0:
                report_data[partner] = {
                    "opening_balance": opening_balance,
                    "debit": debit,
                    "credit": credit,
                    "closing_balance": closing_balance,
                    "lines": partner_transactions,
                }
        row = 3
        worksheet.merge_range('A1:C1',
                              'Partner Statement : ' + str(date_format(date_f)) + ' To ' + str(date_format(date_t)),
                              heading_format)
        worksheet.write_string(row, 0, 'Partner Name', line_heading_format)
        worksheet.write_string(row, 1, 'Opening Balance', line_heading_format)
        worksheet.write_string(row, 2, 'Credit', line_heading_format)
        worksheet.write_string(row, 3, 'Debit', line_heading_format)
        worksheet.write_string(row, 4, 'Closing Balance', line_heading_format)
        row = 4
        for partner_id, data in report_data.items():
            partner_name = self.env["res.partner"].browse(partner_id).name
            print(f"Partner: {partner_name}")
            print(
                f"Opening Balance: {data['opening_balance']}, Debit: {data['debit']}, Credit: {data['credit']}, Closing Balance: {data['closing_balance']}")
            print("Transactions:")
            for line in data["lines"]:
                print(
                    f"  Date: {line.date}, Debit: {line.debit}, Credit: {line.credit}, Balance: {line.debit - line.credit}")
            print("-" * 50)
            worksheet.write_string(row, 0, str(partner_name), line_data)
            worksheet.write(row, 1, data['opening_balance'], line_data)
            worksheet.write(row, 2, data['credit'], line_data)
            worksheet.write(row, 3, data['debit'], line_data)
            worksheet.write(row, 4, data['closing_balance'], line_data)
            row = row + 1