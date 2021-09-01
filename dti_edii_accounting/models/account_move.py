from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re

class AccountMove(models.Model):
    _inherit = 'account.move'

    myr                 = fields.Float('Kurs(MYR)', compute="_compute_get_kurs")
    usd                 = fields.Float('Kurs(USD)', compute="_compute_get_kurs")

    @api.depends('name')
    def _compute_get_kurs(self):
        for rec in self:
            if rec.name != False:
                get_kurs    = self.env['account.invoice'].search([('number','=',rec.name)])

                rec.myr     = get_kurs.myr
                rec.usd     = get_kurs.usd

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    amount_myr = fields.Float('Amount Currency MYR', compute="_compute_amount_currency", digits=(20,4))
    amount_usd = fields.Float('Amount Currency USD', compute="_compute_amount_currency", digits=(20,4))

    @api.depends('account_id','credit','debit')
    def _compute_amount_currency(self):
        for rec in self:
            if rec.move_id.name != False:
                currency = self.env['account.invoice'].search([('number','=',rec.move_id.name)])

                if rec.credit == 0:
                    sign = 1
                else:
                    sign = -1

                if rec.credit == 0:
                    amount_myr = sign * (currency.invoice_line_ids.amount_myr)
                    amount_usd = sign * (currency.invoice_line_ids.amount_usd)
                else:
                    amount_myr = sign * (currency.amount_total_myr)
                    amount_usd = sign * (currency.amount_total_usd)

                rec.amount_myr = amount_myr
                rec.amount_usd = amount_usd