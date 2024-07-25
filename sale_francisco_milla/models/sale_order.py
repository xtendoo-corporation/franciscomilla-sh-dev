from odoo import models, fields, _, api
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    kg_price = fields.Float(string='Precio por kg', related='product_id.kg_price')
    kg_qty = fields.Float(string='kg')
    price_type = fields.Selection(
        [
            ("unit", "Por unidades"),
            ("kg", "Por kilogramos"),
        ],
        default='unit',
    )

    @api.onchange('price_type')
    def _onchange_price_type(self):
        if self.price_type == 'kg':
            if self.kg_price <= 0:
                raise UserError(_("El producto no tiene precio por kilogramo"))

            #self.price_unit = self.kg_qty * self.kg_price
            self.price_unit = self._get_price_kg_in_pricelist(self.product_id, self.order_id.pricelist_id)
        else:
            self.price_unit = self._onchange_

    @api.onchange('kg_qty')
    def _onchange_kg_qty(self):
        if self.price_type == 'kg':
            self.price_unit = self.kg_qty * self.kg_price

    def _get_price_kg_in_pricelist(self, product, pricelist):
        price = self.product_id.lst_price
        item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist.id), ('applied_on', '=', '1_product'), ('product_tmpl_id', '=', product.product_tmpl_id.id)])
        if not item:
            item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist.id), ('applied_on', '=', '0_product_variant'), ('product_id', '=', product.id)])
        if not item:
            item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist.id), ('applied_on', '=', '2_product_category'), ('categ_id', '=', product.categ_id.id)])
        if not item:
            item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist.id), ('applied_on', '=', '3_global')])

        if not item:
            return price

        # price = item._compute_price(product, self.product_uom_qty, product.uom_id, pricelist.currency_id, pricelist)
        print("pricelist_id: ", pricelist)
        print("item: ", item)
        print("price: ", price)

        return price






    def _get_price_kg_in_pricelist_item(
        self, pricelist_item, pricelist_type, product=None
    ):
        price = 0.00
        if pricelist_type == "4_analysis_group":
            product = pricelist_item.analysis_group_ids
        elif pricelist_type == "5_analytical_method":
            product = pricelist_item.analitycal_method_ids
        if pricelist_item.compute_price == "fixed":
            price = pricelist_item.fixed_price
        if pricelist_item.compute_price == "percentage":
            price = product.price - product.price * (pricelist_item.percent_price / 100)
        if pricelist_item.compute_price == "formula":
            if pricelist_item.base == "pricelist":
                if pricelist_item.base_pricelist_id:
                    parent_pricelist_item = self.env["product.pricelist.item"].search(
                        [
                            ("analysis_group_ids", "=", product.id),
                            ("pricelist_id", "=", pricelist_item.base_pricelist_id.id),
                        ],
                        limit=1,
                    )
                    if parent_pricelist_item:
                        price = self._get_price_in_pricelist_item(
                            parent_pricelist_item, parent_pricelist_item.applied_on
                        )
                    else:
                        parent_pricelist_item = self.env[
                            "product.pricelist.item"
                        ].search(
                            [
                                ("analitycal_method_ids", "=", product.id),
                                (
                                    "pricelist_id",
                                    "=",
                                    pricelist_item.base_pricelist_id.id,
                                ),
                            ],
                            limit=1,
                        )
                        if parent_pricelist_item:
                            price = self._get_price_in_pricelist_item(
                                parent_pricelist_item, parent_pricelist_item.applied_on
                            )
                        else:
                            parent_pricelist_item = self.env[
                                "product.pricelist.item"
                            ].search(
                                [
                                    ("applied_on", "=", "3_global"),
                                    (
                                        "pricelist_id",
                                        "=",
                                        pricelist_item.base_pricelist_id.id,
                                    ),
                                ],
                                limit=1,
                            )
                            price = self._get_price_in_pricelist_item(
                                parent_pricelist_item,
                                parent_pricelist_item.applied_on,
                                product,
                            )
                else:
                    price = product.price
            else:
                price = product.price
            price = (
                price
                - price * (pricelist_item.price_discount / 100)
                + pricelist_item.price_surcharge
            )
        return price
