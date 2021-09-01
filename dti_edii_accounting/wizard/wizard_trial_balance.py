from odoo import api,fields,models,_ 
from datetime import date, time, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning
import collections
import base64
from io import BytesIO
import xlsxwriter

class DtWizardTrialBalanceReport(models.TransientModel):
    _name = 'dt.wizard.trial.balance.report'

    fiscal_year_id  = fields.Many2one('account.fiscal.year', 'Fiscal Year', required=False)
    period_id       = fields.Many2one('account.period', 'Period', required=False)
    customize_date  = fields.Boolean('Custom Date Range')
    start_date      = fields.Date('Start Date')
    end_date        = fields.Date('End Date')
    company_id      = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    account_id      = fields.Many2one('account.account','Account', required=False)
    file            = fields.Binary('File')

    @api.onchange('fiscal_year_id')
    def onchange_fiscal_year(self):
        self.period_id = False
        self.start_date = False
        self.end_date = False
        result = {}
        if self.fiscal_year_id:
            result['domain'] = {'period_id': [('fiscalyear_id.id', '=', self.fiscal_year_id.id)]}
        return result

    @api.onchange('period_id')
    def onchange_period_id(self):
        result = {}
        if self.period_id:
            self.start_date = self.period_id.date_start
            self.end_date = self.period_id.date_stop

    def generate_report_pdf(self):
        template = 'dt_centra_accounting.report_dt_trial_balance_report_pdf'
        report = self.env['ir.actions.report']._get_report_from_name(template)

        domain = {
            'period_id'         : self.period_id.id,
            'start_date'        : self.start_date,
            'end_date'          : self.end_date,
            'account_id'        : self.account_id.id,
        }
        values = {
            'ids'       : self.ids,
            'model'     : report.model,
            'form'      : domain
        }
        return self.env.ref('dt_centra_accounting.report_dt_wizard_trial_balance_report_pdf_id').report_action(self, data=values)

    def generate_report_excel(self):
        
        today = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        #################################################################################
        h1_center_title = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'center'})
        h1_center_title.set_font_size('16')
        #################################################################################
        left_title = workbook.add_format({'valign':'vcenter', 'align':'left'})
        left_title.set_font_size('13')
        #################################################################################
        center_title = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'center'})
        center_title.set_font_size('13')
        #################################################################################
        header_table = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'center', 'color':'white'})
        header_table.set_font_size('13')
        header_table.set_bg_color('#337AB7')
        header_table.set_border()
        #################################################################################
        set_border = workbook.add_format({'valign':'vcenter', 'align':'left'})
        set_border.set_font_size('11')
        set_border.set_border()
        #################################################################################
        center_border = workbook.add_format({'valign':'vcenter', 'align':'center'})
        center_border.set_font_size('11')
        center_border.set_border()
        #################################################################################
        numb_format_border = workbook.add_format({'valign':'vcenter', 'align':'right','num_format':'#,##0'})
        numb_format_border.set_font_size('11')
        numb_format_border.set_border()
        #################################################################################
        numb_format = workbook.add_format({'bold': 1,'valign':'vcenter', 'align':'right','num_format':'#,##0'})
        numb_format.set_font_size('11')
        #################################################################################
        no_border = workbook.add_format({'bold': 1,'valign':'vcenter', 'align':'right'})
        no_border.set_font_size('11')
        
        worksheet1 = workbook.add_worksheet('All')

        worksheet1.set_column('A:A', 13)
        worksheet1.set_column('B:B', 45)
        worksheet1.set_column('C:C', 20)
        worksheet1.set_column('D:D', 20)
        worksheet1.set_column('E:E', 20)
        worksheet1.set_column('F:F', 20)

        worksheet1.merge_range('A1:H1', 'Printed by ' +  datetime.strptime(today, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S") + ' by ' + self.env.user.name, left_title)
        worksheet1.merge_range('A2:H2', self.env.user.company_id.name, h1_center_title)
        worksheet1.merge_range('A3:H3', 'LAPORAN TRIAL BALANCE', h1_center_title)
        worksheet1.merge_range('A4:H4', 'PERIOD ' + self.period_id.name + ' (' + self.start_date.strftime("%d-%m-%Y") + ' ' + ' until ' + ' ' + self.end_date.strftime("%d-%m-%Y") + ')', center_title)


        worksheet1.merge_range('A5:A6', 'Kode COA', header_table)
        worksheet1.merge_range('B5:B6', 'Nama COA', header_table)
        worksheet1.merge_range('C5:C6', 'Saldo Awal', header_table)
        worksheet1.merge_range('D5:E5', 'Mutasi', header_table)
        worksheet1.write(5, 3, 'Debit', header_table)
        worksheet1.write(5, 4, 'Credit', header_table)
        worksheet1.merge_range('F5:F6', 'Saldo Akhir', header_table)
        worksheet1.merge_range('G5:G6', 'MYR', header_table)
        worksheet1.merge_range('H5:H6', 'USD', header_table)
        i = 6

        data_report = self.env['dt.acc.global.function'].get_trial_balance_report_data(self.period_id.id, self.start_date, self.end_date, self.account_id.id)

        for line in data_report:
            worksheet1.write(i, 0, line['code'], set_border)
            worksheet1.write(i, 1, line['account_id'], set_border)
            worksheet1.write(i, 2, line['saldo_awal'], numb_format_border)
            worksheet1.write(i, 3, line['debit'], numb_format_border)
            worksheet1.write(i, 4, line['credit'], numb_format_border)
            worksheet1.write(i, 5, line['saldo_akhir'], numb_format_border)
            worksheet1.write(i, 6, line['myr'], numb_format_border)
            worksheet1.write(i, 7, line['usd'], numb_format_border)
            i += 1

        worksheet1.write(i, 2, sum(line['saldo_awal'] for line in data_report), numb_format)
        worksheet1.write(i, 3, sum(line['debit'] for line in data_report), numb_format)
        worksheet1.write(i, 4, sum(line['credit'] for line in data_report), numb_format)
        worksheet1.write(i, 5, sum(line['saldo_akhir'] for line in data_report), numb_format)
        worksheet1.write(i, 6, sum(line['myr'] for line in data_report), numb_format)
        worksheet1.write(i, 7, sum(line['usd'] for line in data_report), numb_format)
        i += 1

        workbook.close()
        file=base64.encodestring(fp.getvalue())
        self.write({'file':file})
        fp.close()
        
        return{
            'type' : 'ir.actions.act_url',
            'url': 'web/content/?model=dt.wizard.trial.balance.report&field=file&download=true&id=%s&filename=TrialBalance.xlsx'%(self.id),
            'target': 'new',
        }

