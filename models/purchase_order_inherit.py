# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone
from ast import literal_eval
from markupsafe import escape, Markup
from werkzeug.urls import url_encode

from odoo import api, fields, models, _
from odoo.fields import Command, Domain
from odoo.tools import format_amount, format_date, formatLang, groupby, OrderedSet, SQL
from odoo.tools.float_utils import float_is_zero, float_repr
from odoo.exceptions import AccessDenied, UserError, ValidationError

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    partner_id = fields.Many2one(
        'res.partner', string='Vendor', change_default=True,
        tracking=True, check_company=True, index=True, required=False,
        help="You can find a vendor by its Name, TIN, Email or Internal Reference.")

    @api.constrains('partner_id')
    def _check_unique_code(self):
        for rec in self:
            if not rec.partner_id and rec.state != 'draft':
                raise ValidationError('Vui lòng chọn Nhà Cung Cấp (Vendor).')