{
    'name': 'Estate',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'Manage real estate properties',
    'author': 'Dhruv Kanjiya',
    'depends': ['base'],  # The only necessary dependency for now
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_view.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_type_view.xml',
        'views/estate_property_tag_view.xml',
        'views/inherited_model_views.xml',
        'views/estate_property_action.xml',
        'views/estate_property_menu.xml'
    ],


    'installable': True,  # This ensures the module can be installed
    'application': True,  # This marks the module as an 'App' in the Apps list
    'auto_install': False,  # Whether it should be automatically installed
}