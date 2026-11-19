from odoo import api, fields, models
from .res_partner import CANALES_VENTA

MONTO_APROBACION = 50000


class SaleOrder(models.Model):
    _inherit = "sale.order"

    canal_venta = fields.Selection(
        CANALES_VENTA,
        string="Canal de venta",
        compute="_compute_canal_venta",
        store=True,
        readonly=False,
    )
    total_unidades = fields.Float(
        string="Total de unidades", compute="_compute_total_unidades", store=True,
    )
    requiere_aprobacion = fields.Boolean(
        string="Requiere aprobación", compute="_compute_requiere_aprobacion", store=True,
    )

    @api.depends("partner_id")
    def _compute_canal_venta(self):
        for order in self:
            order.canal_venta = order.partner_id.canal_preferido

    @api.depends("order_line.product_uom_qty")
    def _compute_total_unidades(self):
        for order in self:
            order.total_unidades = sum(order.order_line.mapped("product_uom_qty"))

    @api.depends("amount_total")
    def _compute_requiere_aprobacion(self):
        for order in self:
            order.requiere_aprobacion = order.amount_total > MONTO_APROBACION
