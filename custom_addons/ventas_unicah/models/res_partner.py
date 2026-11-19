from odoo import fields, models

CANALES_VENTA = [
    ("tienda", "Tienda"),
    ("telefono", "Teléfono"),
    ("web", "Sitio web"),
    ("distribuidor", "Distribuidor"),
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    canal_preferido = fields.Selection(
        CANALES_VENTA,
        string="Canal preferido",
        help="Canal por el que este cliente suele comprar.",
    )
