import itertools

from odoo import api, models, fields, tools, _
from odoo.exceptions import ValidationError, RedirectWarning, UserError
from odoo.osv import expression
from odoo.tools import pycompat



class ProductTemplate(models.Model):
    _inherit = "product.template"

    _sql_constrains = [
        ('name_uniq','unique(display_name)','Product Name Already Exist!'),
        ('default_code','unique(default_code)','Internal Reference Already Exist')
    ]

    # @api.model_create_multi
    @api.model
    def create(self, values):
        display_name = values.get('name', False)
        cari_nama_barang = self.env['product.template'].search([('name','=',display_name)])
        int_reference = values.get('default_code', False)
        cari_int_reference = self.env['product.template'].search([('default_code','=',int_reference)])

        if(len(cari_nama_barang) > 0):
            raise ValidationError(
                _('Sorry, Product Name Already Exist!'))
        elif(int_reference != False and len(cari_int_reference) > 0):
            raise ValidationError(
                _('Sorry, Internal Reference Already Exist!'))

        return super(ProductTemplate, self).create(values)