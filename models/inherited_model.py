from odoo import fields, models

class InheritedModel(models.Model):
    # Inherit the 'res.users' model to add custom fields specific to users
    _inherit = 'res.users'

    property_ids=fields.One2many("estate.property","salesperson_id", string="Properties of Salesman",
                                 domain=[('state', 'in', ['new', 'offer_received'])])


