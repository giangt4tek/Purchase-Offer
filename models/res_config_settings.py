from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    offer_approval_required = fields.Boolean(
        related='company_id.offer_approval_required',
        string="Require Offer Approval",
        readonly=False)
