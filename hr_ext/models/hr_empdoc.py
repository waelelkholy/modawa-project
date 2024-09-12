# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from datetime import datetime, date, timedelta

class HrEmpDoc(models.Model):
    _name = 'hr.emp.doc'
    _description = "Employee Document"
    _rec_name = "type"

    hrdoc = fields.Many2one('hr.employee', string="Insurance Ref", required=1)
    # name = fields.Char("Document Name")
    type = fields.Many2one('hr.emp.doc.type',string="Document Type")
    start_date = fields.Date("Document Start date")
    end_date = fields.Date("Document End date")
    upload_file = fields.Many2many('ir.attachment')
    file_name = fields.Char(string="File Name")
    issue_place = fields.Char(string="Issue Place")
    document_no = fields.Char(string="Document No")

    #email reminder for relavant document 
    def mail_reminder(self):
        for data in self.search([('type','!=',False),('end_date','!=',False)]):
            now = datetime.now()
            date_now = now.date()
            if data.type.no_of_days:
                exp_date = data.end_date - timedelta(days=int(data.type.no_of_days))
                if date_now >= exp_date:
                    mail_content = "  Hello  " + data.hrdoc.name + ",<br>Your Document " + data.type.name + "is going to expire on " + \
                                   str(data.end_date) + ". Please renew it before expiry date"
                    main_content = {
                        'subject': _('Document-%s Expired On %s') % (data.type.name, data.end_date),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': data.hrdoc.work_email,
                    }
                    self.env['mail.mail'].create(main_content).send()
                    document_expiry_id = self.env.ref('hr_ext.document_expiry_channel')
                    if document_expiry_id:
                        vals = {'subject': _('Document- Expired'),
                                'body': str(data.hrdoc.name) + " - " + _('Document-%s Expired On %s') % (data.type.name, data.end_date),
                                'message_type' : 'comment',
                                'subtype_id' : 1,
                                'res_id' : document_expiry_id.id,
                                'model' : 'mail.channel',
                                'record_name' : document_expiry_id.name,
                                }
                        message_id = self.env['mail.message'].create(vals)
                    #to create notification for hr administrator
                    # for data in self.env['res.users'].search([]):
                    #     if data.has_group('hr.group_hr_manager'):
                    #         res_model_id = self.env['ir.model'].search(
                    #             [('name', '=', self._description)]).id
                    #         search_mail_activity_id = self.env['mail.activity'].search([('res_id','=',self.id),('user_id','=',data.id)])
                    #         if not search_mail_activity_id:
                    #             activity_id = self.env['mail.activity'].create([{'activity_type_id': 4,
                    #                                                'date_deadline': datetime.today(),
                    #                                                'summary': self.hrdoc.name,
                    #                                                'create_uid' : data.id,
                    #                                                'user_id': data.id,
                    #                                                'res_id': self.id,
                    #                                                'res_model_id': res_model_id,
                    #                                                'note': 'Document Expired...!',
                    #                                                }])


class HrDocType(models.Model):
    _name = 'hr.emp.doc.type'
    _description = "Employee Document"

    name = fields.Char("Name", required=1)
    no_of_days = fields.Char(string="Alert before expiration (Days)")