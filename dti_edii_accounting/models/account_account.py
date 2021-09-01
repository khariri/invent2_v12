from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re

class AccountAccount(models.Model):
    _inherit = 'account.account'

    saldo_normal = fields.Selection([('debit','Debit'),('credit','Credit')], string='Jenis Saldo', default='debit')
    parent_id    = fields.Many2one('account.account','Parent')