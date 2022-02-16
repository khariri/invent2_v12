from odoo import models
from odoo.exceptions import UserError

class PemasukanXlsx(models.AbstractModel):
    _name = 'report.djbc_lap_plb_masuk.pemasukan_plb_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        # raise UserError("yes working...")
        sheet = workbook.add_worksheet('Pemasukan')
        format1 = workbook.add_format({'font_size':12, 'align':'center', 'bold':True})
        format2 = workbook.add_format({'font_size':12, 'align':'center'})
        sheet.merge_range('A1:N1', 'Laporan Pemasukan', format1)
        sheet.merge_range('A2:N2', 'Periode: ' + str(data['form']['date_start']) + ' s.d. ' + str(data['form']['date_end']), format1)

        sheet.write(3,0,'No',format1)
        sheet.write(3,1,'Jenis Dokumen',format1)
        sheet.write(3,2,'Nomer Pendaftaran',format1)
        sheet.write(3,3,'Tanggal Pendaftaran',format1)
        sheet.write(3,4,'Nomer Penerimaan',format1)
        sheet.write(3,5,'Tanggal Penerimaan',format1)
        sheet.write(3,6,'Pengiriman Barang',format1)
        sheet.write(3,7,'Pemilik Barang',format1)
        sheet.write(3,8,'Kode Barang',format1)
        sheet.write(3,9,'Nama Barang',format1)
        sheet.write(3,10,'Jumlah',format1)
        sheet.write(3,11,'Satuan',format1)
        sheet.write(3,12,'Nilai',format1)
        sheet.write(3,13,'Currency',format1)
        sheet.write(3,14,'Warehouse',format1)

        no = 1
        row = 4
        lines = self.env['djbc.lap_plb_masuk'].search([])
        for obj in lines:
            if obj.pemilik:
                pemilik = obj.pemilik
            else:
                pemilik = " "
            sheet.write(row, 0, no, format2)
            sheet.write(row, 1, obj.jenis_dok, format2)
            sheet.write(row, 2, obj.no_dok, format2)
            sheet.write(row, 3, str(obj.tgl_dok), format2)
            sheet.write(row, 4, obj.no_penerimaan.name, format2)
            sheet.write(row, 5, str(obj.tgl_penerimaan), format2)

            sheet.write(row, 6, obj.pengirim, format2)
            sheet.write(row, 7, pemilik, format2)
            sheet.write(row, 8, obj.kode_barang, format2)
            sheet.write(row, 9, obj.nama_barang, format2)
            sheet.write(row, 10, obj.jumlah, format2)
            sheet.write(row, 11, obj.satuan, format2)
            sheet.write(row, 12, obj.nilai, format2)
            sheet.write(row, 13, obj.currency, format2)
            sheet.write(row, 14, obj.warehouse, format2)

            no = no+1
            row = row+1

        # set lebar kolom
        # sheet.set_column('B:D', 21)
        # sheet.set_column('E:F', 18)
        # sheet.set_column('G:G', 20)
        # sheet.set_column('H:H', 15)
        # sheet.set_column('I:I', 15)
        # sheet.set_column('J:J', 10)
        # sheet.set_column('K:K', 15)

        # sheet.merge_range('A3:A4', 'No', format1)
        # sheet.merge_range('B3:D3', 'Dokumen Pabean', format1)
        # sheet.merge_range('E3:F3', 'Bukti Penerimaan Barang', format1)
        # sheet.write(3,1,'Type',format1)
        # sheet.write(3,2,'Nomer',format1)
        # sheet.write(3,3,'Tanggal',format1)
        # sheet.write(3,4,'Nomer',format1)
        # sheet.write(3,5,'Tanggal',format1)
        # sheet.merge_range('G3:G4', 'Pengiriman Barang', format1)
        # sheet.merge_range('H3:H4', 'Kode Barang', format1)
        # sheet.merge_range('I3:I4', 'Jumlah', format1)
        # sheet.merge_range('J3:J4', 'Sat', format1)
        # sheet.merge_range('K3:K4', 'Jumlah', format1)

        

        # i=4
        # lines = self.env['djbc.nofas_masuk'].search([])
        # for obj in lines:
        #     i=i+1
        #     sheet.write(i,1,'test',format2)
