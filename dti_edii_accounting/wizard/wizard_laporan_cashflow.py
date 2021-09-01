from odoo import api,fields,models,_ 
from datetime import date, time, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning
import collections
import base64
from io import BytesIO
import xlsxwriter

class DtWizardLaporanCashflow(models.TransientModel):
    _name               = "dt.wizard.laporan.cashflow"
    _description        = "Laporan Cashflow"

    company_id          = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    fiscalyear_id       = fields.Many2one('account.fiscal.year', string='Fiscal Year', ondelete='cascade')
    account_report_id   = fields.Many2one('dti.cashflow.items', string='Account Reports', required=True)
    period_id           = fields.Many2one('account.period', string="Period", ondelete='cascade')
    date_from           = fields.Date(string='Start Date')
    date_to             = fields.Date(string='End Date')
    file                = fields.Binary('File')
    is_detail           = fields.Boolean('Is Detail')
    with_movement       = fields.Boolean('With Movement Only', default=True)

    @api.onchange("period_id","fiscalyear_id")
    def onchange_period(self):
        if self.period_id :
            if  self.account_report_id.report_group == 'Balance Sheet' or self.account_report_id.report_group == 'BALANCE SHEET':
                self.date_from = self.fiscalyear_id.date_from
            else :
                self.date_from = self.period_id.date_start

            self.date_to = self.period_id.date_stop
    
    def button_download_pdf(self):
        data = {
            'company_id'        : self.company_id.id,
            'fiscalyear_id'     : self.fiscalyear_id.id,
            'period_id'         : self.period_id.id,
        }
        if self.account_report_id.name == 'NERACA':
            return self.env['report'].get_action([], 'dt_centra_accounting.report_dt_balance_sheet_pdf',data=data)
        else:
            return self.env['report'].get_action([], 'dt_centra_accounting.report_dt_profit_loss_report_pdf',data=data)


    @api.multi
    def button_download_excel(self):

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
        h1_content_format_center = workbook.add_format({'bold': 1,'valign':'vcenter', 'align':'center'})
        h1_content_format_center.set_font_size('12')
        #################################################################################
        h1_content_format_right = workbook.add_format({'bold': 1,'valign':'vcenter', 'align':'right'})
        h1_content_format_right.set_font_size('12')

        # CONTENT FORMAT
        #################################################################################
        content_format_style1 = workbook.add_format({'bold': 1,'valign':'vcenter', 'align':'left'})
        content_format_style1.set_font_size('13')
        #################################################################################
        content_format_style2 = workbook.add_format({'bold': 1,'valign':'vcenter', 'align':'left'})
        content_format_style2.set_font_size('12')
        #################################################################################
        content_format_style3 = workbook.add_format({'valign':'vcenter', 'align':'left'})
        content_format_style3.set_font_size('12')
        #################################################################################
        content_format_style4 = workbook.add_format({'valign':'vcenter', 'align':'left'})
        content_format_style4.set_font_size('12')
        #################################################################################
        
        # NUMBER
        numb_format_style1 = workbook.add_format({'bold': 1,'valign':'vcenter', 'align':'right','num_format':'#,##0'})
        numb_format_style1.set_font_size('13')
        #################################################################################
        numb_format_style2 = workbook.add_format({'bold': 1,'valign':'vcenter', 'align':'right','num_format':'#,##0'})
        numb_format_style2.set_font_size('12')
        #################################################################################
        numb_format_style3 = workbook.add_format({'valign':'vcenter', 'align':'right','num_format':'#,##0'})
        numb_format_style3.set_font_size('12')
        #################################################################################
        numb_format_style4 = workbook.add_format({'valign':'vcenter', 'align':'right','num_format':'#,##0'})
        numb_format_style4.set_font_size('12')
        
        worksheet1 = workbook.add_worksheet('All')
        worksheet1.set_column('A:A', 5)
        worksheet1.set_column('B:B', 20)
        worksheet1.set_column('C:C', 45)
        worksheet1.set_column('D:D', 20)
        worksheet1.set_column('E:E', 20)
        worksheet1.set_column('F:F', 20)

        worksheet1.merge_range('B1:F1', 'Printed by ' +  datetime.strptime(today, "%Y-%m-%d %H:%M:%S").\
                                             strftime("%Y-%m-%d %H:%M:%S") + ' by ' + self.env.user.name, left_title)
        worksheet1.merge_range('B2:F2', self.company_id.name, h1_center_title)
        worksheet1.merge_range('B3:F3', 'Cashflow Report', h1_center_title)
        worksheet1.merge_range('B4:F4', 'Period ' + self.period_id.name, center_title)
        
        row = 5
        worksheet1.write(row, 1, '', h1_content_format_center)
        worksheet1.write(row, 2, '', h1_content_format_center)
        worksheet1.write(row, 3, 'Until Prev. Period', h1_content_format_right)
        worksheet1.write(row, 4, 'This Period', h1_content_format_right)
        worksheet1.write(row, 5, 'Year to Date (YTD)', h1_content_format_right)

        row += 1

        data_report = self.env['dt.acc.global.function'].get_cashflow_report_data(self.company_id.id, self.fiscalyear_id.id, self.period_id.id, self.is_detail, self.with_movement)

        for dt in data_report:
            if dt['name'] != 'BREAK':

                if dt['style'] == 1:
                    worksheet1.write(row, 1, dt['code'] or '', content_format_style1)
                    worksheet1.write(row, 2, dt['name'], content_format_style1)
                    worksheet1.write(row, 3, dt['saldo_sd_bulan_lalu'] if dt['type'] != 'view' else '', numb_format_style1)
                    worksheet1.write(row, 4, dt['mutasi_bulan_ini'] if dt['type'] != 'view' else '', numb_format_style1)
                    worksheet1.write(row, 5, dt['saldo_sd_bulan_ini'] if dt['type'] != 'view' else '', numb_format_style1)
                elif dt['style'] == 2:
                    worksheet1.write(row, 1, dt['code'] or '', content_format_style2)
                    worksheet1.write(row, 2, dt['name'], content_format_style2)
                    worksheet1.write(row, 3, dt['saldo_sd_bulan_lalu'] if dt['type'] != 'view' else '', numb_format_style2)
                    worksheet1.write(row, 4, dt['mutasi_bulan_ini'] if dt['type'] != 'view' else '', numb_format_style2)
                    worksheet1.write(row, 5, dt['saldo_sd_bulan_ini'] if dt['type'] != 'view' else '', numb_format_style2)
                elif dt['style'] == 3:
                    worksheet1.write(row, 1, dt['code'] or '', content_format_style3)
                    worksheet1.write(row, 2, dt['name'], content_format_style3)
                    worksheet1.write(row, 3, dt['saldo_sd_bulan_lalu'] if dt['type'] != 'view' else '', numb_format_style3)
                    worksheet1.write(row, 4, dt['mutasi_bulan_ini'] if dt['type'] != 'view' else '', numb_format_style3)
                    worksheet1.write(row, 5, dt['saldo_sd_bulan_ini'] if dt['type'] != 'view' else '', numb_format_style3)
                else:
                    worksheet1.write(row, 1, dt['code'] or '', content_format_style4)
                    worksheet1.write(row, 2, dt['name'], content_format_style4)
                    worksheet1.write(row, 3, dt['saldo_sd_bulan_lalu'] if dt['type'] != 'view' else '', numb_format_style4)
                    worksheet1.write(row, 4, dt['mutasi_bulan_ini'] if dt['type'] != 'view' else '', numb_format_style4)
                    worksheet1.write(row, 5, dt['saldo_sd_bulan_ini'] if dt['type'] != 'view' else '', numb_format_style4)
            row += 1

        workbook.close()
        file=base64.encodestring(fp.getvalue())
        self.write({'file':file})
        fp.close()
        
        return{
            'type' : 'ir.actions.act_url',
            'url': 'web/content/?model=dt.wizard.laporan.cashflow&field=file&download=true&id=%s&filename=CashflowReport.xlsx'%(self.id),
            'target': 'new',
        }