from odoo import models
# from odoo.exceptions import UserError

class PengeluaranXlsx(models.AbstractModel):
    _name = 'report.djbc_nofas_keluar_v3.pengeluaran_v3_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        # raise UserError("yes working...")
        sheet = workbook.add_worksheet('Pengeluaran')
        format1 = workbook.add_format({'font_size':12, 'align':'center', 'bold':True})
        format2 = workbook.add_format({'font_size':12, 'align':'center'})
        sheet.merge_range('A1:N1', 'Laporan Pengeluaran', format1)
        sheet.merge_range('A2:N2', 'Periode: ' + str(data['form']['date_start']) + ' s.d. ' + str(data['form']['date_end']), format1)

        sheet.write(3,0,'No',format1)
        sheet.write(3,1,'Jenis Dokumen',format1)
        sheet.write(3,2,'Nomer Pendaftaran',format1)
        sheet.write(3,3,'Tanggal Pendaftaran',format1)
        sheet.write(3,4,'Nomer Pengeluaran',format1)
        sheet.write(3,5,'Tanggal Pengeluaran',format1)
        sheet.write(3,6,'Pengiriman Barang',format1)
        sheet.write(3,7,'Kode Barang',format1)
        sheet.write(3,8,'Nama Barang',format1)
        sheet.write(3,9,'Jumlah',format1)
        sheet.write(3,10,'Satuan',format1)
        sheet.write(3,11,'Nilai',format1)
        sheet.write(3,12,'Currency',format1)
        sheet.write(3,13,'Warehouse',format1)

        no = 1
        row = 4
        objs = self.env['djbc.nofas_keluar_v3'].search([])
        for obj in objs:
            sheet.write(row, 0, no, format2)
            sheet.write(row, 1, obj.jenis_dok, format2)
            sheet.write(row, 2, obj.no_dok, format2)
            sheet.write(row, 3, str(obj.tgl_dok), format2)
            sheet.write(row, 4, obj.no_pengeluaran.name, format2)
            sheet.write(row, 5, str(obj.tgl_pengeluaran), format2)

            sheet.write(row, 6, obj.penerima, format2)
            sheet.write(row, 7, obj.kode_barang, format2)
            sheet.write(row, 8, obj.nama_barang, format2)
            sheet.write(row, 9, obj.jumlah, format2)
            sheet.write(row, 10, obj.satuan, format2)
            sheet.write(row, 11, obj.nilai, format2)
            sheet.write(row, 12, obj.currency, format2)
            sheet.write(row, 13, obj.warehouse, format2)

            no += 1
            row += 1

        

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
        # i=2
        # lines = self.env['djbc.mutasi'].search([])
        # for obj in lines:
        #     i=i+1
        #     sheet.write(i,0,obj.kode_barang,format2)
        #     sheet.write(i,1,obj.nama_barang,format2)
        #     sheet.write(i,2,obj.saldo_awal,format2)
        #     sheet.write(i,3,obj.pemasukan,format2)
        #     sheet.write(i,4,obj.pengeluaran,format2)
        #     sheet.write(i,5,obj.penyesuaian,format2)
        #     sheet.write(i,6,obj.stock_opname,format2)
        #     sheet.write(i,7,obj.saldo_akhir,format2)
        #     sheet.write(i,8,obj.selisih,format2)
        #     sheet.write(i,9,obj.keterangan,format2)
        #     sheet.write(i,10,obj.warehouse,format2)
            
#
