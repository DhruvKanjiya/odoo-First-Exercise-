from odoo import models, fields
class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Property Type'
    _order = "sequence,name"

    name=fields.Char(string="Property Type", required=True)
    sequence=fields.Integer(string="Sequence")
    property_ids=fields.One2many("estate.property","property_type_id",string="Properties")
    offer_ids=fields.One2many("estate.property.offer","property_type_id",string="Offers")
    offer_count=fields.Integer(string="Offer Count", compute="_compute_offer_count")

    _sql_constraints = [
        ('unique_property_type_name',
         'UNIQUE(name)',
         'The property type name must be unique!')
    ]

    def _compute_offer_count(self):
        """
            **Description:**
            - This method calculates the number of offers (`offer_ids`) linked to a record.
            - It updates the `offer_count` field with the total count of related offers.

            **Arguments:**
            - `self`: Represents the current record(s) being processed.

            **Returns:**
            - None: This method does not return a value but updates the `offer_count` field for each record.
            """
        for record in self:
            record.offer_count = len(record.offer_ids)

