# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError, ValidationError


class HrCustody(models.Model):
    """
        Hr custody contract creation model.
        """
    _name = 'hr.custody'
    _description = 'Hr Custody Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    read_only = fields.Boolean(string="check field")

    #override default get method
    @api.model
    def default_get(self, default_fields):
        rec = super(HrCustody, self).default_get(default_fields)
        if self._context.get('custody_type') == 'return':
            rec['custody_type'] = 'return'
        return rec

    @api.onchange('employee')
    def _compute_read_only(self):
        """ Use this function to check weather the user has the permission to change the employee"""
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr.group_hr_user'):
            self.read_only = True
        else:
            self.read_only = False

    def mail_reminder(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([('state', '=', 'approved')])
        for i in match:
            if i.return_date:
                exp_date = fields.Date.from_string(i.return_date)
                if exp_date <= date_now:
                    base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                    url = base_url + _('/web#id=%s&view_type=form&model=hr.custody&menu_id=') % i.id
                    mail_content = _('Hi %s,<br>As per the %s you took %s on %s for the reason of %s. S0 here we '
                                     'remind you that you have to return that on or before %s. Otherwise, you can '
                                     'renew the reference number(%s) by extending the return date through following '
                                     'link.<br> <div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
                                     'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
                                     'border-color:#875A7B;text-decoration: none; display: inline-block; '
                                     'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
                                     'cursor: pointer; white-space: nowrap; background-image: none; '
                                     'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
                                     'Renew %s</a></div>') % \
                                   (i.employee.name, i.name, i.custody_name.name, i.date_request, i.purpose,
                                    date_now, i.name, url, i.name)
                    main_content = {
                        'subject': _('REMINDER On %s') % i.name,
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.employee.work_email,
                    }
                    mail_id = self.env['mail.mail'].create(main_content)
                    mail_id.mail_message_id.body = mail_content
                    mail_id.send()
                    if i.employee.user_id:
                        mail_id.mail_message_id.write({'partner_ids': [(4, i.employee.user_id.partner_id.id)]})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.custody')
        return super(HrCustody, self).create(vals)

    def sent(self):
        # if self.custody_type == 'normal':
        #     self.custody_name.is_used = True
        #     self.custody_name.state = 'acquired'
        #     self.custody_name.employee_id = self.employee.id
        #     self.employee.property_ids = [(4,self.custody_name.id)]
        # else:
        #     self.employee.property_ids = [(3, self.return_property_id.id)]
        #     self.return_property_id.is_used = False
        #     self.return_property_id.state = 'free'
        #     self.return_property_id.employee_id = False
        if self.employee.user_id and self.custody_type == 'normal':
            res_model_id = self.env['ir.model'].search(
                [('name', '=', self._description)]).id
            search_mail_activity_id = self.env['mail.activity'].search([('res_id','=',self.id),('user_id','=',self.employee.user_id.id)])
            if not search_mail_activity_id:
                message = "Please approve the Custody :-" + " " +  str(self.name) + "which is created by :-" + " " +str(self.env.user.name)
                activity_id =  self.env['mail.activity'].create([{'activity_type_id': 4,
                                                   'date_deadline': datetime.today(),
                                                   'summary': self.name,
                                                   'create_uid' : self.employee.user_id.id,
                                                   'user_id': self.employee.user_id.id,
                                                   'res_id': self.id,
                                                   'res_model_id': res_model_id,
                                                   'note': message,
                                                   }])                    
        else:
            res_model_id = self.env['ir.model'].search(
                [('name', '=', self._description)]).id
            search_mail_activity_id = self.env['mail.activity'].search([('res_id','=',self.id),('user_id','=',self.employee.user_id.id)])
            if not search_mail_activity_id:                      
                message = "Please approve the Custody :-" + " " +  str(self.name) + "which is created by :-" + " " +str(self.env.user.name)
                activity_id =  self.env['mail.activity'].create([{'activity_type_id': 4,
                                                         'date_deadline': datetime.today(),
                                                         'summary': self.name,
                                                         'create_uid' : self.employee.user_id.id,
                                                         'user_id': self.employee.user_id.id,
                                                         'res_id': self.id,
                                                         'res_model_id': res_model_id,
                                                         'note': message,
                                                         }])
        # self.send_mail()
        self.state = 'to_approve'

    def send_mail(self):
        template = self.env.ref('hr_custody_ext.custody_email_notification_template')
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        self.mail_send = True

    def set_to_draft(self):
        self.state = 'draft'

    def renew_approve(self):
        for custody in self.env['hr.custody'].search([('custody_name', '=', self.custody_name.id)]):
            if custody.state == "approved":
                raise UserError(_("Custody is not available now"))
        self.return_date = self.renew_date
        self.renew_date = ''
        self.state = 'approved'

    def renew_refuse(self):
        for custody in self.env['hr.custody'].search([('custody_name', '=', self.custody_name.id)]):
            if custody.state == "approved":
                raise UserError(_("Custody is not available now"))
        self.renew_date = ''
        self.state = 'approved'

    def approve(self):
        # for custody in self.env['hr.custody'].search([('custody_name', '=', self.custody_name.id)]):
        #     if custody.state == "approved":
        #         raise UserError(_("Custody is not available now"))
        if self.custody_type == 'normal':
            self.custody_name.is_used = True
            self.custody_name.state = 'acquired'
            self.custody_name.employee_id = self.employee.id
            self.employee.property_ids = [(4,self.custody_name.id)]
        else:
            self.employee.property_ids = [(3, self.return_property_id.id)]
            self.return_property_id.is_used = False
            self.return_property_id.state = 'free'
            self.return_property_id.employee_id = False

        if self.custody_type == 'normal':
            self.state = 'approved'
        else:
            self.state = 'returned'
            self.return_date = fields.Date.today()
        for data in self.activity_ids:
            data.action_done()

    def set_to_return(self):
        return {
            'name': _('Return Date'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'return.date',
            'target' : 'new',
            'view_id' : self.env.ref('hr_custody_ext.wizard_return_date').id,
            'type': 'ir.actions.act_window',
        }
        # self.state = 'returned'
        # self.return_date = date.today()

    # # return date validation
    # @api.constrains('return_date')
    # def validate_return_date(self):
    #     if self.return_date < self.date_request:
    #         raise ValidationError(_('Please Give Valid Return Date'))

    name = fields.Char(string='Code', copy=False, help="Code")
    company_id = fields.Many2one('res.company', 'Company', readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id, copy=False)
    rejected_reason = fields.Text(string='Rejected Reason',  readonly=1, help="Reason for the rejection", copy=False)
    renew_rejected_reason = fields.Text(string='Renew Rejected Reason', copy=False, readonly=1,
                                        help="Renew rejected reason")
    date_request = fields.Date(string='Requested Date', required=True, tracking=True, readonly=True,
                               help="Requested date",
                               states={'draft': [('readonly', False)]}, default=datetime.now().strftime('%Y-%m-%d'), copy=False)
    employee = fields.Many2one('hr.employee', string='Employee', required=True, readonly=True, help="Employee",
                               default=lambda self: self.env.user.employee_id.id,
                               states={'draft': [('readonly', False)]}, copy=False)
    property_ids = fields.Many2many(related="employee.property_ids")
    purpose = fields.Char(string='Reason', tracking=True, required=True, readonly=True, help="Reason",
                          states={'draft': [('readonly', False)]})
    custody_name = fields.Many2one('custody.property', string='Property', readonly=True, help="Property name",
                                   states={'draft': [('readonly', False)]}, copy=False)
    return_date = fields.Date(string='Return Date', tracking=True, readonly=True,
                              help="Return date",
                              states={'draft': [('readonly', False)]}, copy=False)
    
    renew_date = fields.Date(string='Renewal Return Date', tracking=True,
                             help="Return date for the renewal", readonly=True, copy=False)
    notes = fields.Html(string='Notes', copy=False)
    renew_return_date = fields.Boolean(default=False, copy=False)
    renew_reject = fields.Boolean(default=False, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'Waiting For Approval'), ('approved', 'Approved'),
                              ('returned', 'Returned'), ('rejected', 'Refused')], string='Status', default='draft',
                             tracking=True)
    custody_type = fields.Selection([('normal', 'Normal'), ('return', 'Return')], default='normal',string='Custody Type', tracking=True, copy=False)
    mail_send = fields.Boolean(string="Mail Send")
    return_property_id = fields.Many2one('custody.property', string='Return Property', readonly=True, help="Return Property name",
                                   states={'draft': [('readonly', False)]}, copy=False)

    #override method to make restict on it
    def unlink(self):
        for data in self:
            if data.state not in ['draft']:
                raise UserError(_('You can delete only draft status records...'),)
        return super(HrCusto, self).unlink()

class HrPropertyName(models.Model):
    """
            Hr property creation model.
            """
    _name = 'custody.property'
    _description = 'Property Name'

    name = fields.Char(string='Property Name', required=True)
    image = fields.Image(string="Image",
                         help="This field holds the image used for this provider, limited to 1024x1024px")
    image_medium = fields.Binary(
        "Medium-sized image", attachment=True,
        help="Medium-sized image of this provider. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized image", attachment=True,
        help="Small-sized image of this provider. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    desc = fields.Html(string='Description', help="Description")
    company_id = fields.Many2one('res.company', 'Company', help="Company",
                                 default=lambda self: self.env.user.company_id)
    property_selection = fields.Selection([('empty', 'No Connection'),
                                           ('product', 'Products')],
                                          default='empty',
                                          string='Property From', help="Select the property")

    product_id = fields.Many2one('product.product', string='Product', help="Product")
    is_used = fields.Boolean(string="Is Used Property")
    state = fields.Selection([('acquired', 'Acquired'), ('free', 'Free')], string='Status', default='free')
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True, help="Employee")
    # def _compute_read_only(self):
    #     """ Use this function to check weather the user has the permission to change the employee"""
    #     res_user = self.env['res.users'].search([('id', '=', self._uid)])
    #     print(res_user.has_group('hr.group_hr_user'))
    #     if res_user.has_group('hr.group_hr_user'):
    #         self.read_only = True
    #     else:
    #         self.read_only = False


    @api.onchange('product_id')
    def onchange_product(self):
        self.name = self.product_id.name


class HrReturnDate(models.TransientModel):
    """Hr custody contract renewal wizard"""
    _name = 'wizard.return.date'
    _description = 'Hr Custody Name'

    returned_date = fields.Date(string='Renewal Date', required=1)

    # renewal date validation
    @api.constrains('returned_date')
    def validate_return_date(self):
        context = self._context
        custody_obj = self.env['hr.custody'].search([('id', '=', context.get('custody_id'))])
        if self.returned_date <= custody_obj.date_request:
            raise ValidationError('Please Give Valid Renewal Date')

    def proceed(self):
        context = self._context
        custody_obj = self.env['hr.custody'].search([('id', '=', context.get('custody_id'))])
        custody_obj.write({'renew_return_date': True,
                           'renew_date': self.returned_date,
                           'state': 'to_approve'})
