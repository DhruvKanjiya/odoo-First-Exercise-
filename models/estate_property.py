

from odoo import models, fields , api  ,_
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"

    name=fields.Char(string="Name",required=True)
    description=fields.Text(string="Description")
    postcode=fields.Char(string="Postcode")
    date_availability = fields.Date(default=lambda self: datetime.today() + timedelta(days=90), copy=False)
    # property_type = fields.Selection(
    #     [('house', 'House'), ('apartment', 'Apartment'), ('land', 'Land')],
    #     string="Property Type"
    # )
    active=fields.Boolean(string="Active",default=True)
    user_id=fields.Many2one('res.users',string="Owner")
    bedrooms=fields.Integer(string="Bedroom",default=2)
    facades=fields.Integer(string="Facades")
    garage=fields.Boolean(string="Garage")
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    salesperson_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string='Buyer',copy=False)
    property_tag_ids=fields.Many2many('estate.property.tag',string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    living_area = fields.Integer(string="Living")
    total_area=fields.Integer(string="Total Area" , compute="_compute_total_area",store=True)
    best_offer=fields.Float(string="Best Offer", compute="_compute_best_offer",store=True)
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Float(string="Garden Area" )
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ], string="Orientation")

    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled')
    ], string="Status", default="new")
    selling_price = fields.Float(string="Selling Price")
    expected_price = fields.Float(string="Expected Price", required=True)



    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        """
            Description:
                Computes the total area of a property by summing the living area and garden area.
                This method is triggered whenever 'living_area' or 'garden_area' is modified.

            Arguments:
                self (recordset): The current recordset for which the computation is performed.

            Return:
                None: The method updates the 'total_area' field in-place for each record.
            """
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        """
           Description:
               Computes the highest offer price from the related 'offer_ids'.
               It finds the maximum value among all offers linked to the record.
               If no offers exist, it defaults to 0.0.

           Arguments:
               self (recordset): The current recordset for which the computation is performed.

           Return:
               None: The method updates the 'best_offer' field in-place for each record.
           """
        for record in self:
            record.best_offer = max(record.offer_ids.mapped('price'), default=0.0)

    @api.onchange('garden')
    def _onchange_garden(self):
        """
            Description:
                This method is triggered when the 'garden' field is changed. It automatically
                sets the 'garden_area' and 'orientation' fields based on the presence of a garden.

            Arguments:
                None: This method does not accept any external arguments. It works directly with
                the current instance of the object (self).

            Return:
                None: This method does not return anything. It modifies the values of the fields
                'garden_area' and 'orientation' based on the garden selection.
            """

        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False  # Clears the field

    def action_cancel(self):

        """
            Description:
                This method is used to mark a property as 'Cancelled' if it is not already 'Sold'.
                If the property is already marked as 'Sold', it raises a `UserError` to prevent cancellation.

            Arguments:
                None: This method does not take external arguments. It works on the current instance
                of the object (self) in a loop, checking each record.

            Return:
                bool: Returns `True` after marking the property as cancelled, or raising an error if the property is sold.
            """

        for record in self:
            if record.state == 'sold':
                raise UserError("A sold property cannot be cancelled.")
            record.state = 'cancelled'


    def action_sold(self):

        """
            Description:
                This method is used to mark a property as 'Sold'. If the property is already
                marked as 'Cancelled', it raises a `UserError` to prevent it from being sold.

            Arguments:
                None: This method does not accept external arguments. It operates on the current instance
                of the object (self), iterating through each record.

            Return:
                bool: Returns `True` if the property is successfully marked as 'Sold'. If the property is cancelled,
                a `UserError` is raised, and the return value will not be reached.
            """

        for record in self:
            if record.state == 'cancelled':
                raise UserError("A cancelled property cannot be sold.")
            record.state = 'sold'

    def _update_state_on_offer(self):

        """
        **Description:**
    - This method checks if there are any offers (`offer_ids`) associated with the record.
    - If at least one offer exists, it updates the `state` field to `'offer_received'`.

    **Arguments:**
    - `self`: Represents the current record(s) being processed.

    **Returns:**
    - None: This method updates the `state` field of the record but does not return a value.
    """

        for record in self:
            if record.offer_ids:
                record.state = 'offer_received'

    # @api.ondelete(at_uninstall=False)
    # def _prevent_unlink(self):
    #     """"
    #      **Description:**
    # - This method restricts the deletion of records based on their state.
    # - If a record's state is not `'new'` or `'cancelled'`, a `UserError` is raised.
    # - This ensures that only properties in an initial or cancelled state can be deleted.
    #
    #     **Arguments:**
    # - `self`: Represents the current record(s) being processed.
    #
    #     **Returns:**
    # - None: This method does not return anything but raises an exception if the condition is met.
    #
    # **Raises:**
    # - `UserError`: If a property is in any state other than 'New' or 'Cancelled', an error message is shown to the user.
    # """
    #
    #     for property in self:
    #         if property.state not in ['new', 'cancelled']:
    #             raise UserError(_("You can only delete properties that are in 'New' or 'Cancelled' state."))

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        """
                **Description:**
                - This method validates that the `selling_price` of a property is at least 90% of the `expected_price`.
                - If the `selling_price` is **zero**, validation is skipped (to allow properties without a validated offer).
                - If the `selling_price` is **below 90%**, an error is raised.

                **Arguments:**
                - `selling_price` (float): The final selling price of the property.
                - `expected_price` (float): The initially expected price of the property.

                **Return:**
                - Raises a `ValidationError` if the `selling_price` is **less than 90% of the expected price**.
                """
        for record in self:
            # Allow selling_price to be zero until an offer is validated
            if float_is_zero(record.selling_price, precision_digits=2):
                continue  # Skip validation if selling price is zero

            # Calculate 90% of the expected price
            min_acceptable_price = record.expected_price * 0.90

            # Compare selling price with the minimum acceptable price
            if float_compare(record.selling_price, min_acceptable_price, precision_digits=2) == -1:
                raise ValidationError(
                    "Selling price cannot be lower than 90% of the expected price."
                )

    _sql_constraints = [
        ('check_expected_price',
         'CHECK(expected_price > 0)',
         'The expected price must be strictly positive!'),
        ('check_selling_price',
         'CHECK(selling_price >= 0)',
         'The selling price must be positive or zero!')
    ]