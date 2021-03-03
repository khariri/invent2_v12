from odoo import models, fields, api


class DJBCNofasRusakWizard(models.TransientModel):
    _name = "djbc.nofas.rusak.wizard"
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')

    @api.multi
    def call_djbc_nofas_rusak(self):
        cr = self.env.cr
        cr.execute("select djbc_nofas_rusak(%s,%s)",(self.date_start, self.date_end))
        waction = self.env.ref("djbc_nofas_pengrusakan.""nofas_rusak_action")
        result = waction.read()[0]
        return result

    @api.multi
    def generate_laporan_pengrusakan_xls(self):
        cr=self.env.cr
        cr.execute("select djbc_nofas_rusak(%s,%s)",(self.date_start, self.date_end))
        data = {
            'model': 'djbc.nofas.rusak.wizard',
            'form': self.read()[0]
        }
        return self.env.ref('djbc_nofas_pengrusakan.pengrusakan_xlsx').report_action(self, data=data)


    @api.onchange('date_end')
    @api.multi
    def onchange_date(self):
        res={}
        if self.date_start>self.date_end:
            res = {'warning':{
                'title':('Warning'),
                'message':('Tanggal Akhir Lebih Kecil Dari Tanggal Mulai')}}
        if res:
            return res
