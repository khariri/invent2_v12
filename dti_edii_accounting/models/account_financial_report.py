from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning

class AccountFinancialReport(models.Model) :
    _inherit = 'account.financial.report'

    side                = fields.Selection([('left','Left'),('right','Right')],string='Side',help="Used in account financial report horizontal",default='left')
    code_number         = fields.Char('Code Number')
    company_id          = fields.Many2one('res.company','Company')
    is_breakline        = fields.Boolean('Breakline')
    report_group        = fields.Selection([('Balance Sheet','Balance Sheet'), ('Profit and Loss','Profit and Loss')], string='Report Group')
    balance_sheet_type  = fields.Selection([
        ('Aktiva','Assets'),
        ('Liabilitas','Liability'),
        ('Ekuitas','Equity'),
        ],string='Balance Sheet Category')

    use_formula         = fields.Boolean('Use Formula')
    addition_ids        = fields.Many2many('account.financial.report', 'account_report_addition_rel', 'account_id' , 'account2_id', string='Addition Account(s)')
    deduction_ids       = fields.Many2many('account.financial.report', 'account_report_dedcuation_rel', 'account_id' , 'account2_id', string='Deduction Account(s)')
