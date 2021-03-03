from odoo import models, fields, api


class DJBCNofasMusnahWizard(models.TransientModel):
    _name = "djbc.nofas.musnah.wizard"
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')

    @api.multi
    def call_djbc_nofas_musnah(self):
        cr = self.env.cr
        cr.execute("select djbc_nofas_musnah(%s,%s)",(self.date_start, self.date_end))
        waction = self.env.ref("djbc_nofas_pemusnahan.""nofas_musnah_action")
        result = waction.read()[0]
        return result

    @api.multi
    def generate_laporan_pemusnahan_xls(self):
        cr=self.env.cr
        cr.execute("select djbc_nofas_musnah(%s,%s)", (self.date_start, self.date_end))
        data = {
            'model': 'djbc.nofas.musnah.wizard',
            'form': self.read()[0]
        }
        return self.env.ref('djbc_nofas_pemusnahan.pemusnahan_xlsx').report_action(self, data=data)
        
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
