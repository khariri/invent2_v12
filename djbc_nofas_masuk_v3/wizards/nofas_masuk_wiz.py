from odoo import models, fields, api


class DJBCNofasMasukV3Wizard(models.TransientModel):
    _name = "djbc.nofas.masuk.v3.wizard"
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')

    @api.multi
    def call_djbc_nofas_masuk_v3(self):
        cr = self.env.cr
        cr.execute("select djbc_nofas_masuk_v3(%s,%s)",(self.date_start, self.date_end))
        waction = self.env.ref("djbc_nofas_masuk_v3.""nofas_masuk_v3_action")
        result = waction.read()[0]
        return result

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

    @api.multi
    def generate_laporan_xls(self):
        cr=self.env.cr
        cr.execute("select djbc_nofas_masuk_v3(%s,%s)",(self.date_start, self.date_end))
        data = {
            'model': 'djbc.nofas.masuk.v3.wizard',
            'form': self.read()[0]
        }
        
        return self.env.ref('djbc_nofas_masuk_v3.pemasukan_v3_xlsx').report_action(self, data=data)