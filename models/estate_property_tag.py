from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _order = "name asc"

    name=fields.Char(string="Tag Name", required=True)
    color = fields.Integer(string="Color")

    _sql_constraints = [
        ('unique_property_tag_name',
         'UNIQUE(name)',
         'The tag name must be unique!')
    ]
