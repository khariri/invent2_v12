from odoo import api, exceptions, fields, models, _
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, pycompat, date_utils
from odoo.tools.misc import formatLang
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.addons import decimal_precision as dp

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    myr                 = fields.Float('Kurs(MYR)', compute="_compute_kurs")
    usd                 = fields.Float('Kurs(USD)', compute="_compute_kurs")
    amount_untaxed_myr  = fields.Float('Untaxed Amount in MYR', compute="_compute_amount_untaxed_kurs", store=True, digits=(20,4))
    amount_untaxed_usd  = fields.Float('Untaxed Amount in USD', compute="_compute_amount_untaxed_kurs", store=True, digits=(20,4))
    amount_tax_myr      = fields.Float('Tax in MYR', compute="_compute_amount_tax_kurs", store=True, digits=(20,4))
    amount_tax_usd      = fields.Float('Tax in USD', compute="_compute_amount_tax_kurs", store=True, digits=(20,4))
    amount_total_myr    = fields.Float('Total in MYR', compute="_compute_amount_total_kurs", store=True, digits=(20,4))
    amount_total_usd    = fields.Float('Total in USD', compute="_compute_amount_total_kurs", store=True, digits=(20,4))

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        for rec in self.invoice_line_ids:
            if self.currency_id:
                rec.amount_usd = 0
                rec.amount_myr = 0
                rec.price_unit = 0
                rec.price_subtotal = 0

    @api.depends('amount_untaxed_myr', 'amount_tax_myr')
    def _compute_amount_total_kurs(self):
        for rec in self:
            rec.amount_total_myr = rec.amount_untaxed_myr + rec.amount_tax_myr
            rec.amount_total_usd = rec.amount_untaxed_usd + rec.amount_tax_usd

    @api.depends('invoice_line_ids.invoice_line_tax_ids')
    def _compute_amount_tax_kurs(self):
        for rec in self:
            amount_tax_myr  = sum(t.amount_myr for t in rec.invoice_line_ids)
            amount_tax_usd  = sum(t.amount_usd for t in rec.invoice_line_ids)
            for line in rec.invoice_line_ids:
                rec.amount_tax_myr = amount_tax_myr * line.invoice_line_tax_ids.amount / 100
                rec.amount_tax_usd = amount_tax_usd * line.invoice_line_tax_ids.amount / 100

    @api.depends('invoice_line_ids.amount_myr', 'invoice_line_ids.amount_usd', 'invoice_line_ids')
    def _compute_amount_untaxed_kurs(self):
        for rec in self:
            rec.amount_untaxed_myr = sum(t.amount_myr for t in rec.invoice_line_ids)
            rec.amount_untaxed_usd = sum(t.amount_usd for t in rec.invoice_line_ids)

    @api.depends('partner_id')
    def _compute_kurs(self):
        for rec in self:
            myr = self.env['res.currency'].search(['|',('name','=','MYR'),('symbol','=','RM')], limit=1, order='id desc')
            usd = self.env['res.currency'].search(['|',('name','=','USD'),('symbol','=','$')], limit=1, order='id desc')

            rec.myr = myr.rate
            rec.usd = usd.rate

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    price_subtotal  = fields.Float('Amount IDR', compute="_compute_amount_kurs", store=True)
    amount_myr      = fields.Float('Amount MYR', compute="_compute_amount_kurs", store=True, digits=(20,4))
    amount_usd      = fields.Float('Amount USD', compute="_compute_amount_kurs", store=True, digits=(20,4))

    @api.depends('invoice_id.myr', 'invoice_id.usd', 'invoice_id.currency_id')
    def _compute_amount_kurs(self):
        for rec in self:
            if rec.invoice_id.currency_id.name == 'IDR' or rec.invoice_id.currency_id.symbol == 'Rp':
                rec.price_subtotal  = rec.quantity * rec.price_unit
                rec.amount_myr      = rec.quantity * rec.price_unit / rec.invoice_id.myr
                rec.amount_usd      = rec.quantity * rec.price_unit / rec.invoice_id.usd
            elif rec.invoice_id.currency_id.name == 'USD' or rec.invoice_id.currency_id.symbol == '$':
                rec.price_subtotal  = rec.quantity * rec.price_unit * rec.invoice_id.usd
                rec.amount_myr      = rec.price_subtotal / rec.invoice_id.myr
                rec.amount_usd      = rec.quantity * rec.price_unit
            elif rec.invoice_id.currency_id.name == 'MYR' or rec.invoice_id.currency_id.symbol == 'RM':
                rec.price_subtotal  = rec.quantity * rec.price_unit * rec.invoice_id.myr
                rec.amount_myr      = rec.quantity * rec.price_unit
                rec.amount_usd      = rec.price_subtotal / rec.invoice_id.usd