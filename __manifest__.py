{
    "name": "Purchase Offer",
    "version": "1.0",
    "summary": "Chức năng bổ sung cho Purchase",
    "category": "Purchase",
    "author": "GinGa GX",
    "license": "AGPL-3",
    "sequence": -99,
    "depends": ["purchase"],
    "auto_install": True,
    "data": [
        "security/purchase_offer_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/res_config_settings_views.xml",
        "views/purchase_offer_views.xml"
    ],
    "installable": True,
    "application": False,
}
