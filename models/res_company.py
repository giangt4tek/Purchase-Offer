from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    offer_approval_required = fields.Boolean(
        string="Require Offer Approval", 
        default=False,
        help="If checked, purchase offers will require manager approval before they can be confirmed."
    )
