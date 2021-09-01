from odoo import api, fields, models, _
from datetime import date, time, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning
import collections
import base64
from io import BytesIO
import xlsxwriter

class DtWizardGeneralLedgerReport(models.TransientModel):
    _name = 'dt.wizard.general.ledger.report'

    fiscal_year_id          = fields.Many2one('account.fiscal.year', 'Fiscal Year', required=False)
    period_id               = fields.Many2one('account.period', 'Period', required=False)
    customize_date          = fields.Boolean('Custom Date Range')
    start_date              = fields.Date('Start Date')
    end_date                = fields.Date('End Date')
    company_id              = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    account_id              = fields.Many2one('account.account','Account', required=False)
    start_account_id        = fields.Many2one('account.account','From Account', required=True)
    end_account_id          = fields.Many2one('account.account','To Account', required=True)
    file                    = fields.Binary('File')

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

    @api.onchange('start_account_id')
    def onchange_account_id(self):
        if self.start_account_id:
            self.end_account_id = self.start_account_id.id
            result = {}
            domain = [
                ('company_id.id', '=', self.company_id.id)
            ]
            result['domain'] = {'end_account_id': domain}
            return result

        else:
            self.end_account_id = False
            result = {}
            return result

    def generate_report_pdf(self):
        template = 'dt_centra_accounting.report_dt_general_ledger_report_pdf'
        report = self.env['ir.actions.report']._get_report_from_name(template)

        domain = {
            'period_id'         : self.period_id.id,
            'start_date'        : self.start_date,
            'end_date'          : self.end_date,
            'start_account_id'  : self.start_account_id.id,
            'end_account_id'    : self.end_account_id.id,
        }
        values = {
            'ids'       : self.ids,
            'model'     : report.model,
            'form'      : domain
        }
        return self.env.ref('dt_centra_accounting.report_dt_wizard_general_ledger_report_pdf').report_action(self, data=values)

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
        title_left = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'left'})
        title_left.set_font_size('13')
        #################################################################################
        h1_header_table = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'left'})
        h1_header_table.set_font_size('16')
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
        worksheet1.set_column('B:B', 20)
        worksheet1.set_column('C:C', 75)
        worksheet1.set_column('D:D', 15)
        worksheet1.set_column('E:E', 30)
        worksheet1.set_column('F:F', 25)
        worksheet1.set_column('G:G', 25)
        worksheet1.set_column('H:H', 17)
        worksheet1.set_column('I:I', 17)
        worksheet1.set_column('J:J', 20)

        worksheet1.merge_range('A1:J1', 'Printed by ' +  datetime.strptime(today, "%Y-%m-%d %H:%M:%S").\
                                             strftime("%Y-%m-%d %H:%M:%S") + ' by ' + self.env.user.name, left_title)
        worksheet1.merge_range('A2:J2', self.env.user.company_id.name, h1_center_title)
        worksheet1.merge_range('A3:J3', 'LAPORAN BUKU BESAR', h1_center_title)
        worksheet1.merge_range('A4:J4', 'PERIOD ' + self.period_id.name + ' (' + self.start_date.strftime("%d-%m-%Y") + ' ' + ' until ' + ' ' + self.end_date.strftime("%d-%m-%Y") + ')', center_title)
        worksheet1.merge_range('A6:B6', 'Account (COA)', title_left)
        worksheet1.merge_range('C6:E6', ':' + ' (' + str(self.start_account_id.code) + ') ' + str(self.start_account_id.name) + ' - ' + '(' + str(self.end_account_id.code) + ')' + ' ' + str(self.end_account_id.name), title_left)
        i = 8

        data_report = self.env['dt.acc.global.function'].get_general_ledger_report_data(self.period_id.id, self.start_date, self.end_date, self.start_account_id.id, self.end_account_id.id)

        for coa in data_report:
            if data_report:
                merge = 'A' + str(i + 1) + ':' + 'C' + str(i + 1)

                worksheet1.merge_range(merge,'Account : ' + coa['account'], h1_header_table)
                i = i + 1
                worksheet1.write(i, 0, 'Tanggal', header_table)
                worksheet1.write(i, 1, 'No. Invoice', header_table)
                worksheet1.write(i, 2, 'Uraian', header_table)
                worksheet1.write(i, 3, '', header_table)
                worksheet1.write(i, 4, 'Debit', header_table)
                worksheet1.write(i, 5, 'Credit', header_table)
                worksheet1.write(i, 6, 'Saldo', header_table)
                worksheet1.write(i, 7, 'MYR', header_table)
                worksheet1.write(i, 8, 'USD', header_table)
                i = i + 1

                for data in coa['mutasi']:
                    worksheet1.write(i, 0, str(data['date'].strftime("%d-%m-%Y")), set_border)
                    worksheet1.write(i, 1, data['voucher_no'], set_border)
                    worksheet1.write(i, 2, data['label'], set_border)
                    worksheet1.write(i, 3, '', set_border)
                    worksheet1.write(i, 4, data['debit'], numb_format_border)
                    worksheet1.write(i, 5, data['credit'], numb_format_border)
                    worksheet1.write(i, 6, data['saldo'], numb_format_border)
                    worksheet1.write(i, 7, data['myr'], numb_format_border)
                    worksheet1.write(i, 8, data['usd'], numb_format_border)
                    i += 1

                worksheet1.write(i, 3, coa['t_saldo_awal'], numb_format)
                worksheet1.write(i, 4, coa['t_debit'], numb_format)
                worksheet1.write(i, 5, coa['t_credit'], numb_format)
                worksheet1.write(i, 6, coa['t_saldo'], numb_format)
                worksheet1.write(i, 7, coa['t_myr'], numb_format)
                worksheet1.write(i, 8, coa['t_usd'], numb_format)

                i += 1

        workbook.close()
        file=base64.encodestring(fp.getvalue())
        self.write({'file':file})
        fp.close()
        
        return{
            'type' : 'ir.actions.act_url',
            'url': 'web/content/?model=dt.wizard.general.ledger.report&field=file&download=true&id=%s&filename=GeneralLedger.xlsx'%(self.id),
            'target': 'new',
        }


