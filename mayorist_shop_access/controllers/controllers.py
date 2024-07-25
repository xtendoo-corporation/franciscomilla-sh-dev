from odoo import http
from odoo.http import request

class CustomShopAccess(http.Controller):

    @http.route(['/shop'], type='http', auth="public", website=True)
    def shop(self, **kw):
        current_website = request.website
        target_website_id = 12
        print("*"*50)
        print("current_website.id", current_website.id)
        print("target_website_id", target_website_id)
        if current_website.id == target_website_id:
            print("is_portal", request.env.user.has_group('base.group_portal'))
            print("is_internal", request.env.user.has_group('base.group_user'))
            if not request.env.user.has_group('base.group_portal') and not request.env.user.has_group('base.group_user'):
                return request.redirect('/web/login')
            #buscamos la tarifa mayorista
            website_sale_pricelists = request.env['product.pricelist'].sudo().search([('website_id', '=', target_website_id)])
            if website_sale_pricelists is None:
                website_sale_pricelists = []
            print("website_sale_pricelists", website_sale_pricelists)
            print("*"*50)
            return request.redirect('/shop')
