from odoo import models


class PemusnahanXlsx(models.AbstractModel):
    _name = 'report.djbc.pemusnahan_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('Pemusnahan')
        format1 = workbook.add_format({'font_size':12, 'align':'vcenter', 'bold':True})
        format2 = workbook.add_format({'font_size':12, 'align':'vcenter'})
        sheet.write(0,0,'Laporan Pemusnahan Barang', format1)
        sheet.write(1,0,'Periode:' + str(data['form']['date_start']) + ' s.d ' + str(data['form']['date_end']), format1)
        sheet.write(2,0,'No', format1)
        sheet.write(2,1,'Nomor Pemusnahan', format1)
        sheet.write(2,2,'Tanggal Pemusnahan', format1)
        sheet.write(2,3,'Kode Barang', format1)
        sheet.write(2,4,'Nama Barang', format1)
        sheet.write(2,5,'Jumlah', format1)
        sheet.write(2,6,'Satuan', format1)
        i=2
        no=0
        lines = self.env['djbc.nofas_musnah'].search([])
        for obj in lines:
            i=i+1
            no=no+1
            sheet.write(i,0,no,format2)
            sheet.write(i,1,no_pemusnahan,format2)
            sheet.write(i,2,tgl_pemusnahan,format2)
            sheet.write(i,3,obj.kode_barang,format2)
            sheet.write(i,4,obj.nama_barang,format2)
            sheet.write(i,5,obj.jumlah,format2)
            sheet.write(i,6,obj.satuan,format2)