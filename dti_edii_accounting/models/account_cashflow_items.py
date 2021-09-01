from odoo import api, exceptions, fields, models, _
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, pycompat, date_utils
from odoo.tools.misc import formatLang
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.addons import decimal_precision as dp

class DtiCashFlowItems(models.Model):
    _name = 'dti.cashflow.items'

    name                = fields.Char('Report Name')
    sequence            = fields.Integer('Sequence')
    sign                = fields.Selection([('-1', 'Reverse Balance Sign'),
                                            ('1','Preserve Balance Sign')])
    is_breakline        = fields.Boolean('Breakline')
    side                = fields.Selection([('left','Left'),
                                            ('right','Right')])
    report_group        = fields.Selection([('cashflow','Cashflow')])
    use_formula         = fields.Boolean('Use Formula')
    parent_id           = fields.Many2one('dti.cashflow.items', 'Parent')
    type                = fields.Selection([('sum','View'),
                                            ('accounts','Accounts'),
                                            ('account_type','Account Type'),
                                            ('account_report','Report Value')])
    style_overwrite     = fields.Selection([('0','Automatic Formatting'),
                                            ('1','Main Title 1 (bold, underlined)'),
                                            ('2','Title 2 (bold)'),
                                            ('3','Title 3 (bold, smaller)'),
                                            ('4','Normal Text'),
                                            ('5','Italic Text (smaller)'),
                                            ('6','Smallest Text')])
    addition_ids        = fields.Many2many('dti.cashflow.items', 'account_report_addition_rel', 'account_id' , 'account2_id', string='Addition Account(s)')
    deduction_ids       = fields.Many2many('dti.cashflow.items', 'account_report_dedcuation_rel', 'account_id' , 'account2_id', string='Deduction Account(s)')
    code_number         = fields.Char('Code Number')
    company_id          = fields.Many2one('res.company', 'Company')
    display_detail      = fields.Selection([('no_detail','No Detail'),
                                            ('detail_flat', 'Display Children Flat'),
                                            ('detail_with_hierarchy','Display Children With Hierarchy')])
    account_report_id   = fields.Many2one('dti.cashflow.items','Report Value')
    account_ids         = fields.Many2many('account.account')
    account_type_ids    = fields.Many2many('account.account.type')
