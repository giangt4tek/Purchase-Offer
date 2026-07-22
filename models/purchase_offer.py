from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PurchaseOffer(models.Model):
    _name = 'purchase.offer'
    _description = 'Purchase Offer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Offer Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    requester_id = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user, required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', tracking=True, required=True, help="Vendor is required before creating a Purchase Order.")
    date_offer = fields.Datetime(string='Offer Date', default=fields.Datetime.now, required=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('confirmed', 'Confirmed'),
        ('po_created', 'PO Created'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, default='draft', tracking=True)

    offer_line_ids = fields.One2many('purchase.offer.line', 'offer_id', string='Products')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', readonly=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.offer') or _('New')
        return super(PurchaseOffer, self).create(vals_list)

    def _approval_allowed(self):
        self.ensure_one()
        company = self.company_id or self.env.company
        return (
            not company.offer_approval_required
            or self.env.user.has_group('purchase_offer.group_purchase_offer_manager')
        )

    def action_submit(self):
        for rec in self:
            if rec._approval_allowed():
                rec.action_confirm()
            else:
                rec.state = 'to_approve'

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_create_po(self):
        for rec in self:
            if not rec.partner_id:
                raise UserError(_('You must select a Vendor before creating a Purchase Order.'))
            if not rec.offer_line_ids:
                raise UserError(_('You must add at least one product before creating a Purchase Order.'))

            po_vals = {
                'partner_id': rec.partner_id.id,
                'origin': rec.name,
                'order_line': []
            }

            for line in rec.offer_line_ids:
                po_vals['order_line'].append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'product_qty': line.product_qty,
                    'product_uom_id': line.product_uom_id.id,
                    'date_planned': fields.Datetime.now(),
                    # price_unit will be recomputed by Odoo's standard onchanges if not provided
                }))

            po = self.env['purchase.order'].create(po_vals)
            rec.purchase_order_id = po.id
            rec.state = 'po_created'

    def action_view_po(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': self.purchase_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class PurchaseOfferLine(models.Model):
    _name = 'purchase.offer.line'
    _description = 'Purchase Offer Line'

    offer_id = fields.Many2one('purchase.offer', string='Offer Reference', index=True, required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Text(string='Description', required=True)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.product_uom_id = getattr(self.product_id, 'uom_po_id', self.product_id.uom_id).id
