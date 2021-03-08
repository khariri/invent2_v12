from odoo import models


class PengrusakanXlsx(models.AbstractModel):
    _name = 'report.djbc_nofas_pengrusakan.pengrusakan_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('Pengrusakan')
        format1 = workbook.add_format({'font_name':'Arial', 'font_size':12, 'align':'center', 'bold':True})
        format2 = workbook.add_format({'font_name':'Arial', 'font_size':12, 'align':'center'})
        sheet.merge_range('A1:G1', 'Laporan Pengrusakan', format1)
        sheet.merge_range('A2:G2', 'Periode :' + str(data['form']['date_start']) + ' s.d ' + str(data['form']['date_end']), format1)
        
        sheet.write(3,0,'No',format1)
        sheet.write(3,1,'Nomor Pengrusakan',format1)
        sheet.write(3,2,'Tanggal Pengrusakan',format1)
        sheet.write(3,3,'Kode Barang',format1)
        sheet.write(3,4,'Nama Barang',format1)
        sheet.write(3,5,'Jumlah',format1)
        sheet.write(3,6,'Satuan',format1)
        i=3
        no=0
        lines = self.env['djbc.nofas_rusak'].search([])
        for obj in lines:
            i=i+1
            no=no+1
            sheet.write(i,0,no,format2)
            sheet.write(i,1,obj.no_pengrusakan,format2)
            sheet.write(i,2,str(obj.tgl_pengrusakan),format2)
            sheet.write(i,3,obj.kode_barang,format2)
            sheet.write(i,4,obj.nama_barang,format2)
            sheet.write(i,5,obj.jumlah,format2)
            sheet.write(i,6,obj.satuan,format2)

