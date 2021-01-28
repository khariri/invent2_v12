import itertools

from odoo import api, models, fields, tools, _
from odoo.exceptions import ValidationError, RedirectWarning, UserError
from odoo.osv import expression
from odoo.tools import pycompat



class ProductTemplate(models.Model):
    _inherit = "product.template"

    _sql_constrains = [
        ('name_uniq','unique(display_name)','Product Name Already Exist!')
    ]

    # @api.model_create_multi
    @api.model
    def create(self, values):
        display_name = values.get('name', False)
        cari_nama_barang = self.env['product.template'].search([('name','=',display_name)])
        if(len(cari_nama_barang) > 0):
            raise ValidationError(
                _('Sorry, Product Name Already Exist!'))
        
        return super(ProductTemplate, self).create(values)