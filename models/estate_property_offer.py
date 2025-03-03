
from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import UserError



class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    price= fields.Float(string="Price", required=True)
    status = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused')] , string="Status"  )
    partner_id = fields.Many2one("res.partner",string="Partner" , required=True)
    property_id=fields.Many2one("estate.property" , string="Property" , required=True)
    validity=fields.Integer(string="Validity (days)", default=7)
    date_deadline=fields.Date(string="Deadline",compute='_compute_date_deadline', inverse='_inverse_date_deadline', store=True)
    property_type_id = fields.Many2one("estate.property.type", string="Property Type",
                                       related="property_id.property_type_id", store=True)


    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        """Description :
           #           Computes the deadline date based on the creation date and validity period.
           #
           #           Arguments:
           #           - self: The current recordset being processed.
           #
           #           Returns:
           #           - None: The function updates the 'date_deadline' field for each record.
           #           """
        for record in self:
            create_date = record.create_date or fields.Date.today()
            record.date_deadline = create_date + timedelta(days=record.validity)


    def _inverse_date_deadline(self):
        """
            **Description:**
            - This method calculates the difference in days between `date_deadline` and `create_date`.
            - If `create_date` is not set, it defaults to today's date.
            - The computed difference (validity period) is stored in the `validity` field.
            - If the difference is negative, `validity` is set to 0.

            **Arguments:**
            - `self`: Represents the current record(s) being processed.

            **Returns:**
            - None: This method does not return a value but updates the `validity` field for each record.
            """
        for record in self:
            # If create_date is None, use today's date
            create_date = record.create_date.date() if record.create_date else fields.Date.today()
            if record.date_deadline:
                # Calculate the difference in days between deadline and creation date
                delta = (record.date_deadline - create_date).days
                record.validity = delta if delta >= 0 else 0

    def action_accept(self):
        """
            **Description:**
            - Checks if the property is already sold; if so, raises an error.
            - Ensures that only one offer can be accepted per property.
            - Updates the offer's status to 'accepted'.
            - Sets the property's selling price, buyer, and state to 'offer_accepted'.

            **Arguments:**
            - `self`: Represents the current record(s) being processed.

            **Returns:**
            - `True`: Returns `True` after successfully processing the offer.

            **Raises:**
            - `UserError`: If the property is already sold.
            - `UserError`: If an offer has already been accepted for the property.
         """
        for offer in self:
            if offer.property_id.state == 'sold':
                raise UserError("This property is already sold.")

            # Ensure only one offer can be accepted
            if offer.property_id.offer_ids.filtered(lambda o: o.status == 'accepted'):
                raise UserError("Only one offer can be accepted per property.")

            offer.status = 'accepted'
            offer.property_id.selling_price = offer.price
            offer.property_id.buyer_id = offer.partner_id
            offer.property_id.state = 'offer_accepted'
        return True

    def action_refuse(self):
        """.
           **Description:**
           - This method updates the `status` field of an offer to `'refused'`.
           - It is used when an offer is rejected by the seller.

           **Arguments:**
           - `self`: Represents the current record(s) being processed.

           **Returns:**
           - None: This method does not return a value but updates the `status` field.
           """
        for offer in self:
            offer.status = 'refused'

    @api.model
    def create(self, vals):
        """
               **Description:**
               - This method checks if the new offer price is higher than any existing offers.
               - If the new offer is lower than an existing one, it raises a `UserError`.
               - Updates the property state to `'offer_received'` when a valid offer is created.
               - Calls the superclass method to create the record.

               **Arguments:**
               - `vals` (dict): Dictionary of field values for the new record.

               **Returns:**
               - `record`: The newly created `estate.property.offer` record.

               **Raises:**
               - `UserError`: If an offer lower than an existing one is attempted.
               """


        property_id = vals.get('property_id')
        offer_price = vals.get('price')

        if property_id:
            property_obj = self.env['estate.property'].browse(property_id)

            # Check if there's a higher existing offer
            existing_offers = self.env['estate.property.offer'].search([
                ('property_id', '=', property_id)
            ])

            if existing_offers and any(offer.price > offer_price for offer in existing_offers):
                raise UserError(_("You cannot create an offer lower than an existing one."))

            # Update property state
            property_obj.state = 'offer_received'

        return super(EstatePropertyOffer, self).create(vals)


_sql_constraints = [
        ('check_offer_price',
         'CHECK(price > 0)',
         'The offer price must be strictly positive!')
    ]
