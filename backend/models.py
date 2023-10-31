from django.db import models


# Create your models here.
class Logs(models.Model):
    id = models.AutoField(primary_key=True)
    script_name = models.TextField()
    time = models.DateTimeField()
    status = models.TextField()
    value = models.TextField()
    details = models.TextField()

    class Meta:
        managed = False
        db_table = "logs"


class FelmeresQuestions(models.Model):
    question = models.ForeignKey("Questions", models.DO_NOTHING, db_column="question")
    value = models.TextField(blank=True, null=True)
    adatlap = models.ForeignKey("Felmeresek", models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(
        "Products", models.DO_NOTHING, db_column="product", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "pen_felmeres_questions"


class FelmeresekNotes(models.Model):
    value = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    felmeres_id = models.TextField(blank=True, null=True)
    user_id = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    reply_to = models.IntegerField(blank=True, null=True)
    seen = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_felmeresek_notes"


class Products(models.Model):
    id = models.BigIntegerField(
        db_column="ID", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.
    sku = models.TextField(
        db_column="SKU", blank=True, null=True
    )  # Field name made lowercase.
    type = models.TextField(
        db_column="Type", blank=True, null=True
    )  # Field name made lowercase.
    barcodes = models.TextField(
        db_column="Barcodes", blank=True, null=True
    )  # Field name made lowercase.
    alternative_sku = models.TextField(
        db_column="Alternative_SKU", blank=True, null=True
    )  # Field name made lowercase.
    minimum_stock_quantity = models.FloatField(
        db_column="Minimum_Stock_Quantity", blank=True, null=True
    )  # Field name made lowercase.
    optimal_stock_quantity = models.FloatField(
        db_column="Optimal_Stock_Quantity", blank=True, null=True
    )  # Field name made lowercase.
    category = models.TextField(
        db_column="Category", blank=True, null=True
    )  # Field name made lowercase.
    parent_id = models.TextField(
        db_column="Parent_ID", blank=True, null=True
    )  # Field name made lowercase.
    parent_sku = models.TextField(
        db_column="Parent_SKU", blank=True, null=True
    )  # Field name made lowercase.
    bundles_sku = models.TextField(
        db_column="Bundles_SKU", blank=True, null=True
    )  # Field name made lowercase.
    description = models.TextField(
        db_column="Description", blank=True, null=True
    )  # Field name made lowercase.
    short_description = models.TextField(
        db_column="Short_Description", blank=True, null=True
    )  # Field name made lowercase.
    images = models.BigIntegerField(
        db_column="Images", blank=True, null=True
    )  # Field name made lowercase.
    unit = models.TextField(
        db_column="Unit", blank=True, null=True
    )  # Field name made lowercase.
    moq = models.FloatField(
        db_column="MOQ", blank=True, null=True
    )  # Field name made lowercase.
    uom = models.FloatField(
        db_column="UOM", blank=True, null=True
    )  # Field name made lowercase.
    length = models.FloatField(
        db_column="Length", blank=True, null=True
    )  # Field name made lowercase.
    width = models.FloatField(
        db_column="Width", blank=True, null=True
    )  # Field name made lowercase.
    height = models.FloatField(
        db_column="Height", blank=True, null=True
    )  # Field name made lowercase.
    weight = models.BigIntegerField(
        db_column="Weight", blank=True, null=True
    )  # Field name made lowercase.
    net_weight = models.FloatField(
        db_column="Net_Weight", blank=True, null=True
    )  # Field name made lowercase.
    webshop_sort_order = models.BigIntegerField(
        db_column="Webshop_Sort_Order", blank=True, null=True
    )  # Field name made lowercase.
    commodity_code = models.TextField(
        db_column="Commodity_Code", blank=True, null=True
    )  # Field name made lowercase.
    excisable_product = models.BigIntegerField(
        db_column="Excisable_Product", blank=True, null=True
    )  # Field name made lowercase.
    combined_nomenclature = models.FloatField(
        db_column="Combined_Nomenclature", blank=True, null=True
    )  # Field name made lowercase.
    quantity_multiplier = models.FloatField(
        db_column="Quantity_Multiplier", blank=True, null=True
    )  # Field name made lowercase.
    supplementary_unit = models.FloatField(
        db_column="Supplementary_Unit", blank=True, null=True
    )  # Field name made lowercase.
    country_of_origin = models.FloatField(
        db_column="Country_Of_Origin", blank=True, null=True
    )  # Field name made lowercase.
    warranty_period = models.FloatField(
        db_column="Warranty_Period", blank=True, null=True
    )  # Field name made lowercase.
    warranty_period_unit = models.TextField(
        db_column="Warranty_Period_Unit", blank=True, null=True
    )  # Field name made lowercase.
    virtual = models.BigIntegerField(
        db_column="Virtual", blank=True, null=True
    )  # Field name made lowercase.
    fragile = models.TextField(
        db_column="Fragile", blank=True, null=True
    )  # Field name made lowercase.
    product_class = models.TextField(
        db_column="Product_Class", blank=True, null=True
    )  # Field name made lowercase.
    upsell_products = models.TextField(
        db_column="Upsell_Products", blank=True, null=True
    )  # Field name made lowercase.
    upsell_categories = models.TextField(
        db_column="Upsell_Categories", blank=True, null=True
    )  # Field name made lowercase.
    tags = models.TextField(
        db_column="Tags", blank=True, null=True
    )  # Field name made lowercase.
    virtual_net_cost = models.FloatField(
        db_column="Virtual_Net_Cost", blank=True, null=True
    )  # Field name made lowercase.
    virtual_net_cost_currency = models.TextField(
        db_column="Virtual_Net_Cost_Currency", blank=True, null=True
    )  # Field name made lowercase.
    tracking_type = models.TextField(
        db_column="Tracking_Type", blank=True, null=True
    )  # Field name made lowercase.
    manufacturer = models.TextField(
        db_column="Manufacturer", blank=True, null=True
    )  # Field name made lowercase.
    manufacturer_sku = models.TextField(
        db_column="Manufacturer_Sku", blank=True, null=True
    )  # Field name made lowercase.
    price_list_alapertelmezett_net_price_huf = models.BigIntegerField(
        db_column="Price_List___alapertelmezett___Net_Price_HUF", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    price_list_alapertelmezett_price_huf = models.FloatField(
        db_column="Price_List___alapertelmezett___Price_HUF", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    price_list_alapertelmezett_vat = models.TextField(
        db_column="Price_List___alapertelmezett___VAT", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    price_list_alapertelmezett_vat_field = models.BigIntegerField(
        db_column="Price_List___alapertelmezett___VAT_", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row. Field renamed because it ended with '_'.
    price_list_alapertelmezett_quantity_discount = models.FloatField(
        db_column="Price_List___alapertelmezett___Quantity_Discount",
        blank=True,
        null=True,
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    price_list_alapertelmezett_formula = models.TextField(
        db_column="Price_List___alapertelmezett___Formula", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    price_list_alapertelmezett_price_type = models.TextField(
        db_column="Price_List___alapertelmezett___Price_Type", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_net_price_huf = models.FloatField(
        db_column="Sale_Price_List___alapertelmezett___Net_Price_HUF",
        blank=True,
        null=True,
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_price_huf = models.FloatField(
        db_column="Sale_Price_List___alapertelmezett___Price_HUF", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_vat = models.FloatField(
        db_column="Sale_Price_List___alapertelmezett___VAT", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_vat_field = models.FloatField(
        db_column="Sale_Price_List___alapertelmezett___VAT_", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row. Field renamed because it ended with '_'.
    sale_price_list_alapertelmezett_from_date = models.FloatField(
        db_column="Sale_Price_List___alapertelmezett___From_Date", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_to_date = models.FloatField(
        db_column="Sale_Price_List___alapertelmezett___To_Date", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_quantity_discount = models.FloatField(
        db_column="Sale_Price_List___alapertelmezett___Quantity_Discount",
        blank=True,
        null=True,
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_formula = models.FloatField(
        db_column="Sale_Price_List___alapertelmezett___Formula", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_price_type = models.FloatField(
        db_column="Sale_Price_List___alapertelmezett___Price_Type",
        blank=True,
        null=True,
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    warehouse_raktar_1_allowed = models.BigIntegerField(
        db_column="Warehouse___Raktar_1___Allowed", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    warehouse_raktar_1_minimum_stock_quantity = models.FloatField(
        db_column="Warehouse___Raktar_1____Minimum_Stock_Quantity",
        blank=True,
        null=True,
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    warehouse_raktar_1_optimal_stock_quantity = models.FloatField(
        db_column="Warehouse___Raktar_1____Optimal_Stock_Quantity",
        blank=True,
        null=True,
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    warehouse_selejt_allowed = models.BigIntegerField(
        db_column="Warehouse___Selejt___Allowed", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    warehouse_selejt_minimum_stock_quantity = models.FloatField(
        db_column="Warehouse___Selejt____Minimum_Stock_Quantity", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    warehouse_selejt_optimal_stock_quantity = models.FloatField(
        db_column="Warehouse___Selejt____Optimal_Stock_Quantity", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.

    class Meta:
        managed = False
        db_table = "pen_products"


class ProductAttributes(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey("Products", models.DO_NOTHING)
    place = models.BooleanField(blank=True, null=True)
    place_options = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_product_attributes"


class Filters(models.Model):
    name = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    sort_by = models.TextField(blank=True, null=True)
    sort_order = models.CharField(blank=True, null=True)
    user = models.TextField(db_column="user_id", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_filters"


class FilterItems(models.Model):
    field = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=225, blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    filter = models.ForeignKey("Filters", models.CASCADE)
    label = models.TextField(blank=True, null=True)
    options = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_filter_items"


class Questions(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    connection = models.CharField(max_length=255, blank=True, null=True)
    options = models.JSONField(blank=True, null=True)
    mandatory = models.BooleanField()
    description = models.TextField(blank=True, null=True)
    created_from = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_questions"


class Templates(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_templates"


class ProductTemplate(models.Model):
    template = models.ForeignKey("Templates", models.CASCADE, primary_key=True)
    product = models.ForeignKey(
        "Products", models.DO_NOTHING
    )  # The composite primary key (product_id, template_id) found, that is not supported. The first column is selected.

    class Meta:
        managed = False
        db_table = "pen_product_template"
        unique_together = (("product", "template"),)


class Felmeresek(models.Model):
    id = models.AutoField(primary_key=True)
    adatlap_id = models.IntegerField()
    template = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True, default="DRAFT")
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_felmeresek"


class FelmeresItems(models.Model):
    name = models.TextField(blank=True, null=True)
    place = models.BooleanField(blank=True, null=True)
    placeOptions = models.JSONField(
        db_column="place_options", blank=True, null=True
    )  # This field type is a guess.
    product = models.ForeignKey(
        "Products", models.DO_NOTHING, db_column="product_id", blank=True, null=True
    )
    inputValues = models.JSONField(db_column="input_values", blank=True, null=True)
    netPrice = models.IntegerField(db_column="net_price", blank=True, null=True)
    adatlap = models.ForeignKey("Felmeresek", models.CASCADE, db_column="adatlap_id")
    type = models.CharField(max_length=255, blank=True, null=True)
    valueType = models.CharField(
        max_length=255, blank=True, null=True, default="fixed", db_column="value_type"
    )
    source = models.CharField(max_length=100, blank=True, null=True, default="Manual")

    class Meta:
        managed = False
        db_table = "pen_felmeres_items"


class Counties(models.Model):
    telepules = models.TextField(
        db_column="Telepules", primary_key=True
    )  # Field name made lowercase.
    jogallasa = models.TextField(blank=True, null=True)
    megye = models.TextField(
        db_column="Megye_megnevezese_", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = "counties"


class Offers(models.Model):
    id = models.AutoField(primary_key=True)
    offer_id = models.IntegerField(blank=True, null=True)
    adatlap = models.IntegerField(db_column="adatlap_id")
    felmeres_id = models.IntegerField(db_column="Felmeresid", blank=True, null=True)
    status_id = models.IntegerField(blank=True, null=True, db_column="StatusId")

    class Meta:
        managed = False
        db_table = "pen_offers"


class QuestionProducts(models.Model):
    product = models.ForeignKey(
        "Products", models.DO_NOTHING
    )  # The composite primary key (product_id, question_id) found, that is not supported. The first column is selected.
    question = models.ForeignKey("Questions", models.CASCADE, primary_key=True)

    class Meta:
        managed = False
        db_table = "pen_question_products"
        unique_together = (("product", "question"),)


class ErpAuthTokens(models.Model):
    token = models.CharField(max_length=255, blank=True, null=True)
    expire = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_erp_auth_tokens"


class Orders(models.Model):
    adatlap_id = models.IntegerField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_orders"


class Order(models.Model):
    row_type = models.TextField(
        db_column="Row_Type", blank=True, null=True
    )  # Field name made lowercase.
    order_id = models.TextField(
        db_column="Order_ID", blank=True, null=True
    )  # Field name made lowercase.
    sku = models.TextField(
        db_column="SKU", blank=True, null=True
    )  # Field name made lowercase.
    product_name = models.TextField(
        db_column="Product_Name", blank=True, null=True
    )  # Field name made lowercase.
    default_supplier_unit_price = models.FloatField(
        db_column="Default_Supplier_Unit_Price", blank=True, null=True
    )  # Field name made lowercase.
    default_supplier_currency = models.TextField(
        db_column="Default_Supplier_Currency", blank=True, null=True
    )  # Field name made lowercase.
    quantity = models.FloatField(
        db_column="Quantity", blank=True, null=True
    )  # Field name made lowercase.
    unit_price = models.FloatField(
        db_column="Unit_Price", blank=True, null=True
    )  # Field name made lowercase.
    discount = models.FloatField(
        db_column="Discount", blank=True, null=True
    )  # Field name made lowercase.
    tax = models.FloatField(
        db_column="Tax", blank=True, null=True
    )  # Field name made lowercase.
    subtotal = models.FloatField(
        db_column="Subtotal", blank=True, null=True
    )  # Field name made lowercase.
    landed_cost = models.FloatField(
        db_column="Landed_Cost", blank=True, null=True
    )  # Field name made lowercase.
    cogs = models.FloatField(
        db_column="Cogs", blank=True, null=True
    )  # Field name made lowercase.
    margin = models.FloatField(
        db_column="Margin", blank=True, null=True
    )  # Field name made lowercase.
    margin_field = models.FloatField(
        db_column="Margin_", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it ended with '_'.
    item_note = models.FloatField(
        db_column="Item_Note", blank=True, null=True
    )  # Field name made lowercase.
    weight = models.FloatField(
        db_column="Weight", blank=True, null=True
    )  # Field name made lowercase.
    webshop_id = models.TextField(
        db_column="Webshop_ID", blank=True, null=True
    )  # Field name made lowercase.
    return_reason = models.TextField(
        db_column="Return_Reason", blank=True, null=True
    )  # Field name made lowercase.
    package_number = models.FloatField(
        db_column="Package_Number", blank=True, null=True
    )  # Field name made lowercase.
    order_total = models.FloatField(
        db_column="Order_Total", blank=True, null=True
    )  # Field name made lowercase.
    currency = models.TextField(
        db_column="Currency", blank=True, null=True
    )  # Field name made lowercase.
    source = models.TextField(
        db_column="Source", blank=True, null=True
    )  # Field name made lowercase.
    source_name = models.TextField(
        db_column="Source_Name", blank=True, null=True
    )  # Field name made lowercase.
    order_status = models.TextField(
        db_column="Order_Status", blank=True, null=True
    )  # Field name made lowercase.
    order_date = models.TextField(
        db_column="Order_Date", blank=True, null=True
    )  # Field name made lowercase.
    customer_identifier = models.FloatField(
        db_column="Customer_Identifier", blank=True, null=True
    )  # Field name made lowercase.
    memo = models.TextField(
        db_column="Memo", blank=True, null=True
    )  # Field name made lowercase.
    billing_email = models.TextField(
        db_column="Billing_Email", blank=True, null=True
    )  # Field name made lowercase.
    billing_address_1 = models.TextField(
        db_column="Billing_Address_1", blank=True, null=True
    )  # Field name made lowercase.
    billing_address_2 = models.TextField(
        db_column="Billing_Address_2", blank=True, null=True
    )  # Field name made lowercase.
    billing_country = models.TextField(
        db_column="Billing_Country", blank=True, null=True
    )  # Field name made lowercase.
    billing_city = models.TextField(
        db_column="Billing_City", blank=True, null=True
    )  # Field name made lowercase.
    billing_zip_code = models.BigIntegerField(
        db_column="Billing_Zip_Code", blank=True, null=True
    )  # Field name made lowercase.
    billing_last_name = models.TextField(
        db_column="Billing_Last_Name", blank=True, null=True
    )  # Field name made lowercase.
    billing_first_name = models.TextField(
        db_column="Billing_First_Name", blank=True, null=True
    )  # Field name made lowercase.
    billing_tax_number = models.TextField(
        db_column="Billing_Tax_Number", blank=True, null=True
    )  # Field name made lowercase.
    billing_company = models.TextField(
        db_column="Billing_Company", blank=True, null=True
    )  # Field name made lowercase.
    manual_invoicing = models.BooleanField(
        db_column="Manual_Invoicing", blank=True, null=True
    )  # Field name made lowercase.
    manual_proforma = models.BooleanField(
        db_column="Manual_Proforma", blank=True, null=True
    )  # Field name made lowercase.
    shipping_email = models.TextField(
        db_column="Shipping_Email", blank=True, null=True
    )  # Field name made lowercase.
    shipping_address_1 = models.TextField(
        db_column="Shipping_Address_1", blank=True, null=True
    )  # Field name made lowercase.
    shipping_address_2 = models.TextField(
        db_column="Shipping_Address_2", blank=True, null=True
    )  # Field name made lowercase.
    shipping_country = models.TextField(
        db_column="Shipping_Country", blank=True, null=True
    )  # Field name made lowercase.
    shipping_city = models.TextField(
        db_column="Shipping_City", blank=True, null=True
    )  # Field name made lowercase.
    shipping_zip_code = models.TextField(
        db_column="Shipping_Zip_Code", blank=True, null=True
    )  # Field name made lowercase.
    shipping_last_name = models.TextField(
        db_column="Shipping_Last_Name", blank=True, null=True
    )  # Field name made lowercase.
    shipping_first_name = models.TextField(
        db_column="Shipping_First_Name", blank=True, null=True
    )  # Field name made lowercase.
    shipping_company = models.TextField(
        db_column="Shipping_Company", blank=True, null=True
    )  # Field name made lowercase.
    delivery_note = models.TextField(
        db_column="Delivery_Note", blank=True, null=True
    )  # Field name made lowercase.
    shipping_method = models.TextField(
        db_column="Shipping_Method", blank=True, null=True
    )  # Field name made lowercase.
    payment_method = models.TextField(
        db_column="Payment_Method", blank=True, null=True
    )  # Field name made lowercase.
    discount_value = models.BigIntegerField(
        db_column="Discount_Value", blank=True, null=True
    )  # Field name made lowercase.
    exchange_rate = models.BigIntegerField(
        db_column="Exchange_Rate", blank=True, null=True
    )  # Field name made lowercase.
    payment_status = models.TextField(
        db_column="Payment_Status", blank=True, null=True
    )  # Field name made lowercase.
    warehouse = models.TextField(
        db_column="Warehouse", blank=True, null=True
    )  # Field name made lowercase.
    delivery_date = models.FloatField(
        db_column="Delivery_Date", blank=True, null=True
    )  # Field name made lowercase.
    proforma_invoice_id = models.TextField(
        db_column="Proforma_Invoice_ID", blank=True, null=True
    )  # Field name made lowercase.
    proforma_invoice_id_2 = models.FloatField(
        db_column="Proforma_Invoice_ID_2", blank=True, null=True
    )  # Field name made lowercase.
    invoice_id = models.TextField(
        db_column="Invoice_ID", blank=True, null=True
    )  # Field name made lowercase.
    reverse_invoice_id = models.TextField(
        db_column="Reverse_Invoice_ID", blank=True, null=True
    )  # Field name made lowercase.
    prepayment_reverse_invoice_id = models.FloatField(
        db_column="Prepayment_Reverse_Invoice_ID", blank=True, null=True
    )  # Field name made lowercase.
    prepayment_reverse_invoice_id_2 = models.FloatField(
        db_column="Prepayment_Reverse_Invoice_ID_2", blank=True, null=True
    )  # Field name made lowercase.
    tags = models.TextField(
        db_column="Tags", blank=True, null=True
    )  # Field name made lowercase.
    customer_classes = models.TextField(
        db_column="Customer_Classes", blank=True, null=True
    )  # Field name made lowercase.
    created_by = models.TextField(
        db_column="Created_By", blank=True, null=True
    )  # Field name made lowercase.
    default_customer_class = models.TextField(
        db_column="Default_Customer_Class", blank=True, null=True
    )  # Field name made lowercase.
    paid_at = models.TextField(
        db_column="Paid_At", blank=True, null=True
    )  # Field name made lowercase.
    cancel_reason = models.TextField(
        db_column="Cancel_Reason", blank=True, null=True
    )  # Field name made lowercase.
    cancelled_by = models.TextField(
        db_column="Cancelled_By", blank=True, null=True
    )  # Field name made lowercase.
    cancelled_at = models.TextField(
        db_column="Cancelled_At", blank=True, null=True
    )  # Field name made lowercase.
    completed_at = models.TextField(
        db_column="Completed_At", blank=True, null=True
    )  # Field name made lowercase.
    id = models.AutoField(
        db_column="id", primary_key=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "pen_order"


class PaymentMethods(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_payment_methods"


class FelmeresPictures(models.Model):
    felmeres = models.ForeignKey("Felmeresek", models.CASCADE)
    src = models.TextField()

    class Meta:
        managed = False
        db_table = "pen_felmeres_pictures"


class UserRoles(models.Model):
    user = models.TextField(db_column="user_id", blank=True, null=True)
    role = models.ForeignKey(
        "Roles", models.DO_NOTHING, blank=True, null=True, db_column="role"
    )

    class Meta:
        managed = False
        db_table = "pen_user_roles"


class Roles(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_roles"


class MinicrmAdatlapok(models.Model):
    id = models.TextField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    categoryid = models.TextField(
        db_column="CategoryId", blank=True, null=True
    )  # Field name made lowercase.
    contactid = models.TextField(
        db_column="ContactId", blank=True, null=True
    )  # Field name made lowercase.
    maincontactid = models.TextField(
        db_column="MainContactId", blank=True, null=True
    )  # Field name made lowercase.
    statusid = models.TextField(
        db_column="StatusId", blank=True, null=True
    )  # Field name made lowercase.
    userid = models.TextField(
        db_column="UserId", blank=True, null=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.
    statusupdatedat = models.TextField(
        db_column="StatusUpdatedAt", blank=True, null=True
    )  # Field name made lowercase.
    isprivate = models.TextField(
        db_column="IsPrivate", blank=True, null=True
    )  # Field name made lowercase.
    invited = models.TextField(
        db_column="Invited", blank=True, null=True
    )  # Field name made lowercase.
    deleted = models.TextField(
        db_column="Deleted", blank=True, null=True
    )  # Field name made lowercase.
    createdby = models.BigIntegerField(
        db_column="CreatedBy", blank=True, null=True
    )  # Field name made lowercase.
    createdat = models.TextField(
        db_column="CreatedAt", blank=True, null=True
    )  # Field name made lowercase.
    updatedby = models.BigIntegerField(
        db_column="UpdatedBy", blank=True, null=True
    )  # Field name made lowercase.
    updatedat = models.TextField(
        db_column="UpdatedAt", blank=True, null=True
    )  # Field name made lowercase.
    referrer = models.TextField(
        db_column="Referrer", blank=True, null=True
    )  # Field name made lowercase.
    whynotus = models.TextField(
        db_column="WhyNotUs", blank=True, null=True
    )  # Field name made lowercase.
    whyus = models.TextField(
        db_column="WhyUs", blank=True, null=True
    )  # Field name made lowercase.
    importdate = models.TextField(
        db_column="ImportDate", blank=True, null=True
    )  # Field name made lowercase.
    related_businessid = models.TextField(
        db_column="Related_BusinessId", blank=True, null=True
    )  # Field name made lowercase.
    referenceid = models.TextField(
        db_column="ReferenceId", blank=True, null=True
    )  # Field name made lowercase.
    number = models.TextField(
        db_column="Number", blank=True, null=True
    )  # Field name made lowercase.
    issued = models.TextField(
        db_column="Issued", blank=True, null=True
    )  # Field name made lowercase.
    performance = models.TextField(
        db_column="Performance", blank=True, null=True
    )  # Field name made lowercase.
    prompt = models.TextField(
        db_column="Prompt", blank=True, null=True
    )  # Field name made lowercase.
    paid = models.TextField(
        db_column="Paid", blank=True, null=True
    )  # Field name made lowercase.
    amount = models.TextField(
        db_column="Amount", blank=True, null=True
    )  # Field name made lowercase.
    invoicetype = models.TextField(
        db_column="InvoiceType", blank=True, null=True
    )  # Field name made lowercase.
    invoicepdf = models.TextField(
        db_column="InvoicePdf", blank=True, null=True
    )  # Field name made lowercase.
    listsubscriptions = models.BigIntegerField(
        db_column="ListSubscriptions", blank=True, null=True
    )  # Field name made lowercase.
    pushtoken = models.TextField(
        db_column="PushToken", blank=True, null=True
    )  # Field name made lowercase.
    pushdevice = models.TextField(
        db_column="PushDevice", blank=True, null=True
    )  # Field name made lowercase.
    uuid = models.TextField(
        db_column="UUId", blank=True, null=True
    )  # Field name made lowercase.
    uninstalledat = models.TextField(
        db_column="UninstalledAt", blank=True, null=True
    )  # Field name made lowercase.
    phonever = models.TextField(
        db_column="PhoneVer", blank=True, null=True
    )  # Field name made lowercase.
    osver = models.TextField(
        db_column="OSVer", blank=True, null=True
    )  # Field name made lowercase.
    appver = models.TextField(
        db_column="AppVer", blank=True, null=True
    )  # Field name made lowercase.
    autosales_salesstatus = models.TextField(
        db_column="AutoSales_SalesStatus", blank=True, null=True
    )  # Field name made lowercase.
    autosales_qualification = models.TextField(
        db_column="AutoSales_Qualification", blank=True, null=True
    )  # Field name made lowercase.
    autosales_reachedstatus = models.TextField(
        db_column="AutoSales_ReachedStatus", blank=True, null=True
    )  # Field name made lowercase.
    autosales_lasttodomodification = models.TextField(
        db_column="AutoSales_LastToDoModification", blank=True, null=True
    )  # Field name made lowercase.
    satisfactionrating = models.TextField(
        db_column="SatisfactionRating", blank=True, null=True
    )  # Field name made lowercase.
    reachedmobileactivity = models.TextField(
        db_column="ReachedMobileActivity", blank=True, null=True
    )  # Field name made lowercase.
    mobilelastlogin = models.TextField(
        db_column="MobileLastLogin", blank=True, null=True
    )  # Field name made lowercase.
    emailmodule_emailcount = models.TextField(
        db_column="EmailModule_EmailCount", blank=True, null=True
    )  # Field name made lowercase.
    emailmodule_openrate = models.TextField(
        db_column="EmailModule_OpenRate", blank=True, null=True
    )  # Field name made lowercase.
    emailmodule_clickrate = models.TextField(
        db_column="EmailModule_ClickRate", blank=True, null=True
    )  # Field name made lowercase.
    mobileloggedin = models.BigIntegerField(
        db_column="MobileLoggedIn", blank=True, null=True
    )  # Field name made lowercase.
    webshop_reachedstatus = models.TextField(
        db_column="Webshop_ReachedStatus", blank=True, null=True
    )  # Field name made lowercase.
    webshop_lifetimevalue = models.TextField(
        db_column="Webshop_LifeTimeValue", blank=True, null=True
    )  # Field name made lowercase.
    webshop_numberoforders = models.TextField(
        db_column="Webshop_NumberOfOrders", blank=True, null=True
    )  # Field name made lowercase.
    webshop_numberofproducts = models.TextField(
        db_column="Webshop_NumberOfProducts", blank=True, null=True
    )  # Field name made lowercase.
    webshop_firstorderdate = models.TextField(
        db_column="Webshop_FirstOrderDate", blank=True, null=True
    )  # Field name made lowercase.
    webshop_lastorderdate = models.TextField(
        db_column="Webshop_LastOrderDate", blank=True, null=True
    )  # Field name made lowercase.
    webshop_lastorderamount = models.TextField(
        db_column="Webshop_LastOrderAmount", blank=True, null=True
    )  # Field name made lowercase.
    webshop_lastorderstatus = models.TextField(
        db_column="Webshop_LastOrderStatus", blank=True, null=True
    )  # Field name made lowercase.
    webshop_disabled = models.BigIntegerField(
        db_column="Webshop_Disabled", blank=True, null=True
    )  # Field name made lowercase.
    webshop_registrationdate = models.TextField(
        db_column="Webshop_RegistrationDate", blank=True, null=True
    )  # Field name made lowercase.
    webshop_lostbasketcontent = models.TextField(
        db_column="Webshop_LostBasketContent", blank=True, null=True
    )  # Field name made lowercase.
    webshop_lostbasketdate = models.TextField(
        db_column="Webshop_LostBasketDate", blank=True, null=True
    )  # Field name made lowercase.
    webshop_lostbasketvalue = models.TextField(
        db_column="Webshop_LostBasketValue", blank=True, null=True
    )  # Field name made lowercase.
    webshop_alllostbasket = models.TextField(
        db_column="Webshop_AllLostBasket", blank=True, null=True
    )  # Field name made lowercase.
    autosalesv2_qualification = models.TextField(
        db_column="AutoSalesV2_Qualification", blank=True, null=True
    )  # Field name made lowercase.
    autosalesv2_rating = models.TextField(
        db_column="AutoSalesV2_Rating", blank=True, null=True
    )  # Field name made lowercase.
    autosalesv2_salesstatus = models.TextField(
        db_column="AutoSalesV2_SalesStatus", blank=True, null=True
    )  # Field name made lowercase.
    salesstepv2 = models.TextField(
        db_column="SalesStepV2", blank=True, null=True
    )  # Field name made lowercase.
    newsletterv2 = models.BigIntegerField(
        db_column="NewsletterV2", blank=True, null=True
    )  # Field name made lowercase.
    autosalesv2_reachedstatus = models.TextField(
        db_column="AutoSalesV2_ReachedStatus", blank=True, null=True
    )  # Field name made lowercase.
    emailopen_phone = models.TextField(
        db_column="EmailOpen_Phone", blank=True, null=True
    )  # Field name made lowercase.
    emailopen_tablet = models.TextField(
        db_column="EmailOpen_Tablet", blank=True, null=True
    )  # Field name made lowercase.
    emailopen_iphone = models.TextField(
        db_column="EmailOpen_iPhone", blank=True, null=True
    )  # Field name made lowercase.
    emailopen_ipad = models.TextField(
        db_column="EmailOpen_iPad", blank=True, null=True
    )  # Field name made lowercase.
    emailopen_android = models.TextField(
        db_column="EmailOpen_Android", blank=True, null=True
    )  # Field name made lowercase.
    autosalesv3_qualification = models.TextField(
        db_column="AutoSalesV3_Qualification", blank=True, null=True
    )  # Field name made lowercase.
    autosalesv3_ishot = models.BigIntegerField(
        db_column="AutoSalesV3_IsHot", blank=True, null=True
    )  # Field name made lowercase.
    autosalesv3_salesstatus = models.TextField(
        db_column="AutoSalesV3_SalesStatus", blank=True, null=True
    )  # Field name made lowercase.
    autosalesv3_reachedstatus = models.TextField(
        db_column="AutoSalesV3_ReachedStatus", blank=True, null=True
    )  # Field name made lowercase.
    autosalesv3_reachedstatusgroup = models.TextField(
        db_column="AutoSalesV3_ReachedStatusGroup", blank=True, null=True
    )  # Field name made lowercase.
    autosalesv3_leadstep = models.TextField(
        db_column="AutoSalesV3_LeadStep", blank=True, null=True
    )  # Field name made lowercase.
    autosalesv3_customerstep = models.TextField(
        db_column="AutoSalesV3_CustomerStep", blank=True, null=True
    )  # Field name made lowercase.
    write_protected = models.TextField(
        db_column="Write_Protected", blank=True, null=True
    )  # Field name made lowercase.
    navstatus = models.TextField(
        db_column="NavStatus", blank=True, null=True
    )  # Field name made lowercase.
    navstatusmessage = models.TextField(
        db_column="NavStatusMessage", blank=True, null=True
    )  # Field name made lowercase.
    newsletter_subscriber = models.BigIntegerField(
        db_column="Newsletter_Subscriber", blank=True, null=True
    )  # Field name made lowercase.
    customercard_activationdate = models.TextField(
        db_column="CustomerCard_ActivationDate", blank=True, null=True
    )  # Field name made lowercase.
    customercard_averagepurchase = models.TextField(
        db_column="CustomerCard_AveragePurchase", blank=True, null=True
    )  # Field name made lowercase.
    customercard_birthday = models.TextField(
        db_column="CustomerCard_Birthday", blank=True, null=True
    )  # Field name made lowercase.
    customercard_cardnumber = models.TextField(
        db_column="CustomerCard_CardNumber", blank=True, null=True
    )  # Field name made lowercase.
    customercard_cardstatus = models.TextField(
        db_column="CustomerCard_CardStatus", blank=True, null=True
    )  # Field name made lowercase.
    customercard_cardtype = models.TextField(
        db_column="CustomerCard_CardType", blank=True, null=True
    )  # Field name made lowercase.
    customercard_comment = models.TextField(
        db_column="CustomerCard_Comment", blank=True, null=True
    )  # Field name made lowercase.
    customercard_moneybalance = models.TextField(
        db_column="CustomerCard_MoneyBalance", blank=True, null=True
    )  # Field name made lowercase.
    customercard_nameday = models.TextField(
        db_column="CustomerCard_Nameday", blank=True, null=True
    )  # Field name made lowercase.
    customercard_pointbalance = models.TextField(
        db_column="CustomerCard_PointBalance", blank=True, null=True
    )  # Field name made lowercase.
    customercard_registeredbusiness = models.TextField(
        db_column="CustomerCard_RegisteredBusiness", blank=True, null=True
    )  # Field name made lowercase.
    customercard_sex = models.TextField(
        db_column="CustomerCard_Sex", blank=True, null=True
    )  # Field name made lowercase.
    customercard_userid = models.TextField(
        db_column="CustomerCard_UserId", blank=True, null=True
    )  # Field name made lowercase.
    customercard_validcoupons = models.TextField(
        db_column="CustomerCard_ValidCoupons", blank=True, null=True
    )  # Field name made lowercase.
    customercard_validpasses = models.TextField(
        db_column="CustomerCard_ValidPasses", blank=True, null=True
    )  # Field name made lowercase.
    customercard_registrationdate = models.TextField(
        db_column="CustomerCard_RegistrationDate", blank=True, null=True
    )  # Field name made lowercase.
    customercard_lifetimevalue = models.TextField(
        db_column="CustomerCard_LifeTimeValue", blank=True, null=True
    )  # Field name made lowercase.
    customercard_numberoforders = models.TextField(
        db_column="CustomerCard_NumberOfOrders", blank=True, null=True
    )  # Field name made lowercase.
    customercard_lastorderdate = models.TextField(
        db_column="CustomerCard_LastOrderDate", blank=True, null=True
    )  # Field name made lowercase.
    projectmanagement_deadline = models.TextField(
        db_column="ProjectManagement_Deadline", blank=True, null=True
    )  # Field name made lowercase.
    projectmanagement_expectedrevenue = models.TextField(
        db_column="ProjectManagement_ExpectedRevenue", blank=True, null=True
    )  # Field name made lowercase.
    projectmanagement_type = models.TextField(
        db_column="ProjectManagement_Type", blank=True, null=True
    )  # Field name made lowercase.
    projectmanagement_desiredoutcome = models.TextField(
        db_column="ProjectManagement_DesiredOutcome", blank=True, null=True
    )  # Field name made lowercase.
    serial_number = models.TextField(
        db_column="Serial_Number", blank=True, null=True
    )  # Field name made lowercase.
    inboundinvoice_navstatus = models.TextField(
        db_column="InboundInvoice_NavStatus", blank=True, null=True
    )  # Field name made lowercase.
    inboundinvoice_navnumber = models.TextField(
        db_column="InboundInvoice_NavNumber", blank=True, null=True
    )  # Field name made lowercase.
    holiday_start = models.TextField(
        db_column="Holiday_Start", blank=True, null=True
    )  # Field name made lowercase.
    holiday_end = models.TextField(
        db_column="Holiday_End", blank=True, null=True
    )  # Field name made lowercase.
    holiday_substitute = models.TextField(
        db_column="Holiday_Substitute", blank=True, null=True
    )  # Field name made lowercase.
    interests = models.BigIntegerField(
        db_column="Interests", blank=True, null=True
    )  # Field name made lowercase.
    type = models.TextField(
        db_column="Type", blank=True, null=True
    )  # Field name made lowercase.
    category = models.TextField(
        db_column="Category", blank=True, null=True
    )  # Field name made lowercase.
    deadline = models.TextField(
        db_column="Deadline", blank=True, null=True
    )  # Field name made lowercase.
    offerdate = models.TextField(
        db_column="OfferDate", blank=True, null=True
    )  # Field name made lowercase.
    offerprice = models.TextField(
        db_column="OfferPrice", blank=True, null=True
    )  # Field name made lowercase.
    datetime2 = models.TextField(
        db_column="Datetime2", blank=True, null=True
    )  # Field name made lowercase.
    checkbox29 = models.BigIntegerField(
        db_column="Checkbox29", blank=True, null=True
    )  # Field name made lowercase.
    checkbox31 = models.BigIntegerField(
        db_column="Checkbox31", blank=True, null=True
    )  # Field name made lowercase.
    checkbox34 = models.BigIntegerField(
        db_column="Checkbox34", blank=True, null=True
    )  # Field name made lowercase.
    checkbox37 = models.BigIntegerField(
        db_column="Checkbox37", blank=True, null=True
    )  # Field name made lowercase.
    checkbox38 = models.BigIntegerField(
        db_column="Checkbox38", blank=True, null=True
    )  # Field name made lowercase.
    checkbox39 = models.BigIntegerField(
        db_column="Checkbox39", blank=True, null=True
    )  # Field name made lowercase.
    checkbox35 = models.BigIntegerField(
        db_column="Checkbox35", blank=True, null=True
    )  # Field name made lowercase.
    enum1 = models.TextField(
        db_column="Enum1", blank=True, null=True
    )  # Field name made lowercase.
    datetime44 = models.TextField(
        db_column="Datetime44", blank=True, null=True
    )  # Field name made lowercase.
    datetime45 = models.TextField(
        db_column="Datetime45", blank=True, null=True
    )  # Field name made lowercase.
    datetime3 = models.TextField(
        db_column="Datetime3", blank=True, null=True
    )  # Field name made lowercase.
    enum5 = models.TextField(
        db_column="Enum5", blank=True, null=True
    )  # Field name made lowercase.
    enum6 = models.TextField(
        db_column="Enum6", blank=True, null=True
    )  # Field name made lowercase.
    enum7 = models.TextField(
        db_column="Enum7", blank=True, null=True
    )  # Field name made lowercase.
    set8 = models.BigIntegerField(
        db_column="Set8", blank=True, null=True
    )  # Field name made lowercase.
    enum9 = models.TextField(
        db_column="Enum9", blank=True, null=True
    )  # Field name made lowercase.
    set10 = models.BigIntegerField(
        db_column="Set10", blank=True, null=True
    )  # Field name made lowercase.
    enum11 = models.TextField(
        db_column="Enum11", blank=True, null=True
    )  # Field name made lowercase.
    set12 = models.BigIntegerField(
        db_column="Set12", blank=True, null=True
    )  # Field name made lowercase.
    int14 = models.TextField(
        db_column="Int14", blank=True, null=True
    )  # Field name made lowercase.
    int15 = models.TextField(
        db_column="Int15", blank=True, null=True
    )  # Field name made lowercase.
    int16 = models.TextField(
        db_column="Int16", blank=True, null=True
    )  # Field name made lowercase.
    int17 = models.TextField(
        db_column="Int17", blank=True, null=True
    )  # Field name made lowercase.
    varchar18 = models.TextField(
        db_column="Varchar18", blank=True, null=True
    )  # Field name made lowercase.
    enum19 = models.TextField(
        db_column="Enum19", blank=True, null=True
    )  # Field name made lowercase.
    enum20 = models.TextField(
        db_column="Enum20", blank=True, null=True
    )  # Field name made lowercase.
    enum21 = models.TextField(
        db_column="Enum21", blank=True, null=True
    )  # Field name made lowercase.
    enum22 = models.TextField(
        db_column="Enum22", blank=True, null=True
    )  # Field name made lowercase.
    enum23 = models.TextField(
        db_column="Enum23", blank=True, null=True
    )  # Field name made lowercase.
    set25 = models.BigIntegerField(
        db_column="Set25", blank=True, null=True
    )  # Field name made lowercase.
    int26 = models.TextField(
        db_column="Int26", blank=True, null=True
    )  # Field name made lowercase.
    set27 = models.BigIntegerField(
        db_column="Set27", blank=True, null=True
    )  # Field name made lowercase.
    int40 = models.TextField(
        db_column="Int40", blank=True, null=True
    )  # Field name made lowercase.
    checkbox42 = models.BigIntegerField(
        db_column="Checkbox42", blank=True, null=True
    )  # Field name made lowercase.
    enum1098 = models.TextField(
        db_column="Enum1098", blank=True, null=True
    )  # Field name made lowercase.
    text1099 = models.TextField(
        db_column="Text1099", blank=True, null=True
    )  # Field name made lowercase.
    datetime1100 = models.TextField(
        db_column="DateTime1100", blank=True, null=True
    )  # Field name made lowercase.
    text1101 = models.TextField(
        db_column="Text1101", blank=True, null=True
    )  # Field name made lowercase.
    text1102 = models.TextField(
        db_column="Text1102", blank=True, null=True
    )  # Field name made lowercase.
    enum1103 = models.TextField(
        db_column="Enum1103", blank=True, null=True
    )  # Field name made lowercase.
    enum1104 = models.TextField(
        db_column="Enum1104", blank=True, null=True
    )  # Field name made lowercase.
    enum1105 = models.TextField(
        db_column="Enum1105", blank=True, null=True
    )  # Field name made lowercase.
    text1106 = models.TextField(
        db_column="Text1106", blank=True, null=True
    )  # Field name made lowercase.
    enum1107 = models.TextField(
        db_column="Enum1107", blank=True, null=True
    )  # Field name made lowercase.
    alaprajzfeltoltese = models.TextField(
        db_column="AlaprajzFeltoltese", blank=True, null=True
    )  # Field name made lowercase.
    lapraszereltszellozo = models.BigIntegerField(
        db_column="LapraszereltSzellozo", blank=True, null=True
    )  # Field name made lowercase.
    kapcsolatfelvetelokanakrovidleirasa = models.TextField(
        db_column="KapcsolatfelvetelOkanakRovidLeirasa", blank=True, null=True
    )  # Field name made lowercase.
    alakasbantalalhatogazkazancirko = models.BigIntegerField(
        db_column="ALakasbanTalalhatoGazkazanCirko", blank=True, null=True
    )  # Field name made lowercase.
    oknoplastviszontelado = models.TextField(
        db_column="OknoplastViszontelado", blank=True, null=True
    )  # Field name made lowercase.
    enum1115 = models.TextField(
        db_column="Enum1115", blank=True, null=True
    )  # Field name made lowercase.
    enum1116 = models.TextField(
        db_column="Enum1116", blank=True, null=True
    )  # Field name made lowercase.
    int1117 = models.TextField(
        db_column="Int1117", blank=True, null=True
    )  # Field name made lowercase.
    set1118 = models.BigIntegerField(
        db_column="Set1118", blank=True, null=True
    )  # Field name made lowercase.
    enum1119 = models.TextField(
        db_column="Enum1119", blank=True, null=True
    )  # Field name made lowercase.
    enum1121 = models.TextField(
        db_column="Enum1121", blank=True, null=True
    )  # Field name made lowercase.
    datetime1122 = models.TextField(
        db_column="DateTime1122", blank=True, null=True
    )  # Field name made lowercase.
    text1124 = models.TextField(
        db_column="Text1124", blank=True, null=True
    )  # Field name made lowercase.
    felmeres = models.TextField(
        db_column="Felmeres", blank=True, null=True
    )  # Field name made lowercase.
    felmeresidopontja = models.TextField(
        db_column="FelmeresIdopontja", blank=True, null=True
    )  # Field name made lowercase.
    enum1130 = models.TextField(
        db_column="Enum1130", blank=True, null=True
    )  # Field name made lowercase.
    enum1131 = models.TextField(
        db_column="Enum1131", blank=True, null=True
    )  # Field name made lowercase.
    int1132 = models.TextField(
        db_column="Int1132", blank=True, null=True
    )  # Field name made lowercase.
    set1133 = models.BigIntegerField(
        db_column="Set1133", blank=True, null=True
    )  # Field name made lowercase.
    leiras = models.TextField(
        db_column="Leiras", blank=True, null=True
    )  # Field name made lowercase.
    problemak = models.BigIntegerField(
        db_column="Problemak", blank=True, null=True
    )  # Field name made lowercase.
    mitprobaltalmar = models.BigIntegerField(
        db_column="MitProbaltalMar", blank=True, null=True
    )  # Field name made lowercase.
    joinurl = models.TextField(
        db_column="JoinUrl", blank=True, null=True
    )  # Field name made lowercase.
    kovetkezowebinarium = models.TextField(
        db_column="KovetkezoWebinarium", blank=True, null=True
    )  # Field name made lowercase.
    milyenproblemarakeresmegoldast = models.BigIntegerField(
        db_column="MilyenProblemaraKeresMegoldast", blank=True, null=True
    )  # Field name made lowercase.
    mitprobaltmar = models.BigIntegerField(
        db_column="MitProbaltMar", blank=True, null=True
    )  # Field name made lowercase.
    szabadszovegesleiras = models.TextField(
        db_column="SzabadSzovegesLeiras", blank=True, null=True
    )  # Field name made lowercase.
    url = models.TextField(
        db_column="Url", blank=True, null=True
    )  # Field name made lowercase.
    webinariumrajelentkezett = models.BigIntegerField(
        db_column="WebinariumraJelentkezett", blank=True, null=True
    )  # Field name made lowercase.
    resztvett = models.BigIntegerField(
        db_column="ResztVett", blank=True, null=True
    )  # Field name made lowercase.
    webinariummegjegyzes = models.TextField(
        db_column="WebinariumMegjegyzes", blank=True, null=True
    )  # Field name made lowercase.
    felmeresmegtortent = models.BigIntegerField(
        db_column="FelmeresMegtortent", blank=True, null=True
    )  # Field name made lowercase.
    felmerestkert = models.BigIntegerField(
        db_column="FelmerestKert", blank=True, null=True
    )  # Field name made lowercase.
    kedvezmeny = models.TextField(
        db_column="Kedvezmeny", blank=True, null=True
    )  # Field name made lowercase.
    lakaselhelyezkedese = models.TextField(
        db_column="LakasElhelyezkedese", blank=True, null=True
    )  # Field name made lowercase.
    epitoanyag = models.TextField(
        db_column="Epitoanyag", blank=True, null=True
    )  # Field name made lowercase.
    epitmenykora = models.TextField(
        db_column="EpitmenyKora", blank=True, null=True
    )  # Field name made lowercase.
    apeneszedesparalecsapodasmegjelenese = models.BigIntegerField(
        db_column="APeneszedesParalecsapodasMegjelenese", blank=True, null=True
    )  # Field name made lowercase.
    nyilaszaroktipusa = models.TextField(
        db_column="NyilaszarokTipusa", blank=True, null=True
    )  # Field name made lowercase.
    apeneszedesselparalecsapodassalerintetthelyisegek = models.BigIntegerField(
        db_column="APeneszedesselParalecsapodassalErintettHelyisegek",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    apeneszedeselofordulasafokent = models.TextField(
        db_column="APeneszedesElofordulasaFokent", blank=True, null=True
    )  # Field name made lowercase.
    lakasalapterulete = models.TextField(
        db_column="LakasAlapterulete", blank=True, null=True
    )  # Field name made lowercase.
    lakasbelmagassaga = models.TextField(
        db_column="LakasBelmagassaga", blank=True, null=True
    )  # Field name made lowercase.
    kulsotartofalakvastagsaga = models.TextField(
        db_column="KulsoTartoFalakVastagsaga", blank=True, null=True
    )  # Field name made lowercase.
    kulsoszigetelesvastagsaga = models.TextField(
        db_column="KulsoSzigetelesVastagsaga", blank=True, null=True
    )  # Field name made lowercase.
    alakasfodememennyezete = models.TextField(
        db_column="ALakasFodemeMennyezete", blank=True, null=True
    )  # Field name made lowercase.
    lakohelyisegekszamaszobaknappali = models.TextField(
        db_column="LakoHelyisegekSzamaSzobakNappali", blank=True, null=True
    )  # Field name made lowercase.
    vizeshelyisegekszamafurdowckonyhamosokonyhastb = models.TextField(
        db_column="VizesHelyisegekSzamaFurdoWcKonyhaMosokonyhaStb",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    egyebhelyisegekszamatarolokamragardrobstb = models.TextField(
        db_column="EgyebHelyisegekSzamaTaroloKamraGardrobStb", blank=True, null=True
    )  # Field name made lowercase.
    kuszobabelteriajtokon = models.TextField(
        db_column="KuszobABelteriAjtokon", blank=True, null=True
    )  # Field name made lowercase.
    lakasfutese = models.TextField(
        db_column="LakasFutese", blank=True, null=True
    )  # Field name made lowercase.
    alakasbantalalhatogazkeszulekek = models.BigIntegerField(
        db_column="ALakasbanTalalhatoGazkeszulekek", blank=True, null=True
    )  # Field name made lowercase.
    alakasbantalalhatoszellozesilehetosegek = models.BigIntegerField(
        db_column="ALakasbanTalalhatoSzellozesiLehetosegek", blank=True, null=True
    )  # Field name made lowercase.
    alakasbanlakoszemelyekszama = models.TextField(
        db_column="ALakasbanLakoSzemelyekSzama", blank=True, null=True
    )  # Field name made lowercase.
    alaprajzfeltoltese2 = models.TextField(
        db_column="AlaprajzFeltoltese2", blank=True, null=True
    )  # Field name made lowercase.
    peneszedesrolfenykep = models.TextField(
        db_column="PeneszedesrolFenykep", blank=True, null=True
    )  # Field name made lowercase.
    egyebhasznoskep = models.TextField(
        db_column="EgyebHasznosKep", blank=True, null=True
    )  # Field name made lowercase.
    fenykepakazanrol = models.TextField(
        db_column="FenykepAKazanrol", blank=True, null=True
    )  # Field name made lowercase.
    acsaladbanvan = models.BigIntegerField(
        db_column="ACsaladbanVan", blank=True, null=True
    )  # Field name made lowercase.
    felmerolapotkitoltotte = models.BigIntegerField(
        db_column="FelmerolapotKitoltotte", blank=True, null=True
    )  # Field name made lowercase.
    mikorkuldtunkajanlatot = models.TextField(
        db_column="MikorKuldtunkAjanlatot", blank=True, null=True
    )  # Field name made lowercase.
    enum1183 = models.TextField(
        db_column="Enum1183", blank=True, null=True
    )  # Field name made lowercase.
    text1184 = models.TextField(
        db_column="Text1184", blank=True, null=True
    )  # Field name made lowercase.
    enum1185 = models.TextField(
        db_column="Enum1185", blank=True, null=True
    )  # Field name made lowercase.
    int1186 = models.TextField(
        db_column="Int1186", blank=True, null=True
    )  # Field name made lowercase.
    file1188 = models.TextField(
        db_column="File1188", blank=True, null=True
    )  # Field name made lowercase.
    datetime1189 = models.TextField(
        db_column="DateTime1189", blank=True, null=True
    )  # Field name made lowercase.
    enum1190 = models.TextField(
        db_column="Enum1190", blank=True, null=True
    )  # Field name made lowercase.
    text1191 = models.TextField(
        db_column="Text1191", blank=True, null=True
    )  # Field name made lowercase.
    datetime1192 = models.TextField(
        db_column="DateTime1192", blank=True, null=True
    )  # Field name made lowercase.
    afeladatleirasaabeepitoknek = models.TextField(
        db_column="AFeladatLeirasaABeepitoknek", blank=True, null=True
    )  # Field name made lowercase.
    kimertefel = models.BigIntegerField(
        db_column="KiMerteFel", blank=True, null=True
    )  # Field name made lowercase.
    felmeresijegyzetek = models.TextField(
        db_column="FelmeresiJegyzetek", blank=True, null=True
    )  # Field name made lowercase.
    beepitesijegyzetek = models.TextField(
        db_column="BeepitesiJegyzetek", blank=True, null=True
    )  # Field name made lowercase.
    kepekabeepitesrol = models.TextField(
        db_column="KepekABeepitesrol", blank=True, null=True
    )  # Field name made lowercase.
    kepekabeepiteshez01 = models.TextField(
        db_column="KepekABeepiteshez01", blank=True, null=True
    )  # Field name made lowercase.
    kepekabeepiteshez02 = models.TextField(
        db_column="KepekABeepiteshez02", blank=True, null=True
    )  # Field name made lowercase.
    kepekabeepiteshez03 = models.TextField(
        db_column="KepekABeepiteshez03", blank=True, null=True
    )  # Field name made lowercase.
    kepekabeepitesrol02 = models.TextField(
        db_column="KepekABeepitesrol02", blank=True, null=True
    )  # Field name made lowercase.
    ventitipus = models.TextField(
        db_column="VentiTipus", blank=True, null=True
    )  # Field name made lowercase.
    hazvlakas = models.TextField(
        db_column="HazVLakas", blank=True, null=True
    )  # Field name made lowercase.
    ablakoslegbevezetok = models.TextField(
        db_column="AblakosLegbevezetok", blank=True, null=True
    )  # Field name made lowercase.
    falilegbevezetok = models.TextField(
        db_column="FaliLegbevezetok", blank=True, null=True
    )  # Field name made lowercase.
    hollesznekalegbevezetok = models.TextField(
        db_column="HolLesznekALegbevezetok", blank=True, null=True
    )  # Field name made lowercase.
    holleszfali = models.TextField(
        db_column="HolLeszFali", blank=True, null=True
    )  # Field name made lowercase.
    hanyajtofuras = models.TextField(
        db_column="HanyAjtoFuras", blank=True, null=True
    )  # Field name made lowercase.
    melyikajtok = models.TextField(
        db_column="MelyikAjtok", blank=True, null=True
    )  # Field name made lowercase.
    szellozoracshelye = models.TextField(
        db_column="SzellozoRacsHelye", blank=True, null=True
    )  # Field name made lowercase.
    hanybelsofalatbontaslesz = models.TextField(
        db_column="HanyBelsoFalAtbontasLesz", blank=True, null=True
    )  # Field name made lowercase.
    egyebkotojelessorkbarendezve = models.TextField(
        db_column="EgyebKotojelesSorkbaRendezve", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzesaventihelyerolabeepitoknek = models.TextField(
        db_column="MegjegyzesAVentiHelyerolABeepitoknek", blank=True, null=True
    )  # Field name made lowercase.
    nettoar = models.TextField(
        db_column="NettoAr", blank=True, null=True
    )  # Field name made lowercase.
    bruttoar = models.TextField(
        db_column="BruttoAr", blank=True, null=True
    )  # Field name made lowercase.
    nettoarft = models.TextField(
        db_column="NettoArFt", blank=True, null=True
    )  # Field name made lowercase.
    bruttoar2 = models.TextField(
        db_column="BruttoAr2", blank=True, null=True
    )  # Field name made lowercase.
    bruttoarbetuvelkiirva = models.TextField(
        db_column="BruttoArBetuvelKiirva", blank=True, null=True
    )  # Field name made lowercase.
    ebbol957 = models.TextField(
        db_column="Ebbol957", blank=True, null=True
    )  # Field name made lowercase.
    ebbol916 = models.TextField(
        db_column="Ebbol916", blank=True, null=True
    )  # Field name made lowercase.
    n780as = models.TextField(
        db_column="N780as", blank=True, null=True
    )  # Field name made lowercase.
    hollesz916os = models.TextField(
        db_column="HolLesz916os", blank=True, null=True
    )  # Field name made lowercase.
    hollesz957es = models.TextField(
        db_column="HolLesz957es", blank=True, null=True
    )  # Field name made lowercase.
    n716os = models.TextField(
        db_column="N716os", blank=True, null=True
    )  # Field name made lowercase.
    egyebmunkakcsakabeepitoklatjak = models.TextField(
        db_column="EgyebMunkakCsakABeepitokLatjak", blank=True, null=True
    )  # Field name made lowercase.
    paraerzekelosbcx = models.TextField(
        db_column="ParaerzekelosBcx", blank=True, null=True
    )  # Field name made lowercase.
    hova = models.TextField(
        db_column="Hova", blank=True, null=True
    )  # Field name made lowercase.
    hollesza = models.TextField(
        db_column="HolLeszA", blank=True, null=True
    )  # Field name made lowercase.
    hova2 = models.TextField(
        db_column="Hova2", blank=True, null=True
    )  # Field name made lowercase.
    paraesmozgaserzekelosbxc = models.TextField(
        db_column="ParaEsMozgasErzekelosBxc", blank=True, null=True
    )  # Field name made lowercase.
    mozgaserzekelosbxc = models.TextField(
        db_column="MozgaserzekelosBxc", blank=True, null=True
    )  # Field name made lowercase.
    hova3 = models.TextField(
        db_column="Hova3", blank=True, null=True
    )  # Field name made lowercase.
    zsirszuro = models.TextField(
        db_column="Zsirszuro", blank=True, null=True
    )  # Field name made lowercase.
    holleszzajcsillapitobetet = models.TextField(
        db_column="HolLeszZajcsillapitoBetet", blank=True, null=True
    )  # Field name made lowercase.
    zajcsillapitobetetfali = models.TextField(
        db_column="ZajcsillapitoBetetFali", blank=True, null=True
    )  # Field name made lowercase.
    v2av4avamtipusa = models.TextField(
        db_column="V2aV4aVamTipusa", blank=True, null=True
    )  # Field name made lowercase.
    holleszaventieshogyleszkialakitvaajanlatonezlatszik = models.TextField(
        db_column="HolLeszAVentiEsHogyLeszKialakitvaAjanlatonEzLatszik",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    kialakitasrolegyebinfoabeepitoknek = models.TextField(
        db_column="KialakitasrolEgyebInfoABeepitoknek", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzesakabelezeshezabeepitoknek = models.TextField(
        db_column="MegjegyzesAKabelezeshezABeepitoknek", blank=True, null=True
    )  # Field name made lowercase.
    cim = models.TextField(
        db_column="Cim", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzesacimmelkapcsolatban = models.TextField(
        db_column="MegjegyzesACimmelKapcsolatban", blank=True, null=True
    )  # Field name made lowercase.
    holleszear201es = models.TextField(
        db_column="HolLeszEar201es", blank=True, null=True
    )  # Field name made lowercase.
    ear201db = models.TextField(
        db_column="Ear201Db", blank=True, null=True
    )  # Field name made lowercase.
    holleszear200as = models.TextField(
        db_column="HolLeszEar200as", blank=True, null=True
    )  # Field name made lowercase.
    ear200asdb = models.TextField(
        db_column="Ear200asDb", blank=True, null=True
    )  # Field name made lowercase.
    holleszredonytokos = models.TextField(
        db_column="HolLeszRedonytokos", blank=True, null=True
    )  # Field name made lowercase.
    redonytokoslegbevezetodb = models.TextField(
        db_column="RedonytokosLegbevezetoDb", blank=True, null=True
    )  # Field name made lowercase.
    megjalegbevezetokhozszinesovedostb = models.TextField(
        db_column="MegjALegbevezetokhozSzinEsovedoStb", blank=True, null=True
    )  # Field name made lowercase.
    egyebinfoalegbevezetokbeepitesehez = models.TextField(
        db_column="EgyebInfoALegbevezetokBeepitesehez", blank=True, null=True
    )  # Field name made lowercase.
    kulonlegesszinhelyesovedostb = models.TextField(
        db_column="KulonlegesSzinHelyEsovedoStb", blank=True, null=True
    )  # Field name made lowercase.
    egyebinfoaredonytokosbeepitesehez = models.TextField(
        db_column="EgyebInfoARedonytokosBeepitesehez", blank=True, null=True
    )  # Field name made lowercase.
    osszesenhanydb201200mind = models.TextField(
        db_column="OsszesenHanyDb201200Mind", blank=True, null=True
    )  # Field name made lowercase.
    ajtoszellozokarikaszine = models.TextField(
        db_column="AjtoszellozoKarikaSzine", blank=True, null=True
    )  # Field name made lowercase.
    n716osszine = models.TextField(
        db_column="N716osSzine", blank=True, null=True
    )  # Field name made lowercase.
    n916osszine = models.TextField(
        db_column="N916osSzine", blank=True, null=True
    )  # Field name made lowercase.
    hakellcsoveznimibolmennyikell2 = models.TextField(
        db_column="HaKellCsovezniMibolMennyiKell2", blank=True, null=True
    )  # Field name made lowercase.
    garanciavalarralkapcsolatosmegjegyzes = models.TextField(
        db_column="GaranciavalArralKapcsolatosMegjegyzes", blank=True, null=True
    )  # Field name made lowercase.
    pluszvisszaaramlasgatlokdb = models.TextField(
        db_column="PluszVisszaaramlasGatlokDb", blank=True, null=True
    )  # Field name made lowercase.
    hovakellaplusszvisszaaramlasgatlo = models.TextField(
        db_column="HovaKellAPlusszVisszaaramlasGatlo", blank=True, null=True
    )  # Field name made lowercase.
    int1320 = models.TextField(
        db_column="Int1320", blank=True, null=True
    )  # Field name made lowercase.
    enum1322 = models.TextField(
        db_column="Enum1322", blank=True, null=True
    )  # Field name made lowercase.
    text1323 = models.TextField(
        db_column="Text1323", blank=True, null=True
    )  # Field name made lowercase.
    enum1326 = models.TextField(
        db_column="Enum1326", blank=True, null=True
    )  # Field name made lowercase.
    text1335 = models.TextField(
        db_column="Text1335", blank=True, null=True
    )  # Field name made lowercase.
    legutolsoajanlat = models.TextField(
        db_column="LegutolsoAjanlat", blank=True, null=True
    )  # Field name made lowercase.
    kepapeneszesfalszakaszrol = models.TextField(
        db_column="KepAPeneszesFalszakaszrol", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzesapeneszedesselkapcsolatba = models.TextField(
        db_column="MegjegyzesAPeneszedesselKapcsolatba", blank=True, null=True
    )  # Field name made lowercase.
    ablakokajtokkulsobelsoszine = models.TextField(
        db_column="AblakokAjtokKulsoBelsoSzine", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzesazablakokkalajtokkalkapcsolatba = models.TextField(
        db_column="MegjegyzesAzAblakokkalAjtokkalKapcsolatba", blank=True, null=True
    )  # Field name made lowercase.
    azalaprajznaktartalmazniakell = models.BigIntegerField(
        db_column="AzAlaprajznakTartalmazniaKell", blank=True, null=True
    )  # Field name made lowercase.
    nemkapgariszerzodest = models.BigIntegerField(
        db_column="NemKapGariSzerzodest", blank=True, null=True
    )  # Field name made lowercase.
    holvanaram2 = models.TextField(
        db_column="HolVanAram2", blank=True, null=True
    )  # Field name made lowercase.
    ventilatorkapcsolasanakkialakitasa2 = models.TextField(
        db_column="VentilatorKapcsolasanakKialakitasa2", blank=True, null=True
    )  # Field name made lowercase.
    kepabeepiteshez04 = models.TextField(
        db_column="KepABeepiteshez04", blank=True, null=True
    )  # Field name made lowercase.
    enum1361 = models.TextField(
        db_column="Enum1361", blank=True, null=True
    )  # Field name made lowercase.
    text1362 = models.TextField(
        db_column="Text1362", blank=True, null=True
    )  # Field name made lowercase.
    enum1363 = models.TextField(
        db_column="Enum1363", blank=True, null=True
    )  # Field name made lowercase.
    file1365 = models.TextField(
        db_column="File1365", blank=True, null=True
    )  # Field name made lowercase.
    text1367 = models.TextField(
        db_column="Text1367", blank=True, null=True
    )  # Field name made lowercase.
    text1368 = models.TextField(
        db_column="Text1368", blank=True, null=True
    )  # Field name made lowercase.
    enum1370 = models.TextField(
        db_column="Enum1370", blank=True, null=True
    )  # Field name made lowercase.
    tervrajzfeltoltes = models.TextField(
        db_column="TervrajzFeltoltes", blank=True, null=True
    )  # Field name made lowercase.
    hirlevelrefeliratkozas = models.BigIntegerField(
        db_column="HirlevelreFeliratkozas", blank=True, null=True
    )  # Field name made lowercase.
    gdprnyilatkozat = models.BigIntegerField(
        db_column="GdprNyilatkozat", blank=True, null=True
    )  # Field name made lowercase.
    mikorraterveziafelujitast = models.TextField(
        db_column="MikorraTerveziAFelujitast", blank=True, null=True
    )  # Field name made lowercase.
    miazugyfelfoszempontja = models.TextField(
        db_column="MiAzUgyfelFoSzempontja", blank=True, null=True
    )  # Field name made lowercase.
    ilyenvoltkep1 = models.TextField(
        db_column="IlyenVoltKep1", blank=True, null=True
    )  # Field name made lowercase.
    ilyenvoltkep2 = models.TextField(
        db_column="IlyenVoltKep2", blank=True, null=True
    )  # Field name made lowercase.
    kivitelezesinfo = models.TextField(
        db_column="KivitelezesInfo", blank=True, null=True
    )  # Field name made lowercase.
    ilyenlettkep1 = models.TextField(
        db_column="IlyenLettKep1", blank=True, null=True
    )  # Field name made lowercase.
    ilyenlettkep2 = models.TextField(
        db_column="IlyenLettKep2", blank=True, null=True
    )  # Field name made lowercase.
    melyikbrigadvolt = models.TextField(
        db_column="MelyikBrigadVolt", blank=True, null=True
    )  # Field name made lowercase.
    elszamolasdatum = models.TextField(
        db_column="ElszamolasDatum", blank=True, null=True
    )  # Field name made lowercase.
    elszamolasiosszeg = models.TextField(
        db_column="ElszamolasiOsszeg", blank=True, null=True
    )  # Field name made lowercase.
    penzugyimegjegyzes = models.TextField(
        db_column="PenzugyiMegjegyzes", blank=True, null=True
    )  # Field name made lowercase.
    anyagkoltseg = models.TextField(
        db_column="AnyagKoltseg", blank=True, null=True
    )  # Field name made lowercase.
    reklamacioinfo = models.TextField(
        db_column="ReklamacioInfo", blank=True, null=True
    )  # Field name made lowercase.
    reklamaciokoltsege = models.TextField(
        db_column="ReklamacioKoltsege", blank=True, null=True
    )  # Field name made lowercase.
    felmeresdatuma = models.TextField(
        db_column="FelmeresDatuma", blank=True, null=True
    )  # Field name made lowercase.
    egyebszempontok = models.BigIntegerField(
        db_column="EgyebSzempontok", blank=True, null=True
    )  # Field name made lowercase.
    datetime1415 = models.TextField(
        db_column="DateTime1415", blank=True, null=True
    )  # Field name made lowercase.
    text1416 = models.TextField(
        db_column="Text1416", blank=True, null=True
    )  # Field name made lowercase.
    int1417 = models.TextField(
        db_column="Int1417", blank=True, null=True
    )  # Field name made lowercase.
    set1418 = models.BigIntegerField(
        db_column="Set1418", blank=True, null=True
    )  # Field name made lowercase.
    enum1419 = models.TextField(
        db_column="Enum1419", blank=True, null=True
    )  # Field name made lowercase.
    set1420 = models.BigIntegerField(
        db_column="Set1420", blank=True, null=True
    )  # Field name made lowercase.
    datetime1421 = models.TextField(
        db_column="DateTime1421", blank=True, null=True
    )  # Field name made lowercase.
    file1422 = models.TextField(
        db_column="File1422", blank=True, null=True
    )  # Field name made lowercase.
    file1423 = models.TextField(
        db_column="File1423", blank=True, null=True
    )  # Field name made lowercase.
    enum1424 = models.TextField(
        db_column="Enum1424", blank=True, null=True
    )  # Field name made lowercase.
    enum1425 = models.TextField(
        db_column="Enum1425", blank=True, null=True
    )  # Field name made lowercase.
    set1426 = models.BigIntegerField(
        db_column="Set1426", blank=True, null=True
    )  # Field name made lowercase.
    file1427 = models.TextField(
        db_column="File1427", blank=True, null=True
    )  # Field name made lowercase.
    datetime1428 = models.TextField(
        db_column="DateTime1428", blank=True, null=True
    )  # Field name made lowercase.
    enum1429 = models.TextField(
        db_column="Enum1429", blank=True, null=True
    )  # Field name made lowercase.
    datetime1430 = models.TextField(
        db_column="DateTime1430", blank=True, null=True
    )  # Field name made lowercase.
    enum1431 = models.TextField(
        db_column="Enum1431", blank=True, null=True
    )  # Field name made lowercase.
    text1432 = models.TextField(
        db_column="Text1432", blank=True, null=True
    )  # Field name made lowercase.
    datetime1433 = models.TextField(
        db_column="DateTime1433", blank=True, null=True
    )  # Field name made lowercase.
    file1434 = models.TextField(
        db_column="File1434", blank=True, null=True
    )  # Field name made lowercase.
    set1435 = models.BigIntegerField(
        db_column="Set1435", blank=True, null=True
    )  # Field name made lowercase.
    datetime1436 = models.TextField(
        db_column="DateTime1436", blank=True, null=True
    )  # Field name made lowercase.
    parkolasilehetosegek = models.BigIntegerField(
        db_column="ParkolasiLehetosegek", blank=True, null=True
    )  # Field name made lowercase.
    felmeresijegyzetek2 = models.TextField(
        db_column="FelmeresiJegyzetek2", blank=True, null=True
    )  # Field name made lowercase.
    ventitipusa = models.TextField(
        db_column="VentiTipusa", blank=True, null=True
    )  # Field name made lowercase.
    melyikhelyisegbenleszaventilista = models.TextField(
        db_column="Melyikhelyisegbenleszaventilista", blank=True, null=True
    )  # Field name made lowercase.
    hogyleszkialakitvaaventi = models.TextField(
        db_column="Hogyleszkialakitvaaventi", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzesacsovezeshez = models.TextField(
        db_column="MegjegyzesACsovezeshez", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzesaventihelyerolabeepitoknek_0 = models.TextField(
        db_column="Megjegyzesaventihelyerolabeepitoknek", blank=True, null=True
    )  # Field name made lowercase. Field renamed because of name conflict.
    n780as2 = models.TextField(
        db_column="N780as2", blank=True, null=True
    )  # Field name made lowercase.
    hovakerula780as = models.TextField(
        db_column="HovaKerulA780as", blank=True, null=True
    )  # Field name made lowercase.
    n957esdb = models.TextField(
        db_column="N957esDb", blank=True, null=True
    )  # Field name made lowercase.
    hovakerula957es = models.TextField(
        db_column="HovaKerulA957es", blank=True, null=True
    )  # Field name made lowercase.
    zajcsillapitobetetfalidb = models.TextField(
        db_column="ZajcsillapitoBetetFaliDb", blank=True, null=True
    )  # Field name made lowercase.
    holleszzajcsillapitobetet2 = models.TextField(
        db_column="HolLeszZajcsillapitoBetet2", blank=True, null=True
    )  # Field name made lowercase.
    egyebinfoalegbevezetokbeepitesehez2 = models.TextField(
        db_column="EgyebInfoALegbevezetokBeepitesehez2", blank=True, null=True
    )  # Field name made lowercase.
    rajzabeepiteshez = models.TextField(
        db_column="RajzABeepiteshez", blank=True, null=True
    )  # Field name made lowercase.
    ujszovegdobozafeladatleirasaabeepitoknek = models.TextField(
        db_column="UjSzovegdobozAFeladatLeirasaABeepitoknek", blank=True, null=True
    )  # Field name made lowercase.
    parkolasilehetosegek2 = models.BigIntegerField(
        db_column="ParkolasiLehetosegek2", blank=True, null=True
    )  # Field name made lowercase.
    miazugyfelfoszempontja2 = models.TextField(
        db_column="MiAzUgyfelFoSzempontja2", blank=True, null=True
    )  # Field name made lowercase.
    egyebszempontok2 = models.BigIntegerField(
        db_column="EgyebSzempontok2", blank=True, null=True
    )  # Field name made lowercase.
    ertekesitesiinfok = models.TextField(
        db_column="ErtekesitesiInfok", blank=True, null=True
    )  # Field name made lowercase.
    kepabeepiteshez05 = models.TextField(
        db_column="KepABeepiteshez05", blank=True, null=True
    )  # Field name made lowercase.
    ingatlanhasznalat2 = models.TextField(
        db_column="IngatlanHasznalat2", blank=True, null=True
    )  # Field name made lowercase.
    kivitelezescime = models.TextField(
        db_column="KivitelezesCime", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzesacimmelkapcsolatban2 = models.TextField(
        db_column="MegjegyzesACimmelKapcsolatban2", blank=True, null=True
    )  # Field name made lowercase.
    projektleiras = models.TextField(
        db_column="ProjektLeiras", blank=True, null=True
    )  # Field name made lowercase.
    felmeresteljesosszeg = models.TextField(
        db_column="FelmeresTeljesOsszeg", blank=True, null=True
    )  # Field name made lowercase.
    felmeres18000 = models.BigIntegerField(
        db_column="Felmeres18000", blank=True, null=True
    )  # Field name made lowercase.
    szervezetiterulet = models.TextField(
        db_column="SzervezetiTerulet", blank=True, null=True
    )  # Field name made lowercase.
    projektstart = models.TextField(
        db_column="ProjektStart", blank=True, null=True
    )  # Field name made lowercase.
    projektvege = models.TextField(
        db_column="ProjektVege", blank=True, null=True
    )  # Field name made lowercase.
    projektkoltsegenetto = models.TextField(
        db_column="ProjektKoltsegeNetto", blank=True, null=True
    )  # Field name made lowercase.
    havikoltsegnetto = models.TextField(
        db_column="HaviKoltsegNetto", blank=True, null=True
    )  # Field name made lowercase.
    kapcsolodolink1 = models.TextField(
        db_column="KapcsolodoLink1", blank=True, null=True
    )  # Field name made lowercase.
    kapcsolodolink2 = models.TextField(
        db_column="KapcsolodoLink2", blank=True, null=True
    )  # Field name made lowercase.
    ingatlanhasznalata = models.TextField(
        db_column="IngatlanHasznalata", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzescimmelkapcsolatban = models.TextField(
        db_column="MegjegyzesCimmelKapcsolatban", blank=True, null=True
    )  # Field name made lowercase.
    nemkapszgariszerzodest = models.BigIntegerField(
        db_column="NemKapszGariSzerzodest", blank=True, null=True
    )  # Field name made lowercase.
    beepitesdatuma = models.TextField(
        db_column="BeepitesDatuma", blank=True, null=True
    )  # Field name made lowercase.
    kepabeepiteshez01 = models.TextField(
        db_column="KepABeepiteshez01", blank=True, null=True
    )  # Field name made lowercase.
    kepabeepiteshez02 = models.TextField(
        db_column="KepABeepiteshez02", blank=True, null=True
    )  # Field name made lowercase.
    kepabeepiteshez03 = models.TextField(
        db_column="KepABeepiteshez03", blank=True, null=True
    )  # Field name made lowercase.
    kepabeepiteshez06 = models.TextField(
        db_column="KepABeepiteshez06", blank=True, null=True
    )  # Field name made lowercase.
    kepabeepiteshez07 = models.TextField(
        db_column="KepABeepiteshez07", blank=True, null=True
    )  # Field name made lowercase.
    hovakerul716os = models.TextField(
        db_column="HovaKerul716os", blank=True, null=True
    )  # Field name made lowercase.
    n716osszinehanemfeher = models.TextField(
        db_column="N716osSzineHaNemFeher", blank=True, null=True
    )  # Field name made lowercase.
    hovakerul916os = models.TextField(
        db_column="HovaKerul916os", blank=True, null=True
    )  # Field name made lowercase.
    n916osszinehanemfeher = models.TextField(
        db_column="N916osSzineHaNemFeher", blank=True, null=True
    )  # Field name made lowercase.
    kulonlegesszinhelyesovedostb2 = models.TextField(
        db_column="KulonlegesSzinHelyEsovedoStb2", blank=True, null=True
    )  # Field name made lowercase.
    holleszear201es2 = models.TextField(
        db_column="HolLeszEar201es2", blank=True, null=True
    )  # Field name made lowercase.
    holleszear200as2 = models.TextField(
        db_column="HolLeszEar200as2", blank=True, null=True
    )  # Field name made lowercase.
    kulonlegesszinhelyesovedostb3 = models.TextField(
        db_column="KulonlegesSzinHelyEsovedoStb3", blank=True, null=True
    )  # Field name made lowercase.
    osszesfalilegbevezetok2 = models.TextField(
        db_column="OsszesFaliLegbevezetok2", blank=True, null=True
    )  # Field name made lowercase.
    osszesenhanydb716916mind2 = models.TextField(
        db_column="OsszesenHanyDb716916Mind2", blank=True, null=True
    )  # Field name made lowercase.
    n716osdb2 = models.TextField(
        db_column="N716osDb2", blank=True, null=True
    )  # Field name made lowercase.
    n916osdb3 = models.TextField(
        db_column="N916osDb3", blank=True, null=True
    )  # Field name made lowercase.
    osszesenhanydb201200mind3 = models.TextField(
        db_column="OsszesenHanyDb201200Mind3", blank=True, null=True
    )  # Field name made lowercase.
    ear201esdb2 = models.TextField(
        db_column="Ear201esDb2", blank=True, null=True
    )  # Field name made lowercase.
    ear200asdb3 = models.TextField(
        db_column="Ear200asDb3", blank=True, null=True
    )  # Field name made lowercase.
    hanyajtofuras_0 = models.TextField(
        db_column="HanyAjtofuras", blank=True, null=True
    )  # Field name made lowercase. Field renamed because of name conflict.
    melyikajtok2 = models.TextField(
        db_column="MelyikAjtok2", blank=True, null=True
    )  # Field name made lowercase.
    ajtoszellozokarikaszinehanemfeher = models.TextField(
        db_column="AjtoszellozoKarikaSzineHaNemFeher", blank=True, null=True
    )  # Field name made lowercase.
    pluszvisszaaramlasgatlokdb2 = models.TextField(
        db_column="PluszVisszaaramlasGatlokDb2", blank=True, null=True
    )  # Field name made lowercase.
    hovakellapluszvisszaaramlasgatlo = models.TextField(
        db_column="HovaKellAPluszVisszaaramlasGatlo", blank=True, null=True
    )  # Field name made lowercase.
    egyebmunkakarajanlatonisrajtalesz = models.TextField(
        db_column="EgyebMunkakArajanlatonIsRajtaLesz", blank=True, null=True
    )  # Field name made lowercase.
    egyebmunkakcsakabeepitoklatjak2 = models.TextField(
        db_column="EgyebMunkakCsakABeepitokLatjak2", blank=True, null=True
    )  # Field name made lowercase.
    nyiltkazanjavan2 = models.BigIntegerField(
        db_column="NyiltKazanjaVan2", blank=True, null=True
    )  # Field name made lowercase.
    ahaznakkozpontiszellozoventilatoravan = models.BigIntegerField(
        db_column="AHaznakKozpontiSzellozoVentilatoraVan", blank=True, null=True
    )  # Field name made lowercase.
    hanyorasmunkaalapbeallitas36 = models.TextField(
        db_column="HanyOrasMunkaAlapBeallitas36", blank=True, null=True
    )  # Field name made lowercase.
    garanciavalarralkapcsolatosmegjegyzes2 = models.TextField(
        db_column="GaranciavalArralKapcsolatosMegjegyzes2", blank=True, null=True
    )  # Field name made lowercase.
    idoponttemaja = models.TextField(
        db_column="IdopontTemaja", blank=True, null=True
    )  # Field name made lowercase.
    file1590 = models.TextField(
        db_column="File1590", blank=True, null=True
    )  # Field name made lowercase.
    datetime1591 = models.TextField(
        db_column="DateTime1591", blank=True, null=True
    )  # Field name made lowercase.
    enum1592 = models.TextField(
        db_column="Enum1592", blank=True, null=True
    )  # Field name made lowercase.
    datetime1593 = models.TextField(
        db_column="DateTime1593", blank=True, null=True
    )  # Field name made lowercase.
    datetime1594 = models.TextField(
        db_column="DateTime1594", blank=True, null=True
    )  # Field name made lowercase.
    text1595 = models.TextField(
        db_column="Text1595", blank=True, null=True
    )  # Field name made lowercase.
    enum1596 = models.TextField(
        db_column="Enum1596", blank=True, null=True
    )  # Field name made lowercase.
    string1597 = models.TextField(
        db_column="String1597", blank=True, null=True
    )  # Field name made lowercase.
    datetime1598 = models.TextField(
        db_column="DateTime1598", blank=True, null=True
    )  # Field name made lowercase.
    float1599 = models.TextField(
        db_column="Float1599", blank=True, null=True
    )  # Field name made lowercase.
    datetime1600 = models.TextField(
        db_column="DateTime1600", blank=True, null=True
    )  # Field name made lowercase.
    file1601 = models.TextField(
        db_column="File1601", blank=True, null=True
    )  # Field name made lowercase.
    text1602 = models.TextField(
        db_column="Text1602", blank=True, null=True
    )  # Field name made lowercase.
    elolegosszege = models.TextField(
        db_column="ElolegOsszege", blank=True, null=True
    )  # Field name made lowercase.
    elolegfizetvedatum = models.TextField(
        db_column="ElolegFizetveDatum", blank=True, null=True
    )  # Field name made lowercase.
    vegszamlaosszege = models.TextField(
        db_column="VegszamlaOsszege", blank=True, null=True
    )  # Field name made lowercase.
    vegszamlafizetvedatum = models.TextField(
        db_column="VegszamlaFizetveDatum", blank=True, null=True
    )  # Field name made lowercase.
    felmeresdijbekerokikuldve = models.TextField(
        db_column="FelmeresDijbekeroKikuldve", blank=True, null=True
    )  # Field name made lowercase.
    mitvett = models.TextField(
        db_column="MitVett", blank=True, null=True
    )  # Field name made lowercase.
    feladatleirasabeepitoknek = models.TextField(
        db_column="FeladatLeirasaBeepitoknek", blank=True, null=True
    )  # Field name made lowercase.
    feladatleirasabeepitoknek2 = models.TextField(
        db_column="FeladatLeirasaBeepitoknek2", blank=True, null=True
    )  # Field name made lowercase.
    beepitesutanijegyzet = models.TextField(
        db_column="BeepitesUtaniJegyzet", blank=True, null=True
    )  # Field name made lowercase.
    holleszaventieshogyleszkialakitvaajanlatonezlatszik2 = models.TextField(
        db_column="HolLeszAVentiEsHogyLeszKialakitvaAjanlatonEzLatszik2",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    kialakitasrolegyebinfoabeepitoknek2 = models.TextField(
        db_column="KialakitasrolEgyebInfoABeepitoknek2", blank=True, null=True
    )  # Field name made lowercase.
    hakellcsoveznimibolmennyikell = models.TextField(
        db_column="HaKellCsovezniMibolMennyiKell", blank=True, null=True
    )  # Field name made lowercase.
    paraerzekelosbcx2 = models.TextField(
        db_column="ParaerzekelosBcx2", blank=True, null=True
    )  # Field name made lowercase.
    holleszaparaerzekelosbcx = models.TextField(
        db_column="HolLeszAParaerzekelosBcx", blank=True, null=True
    )  # Field name made lowercase.
    mozgaserzekelosbxc2 = models.TextField(
        db_column="MozgaserzekelosBxc2", blank=True, null=True
    )  # Field name made lowercase.
    holleszamozgaserzekelosbxc = models.TextField(
        db_column="HolLeszAMozgaserzekelosBxc", blank=True, null=True
    )  # Field name made lowercase.
    paraesmozgaserzekelosbxc2 = models.TextField(
        db_column="ParaEsMozgasErzekelosBxc2", blank=True, null=True
    )  # Field name made lowercase.
    holleszaparaesmozgaserzekelosbxc = models.TextField(
        db_column="HolLeszAParaEsMozgaserzekelosBxc", blank=True, null=True
    )  # Field name made lowercase.
    zsirszuro2 = models.TextField(
        db_column="Zsirszuro2", blank=True, null=True
    )  # Field name made lowercase.
    holleszazsirszuro = models.TextField(
        db_column="HolLeszAZsirszuro", blank=True, null=True
    )  # Field name made lowercase.
    garanciavalarralkapcsolatosmegjegyzes3 = models.TextField(
        db_column="GaranciavalArralKapcsolatosMegjegyzes3", blank=True, null=True
    )  # Field name made lowercase.
    hogyleszkialakitva = models.TextField(
        db_column="HogyLeszKialakitva", blank=True, null=True
    )  # Field name made lowercase.
    egyedikialakitas = models.TextField(
        db_column="EgyediKialakitas", blank=True, null=True
    )  # Field name made lowercase.
    hanydarabmfo = models.TextField(
        db_column="HanyDarabMfo", blank=True, null=True
    )  # Field name made lowercase.
    mfokivezeteshollesz = models.TextField(
        db_column="MfoKivezetesHolLesz", blank=True, null=True
    )  # Field name made lowercase.
    mashelyenbontas = models.TextField(
        db_column="MasHelyenBontas", blank=True, null=True
    )  # Field name made lowercase.
    felmeres2 = models.TextField(
        db_column="Felmeres2", blank=True, null=True
    )  # Field name made lowercase.
    melyikhelyisegbekerulub = models.TextField(
        db_column="MelyikHelyisegbeKerulUb", blank=True, null=True
    )  # Field name made lowercase.
    masodlagosventilatortipusa = models.TextField(
        db_column="MasodlagosVentilatorTipusa", blank=True, null=True
    )  # Field name made lowercase.
    masodlagosventilatorinfob = models.TextField(
        db_column="MasodlagosVentilatorInfoB", blank=True, null=True
    )  # Field name made lowercase.
    ajanlatertekenettohuf = models.TextField(
        db_column="AjanlatErtekeNettoHuf", blank=True, null=True
    )  # Field name made lowercase.
    ajanlatertekebrutto = models.TextField(
        db_column="AjanlatErtekeBrutto", blank=True, null=True
    )  # Field name made lowercase.
    emelet = models.TextField(
        db_column="Emelet", blank=True, null=True
    )  # Field name made lowercase.
    nyiltegesterukemenyesgazkazan2 = models.TextField(
        db_column="NyiltEgesteruKemenyesGazkazan2", blank=True, null=True
    )  # Field name made lowercase.
    kepabeepiteshez08 = models.TextField(
        db_column="KepABeepiteshez08", blank=True, null=True
    )  # Field name made lowercase.
    kepabeepiteshez09 = models.TextField(
        db_column="KepABeepiteshez09", blank=True, null=True
    )  # Field name made lowercase.
    masodlagosventilatorhelyeub = models.BigIntegerField(
        db_column="MasodlagosVentilatorHelyeUb", blank=True, null=True
    )  # Field name made lowercase.
    kozpontiventilatortipusa = models.TextField(
        db_column="KozpontiVentilatorTipusa", blank=True, null=True
    )  # Field name made lowercase.
    holleszaventi = models.TextField(
        db_column="HolLeszAVenti", blank=True, null=True
    )  # Field name made lowercase.
    afalatbontashelyeu = models.BigIntegerField(
        db_column="AFalAtbontasHelyeU", blank=True, null=True
    )  # Field name made lowercase.
    falatbontasdbu = models.TextField(
        db_column="FalAtbontasDbU", blank=True, null=True
    )  # Field name made lowercase.
    karikaszine = models.TextField(
        db_column="KarikaSzine", blank=True, null=True
    )  # Field name made lowercase.
    pluszvisszaaramlasgatlo = models.TextField(
        db_column="PluszVisszaaramlasGatlo", blank=True, null=True
    )  # Field name made lowercase.
    javitasdatum = models.TextField(
        db_column="JavitasDatum", blank=True, null=True
    )  # Field name made lowercase.
    tetoszellozocserep = models.BigIntegerField(
        db_column="TetoszellozoCserep", blank=True, null=True
    )  # Field name made lowercase.
    lemondtaabeepitest = models.BigIntegerField(
        db_column="LemondtaABeepitest", blank=True, null=True
    )  # Field name made lowercase.
    ajanlatafatartalma = models.TextField(
        db_column="AjanlatAfaTartalma", blank=True, null=True
    )  # Field name made lowercase.
    ajanlatsablontipusa = models.TextField(
        db_column="AjanlatSablonTipusa", blank=True, null=True
    )  # Field name made lowercase.
    emailsorozatotkert = models.BigIntegerField(
        db_column="EmailSorozatotKert", blank=True, null=True
    )  # Field name made lowercase.
    ajanlonevekampany = models.TextField(
        db_column="AjanloNeveKampany", blank=True, null=True
    )  # Field name made lowercase.
    string1679 = models.TextField(
        db_column="String1679", blank=True, null=True
    )  # Field name made lowercase.
    fizetendonetto18eft = models.TextField(
        db_column="FizetendoNetto18eFt", blank=True, null=True
    )  # Field name made lowercase.
    fizetendobrutto = models.TextField(
        db_column="FizetendoBrutto", blank=True, null=True
    )  # Field name made lowercase.
    passzivrendszer = models.BigIntegerField(
        db_column="PasszivRendszer", blank=True, null=True
    )  # Field name made lowercase.
    nyiltkazanjavan = models.BigIntegerField(
        db_column="NyiltKazanjaVan", blank=True, null=True
    )  # Field name made lowercase.
    ahaznakkoszpontiszellozoventilatoravan = models.BigIntegerField(
        db_column="Ahaznakkoszpontiszellozoventilatoravan", blank=True, null=True
    )  # Field name made lowercase.
    hirlevelrefeliratkozas2 = models.BigIntegerField(
        db_column="HirlevelreFeliratkozas2", blank=True, null=True
    )  # Field name made lowercase.
    gdprnyilatkozat2 = models.BigIntegerField(
        db_column="GdprNyilatkozat2", blank=True, null=True
    )  # Field name made lowercase.
    hogyantalaltrankajanloneve = models.TextField(
        db_column="HogyanTalaltRankAjanloNeve", blank=True, null=True
    )  # Field name made lowercase.
    kiepitettebe = models.BigIntegerField(
        db_column="KiEpitetteBe", blank=True, null=True
    )  # Field name made lowercase.
    nettobeepitesidij = models.TextField(
        db_column="NettoBeepitesiDij", blank=True, null=True
    )  # Field name made lowercase.
    penzugyilegrendezett = models.BigIntegerField(
        db_column="PenzugyilegRendezett", blank=True, null=True
    )  # Field name made lowercase.
    kepabeepiteshez010 = models.TextField(
        db_column="KepABeepiteshez010", blank=True, null=True
    )  # Field name made lowercase.
    set1698 = models.BigIntegerField(
        db_column="Set1698", blank=True, null=True
    )  # Field name made lowercase.
    hanyadikemelthanincslift = models.TextField(
        db_column="HanyadikEmeltHaNincsLift", blank=True, null=True
    )  # Field name made lowercase.
    melyikhelyisegbekerulu = models.TextField(
        db_column="MelyikHelyisegbeKerulU", blank=True, null=True
    )  # Field name made lowercase.
    hogyleszkialakitvau = models.TextField(
        db_column="HogyLeszKialakitvaU", blank=True, null=True
    )  # Field name made lowercase.
    egyedikialakitasu = models.TextField(
        db_column="EgyediKialakitasU", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzesacsovezeshez2 = models.TextField(
        db_column="MegjegyzesACsovezeshez2", blank=True, null=True
    )  # Field name made lowercase.
    qfahelye = models.TextField(
        db_column="QfaHelye", blank=True, null=True
    )  # Field name made lowercase.
    aram = models.TextField(
        db_column="Aram", blank=True, null=True
    )  # Field name made lowercase.
    aramegyedi = models.TextField(
        db_column="AramEgyedi", blank=True, null=True
    )  # Field name made lowercase.
    ventilatortipusau = models.TextField(
        db_column="VentilatorTipusaU", blank=True, null=True
    )  # Field name made lowercase.
    hanydarabventilatoru = models.TextField(
        db_column="HanyDarabVentilatorU", blank=True, null=True
    )  # Field name made lowercase.
    masodlagosventilatorhelyeu = models.BigIntegerField(
        db_column="MasodlagosVentilatorHelyeU", blank=True, null=True
    )  # Field name made lowercase.
    hogyleszkialakitvau2 = models.TextField(
        db_column="HogyLeszKialakitvaU2", blank=True, null=True
    )  # Field name made lowercase.
    egyedikialakitasu2 = models.TextField(
        db_column="EgyediKialakitasU2", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzesamasodlagosventilatorbeepitesehez = models.TextField(
        db_column="MegjegyzesAMasodlagosVentilatorBeepitesehez", blank=True, null=True
    )  # Field name made lowercase.
    holleszaventilatoru = models.TextField(
        db_column="HolLeszAVentilatorU", blank=True, null=True
    )  # Field name made lowercase.
    holleszaventilatoregyediu = models.TextField(
        db_column="HolLeszAVentilatorEgyediU", blank=True, null=True
    )  # Field name made lowercase.
    falatbontashelyeu = models.BigIntegerField(
        db_column="FalAtbontasHelyeU", blank=True, null=True
    )  # Field name made lowercase.
    falatbontashelyeegyediu = models.TextField(
        db_column="FalAtbontasHelyeEgyediU", blank=True, null=True
    )  # Field name made lowercase.
    tetoszellozocserep2 = models.BigIntegerField(
        db_column="TetoszellozoCserep2", blank=True, null=True
    )  # Field name made lowercase.
    emeletilakas = models.BigIntegerField(
        db_column="EmeletiLakas", blank=True, null=True
    )  # Field name made lowercase.
    hirlevelneltobbinfotkert = models.BigIntegerField(
        db_column="HirlevelnelTobbInfotKert", blank=True, null=True
    )  # Field name made lowercase.
    emailsorozat = models.BigIntegerField(
        db_column="EmailSorozat", blank=True, null=True
    )  # Field name made lowercase.
    egyebindok = models.TextField(
        db_column="EgyebIndok", blank=True, null=True
    )  # Field name made lowercase.
    fizetesimod = models.TextField(
        db_column="FizetesiMod", blank=True, null=True
    )  # Field name made lowercase.
    felmeresszamlas = models.BigIntegerField(
        db_column="FelmeresSzamlas", blank=True, null=True
    )  # Field name made lowercase.
    beepitesfizetesimod = models.TextField(
        db_column="BeepitesFizetesiMod", blank=True, null=True
    )  # Field name made lowercase.
    beepitesszamlas = models.BigIntegerField(
        db_column="BeepitesSzamlas", blank=True, null=True
    )  # Field name made lowercase.
    felmeresosszegeegyeb = models.TextField(
        db_column="FelmeresOsszegeEgyeb", blank=True, null=True
    )  # Field name made lowercase.
    bruttobeepitesidij = models.TextField(
        db_column="BruttoBeepitesiDij", blank=True, null=True
    )  # Field name made lowercase.
    garanciajavitasidopontja = models.TextField(
        db_column="GaranciaJavitasIdopontja", blank=True, null=True
    )  # Field name made lowercase.
    kepabeepiteshez011 = models.TextField(
        db_column="KepABeepiteshez011", blank=True, null=True
    )  # Field name made lowercase.
    kepabeepiteshez012 = models.TextField(
        db_column="KepABeepiteshez012", blank=True, null=True
    )  # Field name made lowercase.
    kepabeepiteshez10 = models.TextField(
        db_column="KepABeepiteshez10", blank=True, null=True
    )  # Field name made lowercase.
    enum1740 = models.TextField(
        db_column="Enum1740", blank=True, null=True
    )  # Field name made lowercase.
    enum1741 = models.TextField(
        db_column="Enum1741", blank=True, null=True
    )  # Field name made lowercase.
    enum1742 = models.TextField(
        db_column="Enum1742", blank=True, null=True
    )  # Field name made lowercase.
    text1743 = models.TextField(
        db_column="Text1743", blank=True, null=True
    )  # Field name made lowercase.
    milyenproblemavalfordulthozzank = models.TextField(
        db_column="MilyenProblemavalFordultHozzank", blank=True, null=True
    )  # Field name made lowercase.
    file1763 = models.TextField(
        db_column="File1763", blank=True, null=True
    )  # Field name made lowercase.
    int1764 = models.TextField(
        db_column="Int1764", blank=True, null=True
    )  # Field name made lowercase.
    datetime1765 = models.TextField(
        db_column="DateTime1765", blank=True, null=True
    )  # Field name made lowercase.
    float1766 = models.TextField(
        db_column="Float1766", blank=True, null=True
    )  # Field name made lowercase.
    enum1767 = models.TextField(
        db_column="Enum1767", blank=True, null=True
    )  # Field name made lowercase.
    datetime1768 = models.TextField(
        db_column="DateTime1768", blank=True, null=True
    )  # Field name made lowercase.
    enum1769 = models.TextField(
        db_column="Enum1769", blank=True, null=True
    )  # Field name made lowercase.
    text1770 = models.TextField(
        db_column="Text1770", blank=True, null=True
    )  # Field name made lowercase.
    datetime1771 = models.TextField(
        db_column="DateTime1771", blank=True, null=True
    )  # Field name made lowercase.
    set1772 = models.BigIntegerField(
        db_column="Set1772", blank=True, null=True
    )  # Field name made lowercase.
    set1773 = models.BigIntegerField(
        db_column="Set1773", blank=True, null=True
    )  # Field name made lowercase.
    set1774 = models.BigIntegerField(
        db_column="Set1774", blank=True, null=True
    )  # Field name made lowercase.
    enum1775 = models.TextField(
        db_column="Enum1775", blank=True, null=True
    )  # Field name made lowercase.
    text1776 = models.TextField(
        db_column="Text1776", blank=True, null=True
    )  # Field name made lowercase.
    enum1777 = models.TextField(
        db_column="Enum1777", blank=True, null=True
    )  # Field name made lowercase.
    enum1778 = models.TextField(
        db_column="Enum1778", blank=True, null=True
    )  # Field name made lowercase.
    set1779 = models.BigIntegerField(
        db_column="Set1779", blank=True, null=True
    )  # Field name made lowercase.
    enum1780 = models.TextField(
        db_column="Enum1780", blank=True, null=True
    )  # Field name made lowercase.
    enum1781 = models.TextField(
        db_column="Enum1781", blank=True, null=True
    )  # Field name made lowercase.
    file1782 = models.TextField(
        db_column="File1782", blank=True, null=True
    )  # Field name made lowercase.
    int1783 = models.TextField(
        db_column="Int1783", blank=True, null=True
    )  # Field name made lowercase.
    float1784 = models.TextField(
        db_column="Float1784", blank=True, null=True
    )  # Field name made lowercase.
    datetime1785 = models.TextField(
        db_column="DateTime1785", blank=True, null=True
    )  # Field name made lowercase.
    string1786 = models.TextField(
        db_column="String1786", blank=True, null=True
    )  # Field name made lowercase.
    enum1787 = models.TextField(
        db_column="Enum1787", blank=True, null=True
    )  # Field name made lowercase.
    set1788 = models.BigIntegerField(
        db_column="Set1788", blank=True, null=True
    )  # Field name made lowercase.
    enum1789 = models.TextField(
        db_column="Enum1789", blank=True, null=True
    )  # Field name made lowercase.
    int1790 = models.TextField(
        db_column="Int1790", blank=True, null=True
    )  # Field name made lowercase.
    text1791 = models.TextField(
        db_column="Text1791", blank=True, null=True
    )  # Field name made lowercase.
    datetime1792 = models.TextField(
        db_column="DateTime1792", blank=True, null=True
    )  # Field name made lowercase.
    set1793 = models.BigIntegerField(
        db_column="Set1793", blank=True, null=True
    )  # Field name made lowercase.
    int1794 = models.TextField(
        db_column="Int1794", blank=True, null=True
    )  # Field name made lowercase.
    enum1795 = models.TextField(
        db_column="Enum1795", blank=True, null=True
    )  # Field name made lowercase.
    enum1796 = models.TextField(
        db_column="Enum1796", blank=True, null=True
    )  # Field name made lowercase.
    enum1797 = models.TextField(
        db_column="Enum1797", blank=True, null=True
    )  # Field name made lowercase.
    enum1798 = models.TextField(
        db_column="Enum1798", blank=True, null=True
    )  # Field name made lowercase.
    enum1799 = models.TextField(
        db_column="Enum1799", blank=True, null=True
    )  # Field name made lowercase.
    datetime1800 = models.TextField(
        db_column="DateTime1800", blank=True, null=True
    )  # Field name made lowercase.
    enum1801 = models.TextField(
        db_column="Enum1801", blank=True, null=True
    )  # Field name made lowercase.
    enum1802 = models.TextField(
        db_column="Enum1802", blank=True, null=True
    )  # Field name made lowercase.
    text1803 = models.TextField(
        db_column="Text1803", blank=True, null=True
    )  # Field name made lowercase.
    int1804 = models.TextField(
        db_column="Int1804", blank=True, null=True
    )  # Field name made lowercase.
    int1805 = models.TextField(
        db_column="Int1805", blank=True, null=True
    )  # Field name made lowercase.
    enum1806 = models.TextField(
        db_column="Enum1806", blank=True, null=True
    )  # Field name made lowercase.
    enum1807 = models.TextField(
        db_column="Enum1807", blank=True, null=True
    )  # Field name made lowercase.
    file1808 = models.TextField(
        db_column="File1808", blank=True, null=True
    )  # Field name made lowercase.
    text1809 = models.TextField(
        db_column="Text1809", blank=True, null=True
    )  # Field name made lowercase.
    string1810 = models.TextField(
        db_column="String1810", blank=True, null=True
    )  # Field name made lowercase.
    datetime1811 = models.TextField(
        db_column="DateTime1811", blank=True, null=True
    )  # Field name made lowercase.
    file1812 = models.TextField(
        db_column="File1812", blank=True, null=True
    )  # Field name made lowercase.
    enum1813 = models.TextField(
        db_column="Enum1813", blank=True, null=True
    )  # Field name made lowercase.
    string1814 = models.TextField(
        db_column="String1814", blank=True, null=True
    )  # Field name made lowercase.
    float1815 = models.TextField(
        db_column="Float1815", blank=True, null=True
    )  # Field name made lowercase.
    datetime1816 = models.TextField(
        db_column="DateTime1816", blank=True, null=True
    )  # Field name made lowercase.
    datetime1817 = models.TextField(
        db_column="DateTime1817", blank=True, null=True
    )  # Field name made lowercase.
    file1818 = models.TextField(
        db_column="File1818", blank=True, null=True
    )  # Field name made lowercase.
    file1819 = models.TextField(
        db_column="File1819", blank=True, null=True
    )  # Field name made lowercase.
    file1820 = models.TextField(
        db_column="File1820", blank=True, null=True
    )  # Field name made lowercase.
    file1821 = models.TextField(
        db_column="File1821", blank=True, null=True
    )  # Field name made lowercase.
    enum1822 = models.TextField(
        db_column="Enum1822", blank=True, null=True
    )  # Field name made lowercase.
    enum1823 = models.TextField(
        db_column="Enum1823", blank=True, null=True
    )  # Field name made lowercase.
    enum1824 = models.TextField(
        db_column="Enum1824", blank=True, null=True
    )  # Field name made lowercase.
    enum1825 = models.TextField(
        db_column="Enum1825", blank=True, null=True
    )  # Field name made lowercase.
    text1826 = models.TextField(
        db_column="Text1826", blank=True, null=True
    )  # Field name made lowercase.
    text1827 = models.TextField(
        db_column="Text1827", blank=True, null=True
    )  # Field name made lowercase.
    text1828 = models.TextField(
        db_column="Text1828", blank=True, null=True
    )  # Field name made lowercase.
    file1829 = models.TextField(
        db_column="File1829", blank=True, null=True
    )  # Field name made lowercase.
    text1830 = models.TextField(
        db_column="Text1830", blank=True, null=True
    )  # Field name made lowercase.
    text1831 = models.TextField(
        db_column="Text1831", blank=True, null=True
    )  # Field name made lowercase.
    enum1832 = models.TextField(
        db_column="Enum1832", blank=True, null=True
    )  # Field name made lowercase.
    enum1833 = models.TextField(
        db_column="Enum1833", blank=True, null=True
    )  # Field name made lowercase.
    datetime1834 = models.TextField(
        db_column="DateTime1834", blank=True, null=True
    )  # Field name made lowercase.
    int1835 = models.TextField(
        db_column="Int1835", blank=True, null=True
    )  # Field name made lowercase.
    float1836 = models.TextField(
        db_column="Float1836", blank=True, null=True
    )  # Field name made lowercase.
    enum1837 = models.TextField(
        db_column="Enum1837", blank=True, null=True
    )  # Field name made lowercase.
    text1838 = models.TextField(
        db_column="Text1838", blank=True, null=True
    )  # Field name made lowercase.
    enum1839 = models.TextField(
        db_column="Enum1839", blank=True, null=True
    )  # Field name made lowercase.
    enum1840 = models.TextField(
        db_column="Enum1840", blank=True, null=True
    )  # Field name made lowercase.
    file1841 = models.TextField(
        db_column="File1841", blank=True, null=True
    )  # Field name made lowercase.
    enum1842 = models.TextField(
        db_column="Enum1842", blank=True, null=True
    )  # Field name made lowercase.
    datetime1843 = models.TextField(
        db_column="DateTime1843", blank=True, null=True
    )  # Field name made lowercase.
    datetime1844 = models.TextField(
        db_column="DateTime1844", blank=True, null=True
    )  # Field name made lowercase.
    file1845 = models.TextField(
        db_column="File1845", blank=True, null=True
    )  # Field name made lowercase.
    enum1846 = models.TextField(
        db_column="Enum1846", blank=True, null=True
    )  # Field name made lowercase.
    enum1847 = models.TextField(
        db_column="Enum1847", blank=True, null=True
    )  # Field name made lowercase.
    enum1848 = models.TextField(
        db_column="Enum1848", blank=True, null=True
    )  # Field name made lowercase.
    enum1849 = models.TextField(
        db_column="Enum1849", blank=True, null=True
    )  # Field name made lowercase.
    enum1850 = models.TextField(
        db_column="Enum1850", blank=True, null=True
    )  # Field name made lowercase.
    file1851 = models.TextField(
        db_column="File1851", blank=True, null=True
    )  # Field name made lowercase.
    enum1852 = models.TextField(
        db_column="Enum1852", blank=True, null=True
    )  # Field name made lowercase.
    enum1853 = models.TextField(
        db_column="Enum1853", blank=True, null=True
    )  # Field name made lowercase.
    enum1854 = models.TextField(
        db_column="Enum1854", blank=True, null=True
    )  # Field name made lowercase.
    file1855 = models.TextField(
        db_column="File1855", blank=True, null=True
    )  # Field name made lowercase.
    enum1856 = models.TextField(
        db_column="Enum1856", blank=True, null=True
    )  # Field name made lowercase.
    enum1857 = models.TextField(
        db_column="Enum1857", blank=True, null=True
    )  # Field name made lowercase.
    int1858 = models.TextField(
        db_column="Int1858", blank=True, null=True
    )  # Field name made lowercase.
    datetime1859 = models.TextField(
        db_column="DateTime1859", blank=True, null=True
    )  # Field name made lowercase.
    int1860 = models.TextField(
        db_column="Int1860", blank=True, null=True
    )  # Field name made lowercase.
    float1861 = models.TextField(
        db_column="Float1861", blank=True, null=True
    )  # Field name made lowercase.
    enum1862 = models.TextField(
        db_column="Enum1862", blank=True, null=True
    )  # Field name made lowercase.
    file1863 = models.TextField(
        db_column="File1863", blank=True, null=True
    )  # Field name made lowercase.
    datetime1864 = models.TextField(
        db_column="DateTime1864", blank=True, null=True
    )  # Field name made lowercase.
    string1865 = models.TextField(
        db_column="String1865", blank=True, null=True
    )  # Field name made lowercase.
    string1866 = models.TextField(
        db_column="String1866", blank=True, null=True
    )  # Field name made lowercase.
    file1867 = models.TextField(
        db_column="File1867", blank=True, null=True
    )  # Field name made lowercase.
    file1868 = models.TextField(
        db_column="File1868", blank=True, null=True
    )  # Field name made lowercase.
    text1869 = models.TextField(
        db_column="Text1869", blank=True, null=True
    )  # Field name made lowercase.
    file1870 = models.TextField(
        db_column="File1870", blank=True, null=True
    )  # Field name made lowercase.
    enum1871 = models.TextField(
        db_column="Enum1871", blank=True, null=True
    )  # Field name made lowercase.
    enum1872 = models.TextField(
        db_column="Enum1872", blank=True, null=True
    )  # Field name made lowercase.
    datetime1873 = models.TextField(
        db_column="DateTime1873", blank=True, null=True
    )  # Field name made lowercase.
    datetime1874 = models.TextField(
        db_column="DateTime1874", blank=True, null=True
    )  # Field name made lowercase.
    set1875 = models.BigIntegerField(
        db_column="Set1875", blank=True, null=True
    )  # Field name made lowercase.
    text1876 = models.TextField(
        db_column="Text1876", blank=True, null=True
    )  # Field name made lowercase.
    datetime1877 = models.TextField(
        db_column="DateTime1877", blank=True, null=True
    )  # Field name made lowercase.
    datetime1878 = models.TextField(
        db_column="DateTime1878", blank=True, null=True
    )  # Field name made lowercase.
    int1879 = models.TextField(
        db_column="Int1879", blank=True, null=True
    )  # Field name made lowercase.
    float1880 = models.TextField(
        db_column="Float1880", blank=True, null=True
    )  # Field name made lowercase.
    file1881 = models.TextField(
        db_column="File1881", blank=True, null=True
    )  # Field name made lowercase.
    file1882 = models.TextField(
        db_column="File1882", blank=True, null=True
    )  # Field name made lowercase.
    enum1883 = models.TextField(
        db_column="Enum1883", blank=True, null=True
    )  # Field name made lowercase.
    float1884 = models.TextField(
        db_column="Float1884", blank=True, null=True
    )  # Field name made lowercase.
    float1885 = models.TextField(
        db_column="Float1885", blank=True, null=True
    )  # Field name made lowercase.
    string1886 = models.TextField(
        db_column="String1886", blank=True, null=True
    )  # Field name made lowercase.
    file1887 = models.TextField(
        db_column="File1887", blank=True, null=True
    )  # Field name made lowercase.
    text1888 = models.TextField(
        db_column="Text1888", blank=True, null=True
    )  # Field name made lowercase.
    text1889 = models.TextField(
        db_column="Text1889", blank=True, null=True
    )  # Field name made lowercase.
    set1890 = models.BigIntegerField(
        db_column="Set1890", blank=True, null=True
    )  # Field name made lowercase.
    set1891 = models.BigIntegerField(
        db_column="Set1891", blank=True, null=True
    )  # Field name made lowercase.
    file1892 = models.TextField(
        db_column="File1892", blank=True, null=True
    )  # Field name made lowercase.
    file1893 = models.TextField(
        db_column="File1893", blank=True, null=True
    )  # Field name made lowercase.
    file1894 = models.TextField(
        db_column="File1894", blank=True, null=True
    )  # Field name made lowercase.
    enum1895 = models.TextField(
        db_column="Enum1895", blank=True, null=True
    )  # Field name made lowercase.
    enum1896 = models.TextField(
        db_column="Enum1896", blank=True, null=True
    )  # Field name made lowercase.
    datetime1897 = models.TextField(
        db_column="DateTime1897", blank=True, null=True
    )  # Field name made lowercase.
    int1898 = models.TextField(
        db_column="Int1898", blank=True, null=True
    )  # Field name made lowercase.
    float1899 = models.TextField(
        db_column="Float1899", blank=True, null=True
    )  # Field name made lowercase.
    enum1900 = models.TextField(
        db_column="Enum1900", blank=True, null=True
    )  # Field name made lowercase.
    file1901 = models.TextField(
        db_column="File1901", blank=True, null=True
    )  # Field name made lowercase.
    datetime1902 = models.TextField(
        db_column="DateTime1902", blank=True, null=True
    )  # Field name made lowercase.
    datetime1903 = models.TextField(
        db_column="DateTime1903", blank=True, null=True
    )  # Field name made lowercase.
    string1904 = models.TextField(
        db_column="String1904", blank=True, null=True
    )  # Field name made lowercase.
    file1905 = models.TextField(
        db_column="File1905", blank=True, null=True
    )  # Field name made lowercase.
    text1906 = models.TextField(
        db_column="Text1906", blank=True, null=True
    )  # Field name made lowercase.
    file1907 = models.TextField(
        db_column="File1907", blank=True, null=True
    )  # Field name made lowercase.
    file1908 = models.TextField(
        db_column="File1908", blank=True, null=True
    )  # Field name made lowercase.
    datetime1909 = models.TextField(
        db_column="DateTime1909", blank=True, null=True
    )  # Field name made lowercase.
    string1910 = models.TextField(
        db_column="String1910", blank=True, null=True
    )  # Field name made lowercase.
    enum1911 = models.TextField(
        db_column="Enum1911", blank=True, null=True
    )  # Field name made lowercase.
    int1912 = models.TextField(
        db_column="Int1912", blank=True, null=True
    )  # Field name made lowercase.
    enum1913 = models.TextField(
        db_column="Enum1913", blank=True, null=True
    )  # Field name made lowercase.
    file1914 = models.TextField(
        db_column="File1914", blank=True, null=True
    )  # Field name made lowercase.
    float1915 = models.TextField(
        db_column="Float1915", blank=True, null=True
    )  # Field name made lowercase.
    float1916 = models.TextField(
        db_column="Float1916", blank=True, null=True
    )  # Field name made lowercase.
    float1917 = models.TextField(
        db_column="Float1917", blank=True, null=True
    )  # Field name made lowercase.
    enum1918 = models.TextField(
        db_column="Enum1918", blank=True, null=True
    )  # Field name made lowercase.
    enum1919 = models.TextField(
        db_column="Enum1919", blank=True, null=True
    )  # Field name made lowercase.
    enum1920 = models.TextField(
        db_column="Enum1920", blank=True, null=True
    )  # Field name made lowercase.
    enum1921 = models.TextField(
        db_column="Enum1921", blank=True, null=True
    )  # Field name made lowercase.
    enum1922 = models.TextField(
        db_column="Enum1922", blank=True, null=True
    )  # Field name made lowercase.
    datetime1923 = models.TextField(
        db_column="DateTime1923", blank=True, null=True
    )  # Field name made lowercase.
    string1924 = models.TextField(
        db_column="String1924", blank=True, null=True
    )  # Field name made lowercase.
    enum1925 = models.TextField(
        db_column="Enum1925", blank=True, null=True
    )  # Field name made lowercase.
    float1926 = models.TextField(
        db_column="Float1926", blank=True, null=True
    )  # Field name made lowercase.
    datetime1927 = models.TextField(
        db_column="DateTime1927", blank=True, null=True
    )  # Field name made lowercase.
    enum1928 = models.TextField(
        db_column="Enum1928", blank=True, null=True
    )  # Field name made lowercase.
    datetime1929 = models.TextField(
        db_column="DateTime1929", blank=True, null=True
    )  # Field name made lowercase.
    file1930 = models.TextField(
        db_column="File1930", blank=True, null=True
    )  # Field name made lowercase.
    file1931 = models.TextField(
        db_column="File1931", blank=True, null=True
    )  # Field name made lowercase.
    file1932 = models.TextField(
        db_column="File1932", blank=True, null=True
    )  # Field name made lowercase.
    int1933 = models.TextField(
        db_column="Int1933", blank=True, null=True
    )  # Field name made lowercase.
    float1934 = models.TextField(
        db_column="Float1934", blank=True, null=True
    )  # Field name made lowercase.
    enum1935 = models.TextField(
        db_column="Enum1935", blank=True, null=True
    )  # Field name made lowercase.
    enum1936 = models.TextField(
        db_column="Enum1936", blank=True, null=True
    )  # Field name made lowercase.
    float1937 = models.TextField(
        db_column="Float1937", blank=True, null=True
    )  # Field name made lowercase.
    datetime1938 = models.TextField(
        db_column="DateTime1938", blank=True, null=True
    )  # Field name made lowercase.
    float1939 = models.TextField(
        db_column="Float1939", blank=True, null=True
    )  # Field name made lowercase.
    float1940 = models.TextField(
        db_column="Float1940", blank=True, null=True
    )  # Field name made lowercase.
    file1941 = models.TextField(
        db_column="File1941", blank=True, null=True
    )  # Field name made lowercase.
    text1942 = models.TextField(
        db_column="Text1942", blank=True, null=True
    )  # Field name made lowercase.
    float1944 = models.TextField(
        db_column="Float1944", blank=True, null=True
    )  # Field name made lowercase.
    datetime1945 = models.TextField(
        db_column="DateTime1945", blank=True, null=True
    )  # Field name made lowercase.
    enum1951 = models.TextField(
        db_column="Enum1951", blank=True, null=True
    )  # Field name made lowercase.
    datetime1953 = models.TextField(
        db_column="DateTime1953", blank=True, null=True
    )  # Field name made lowercase.
    elutasitasoka = models.BigIntegerField(
        db_column="ElutasitasOka", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzesleiras = models.TextField(
        db_column="MegjegyzesLeiras", blank=True, null=True
    )  # Field name made lowercase.
    felmeresikepek = models.TextField(
        db_column="FelmeresiKepek", blank=True, null=True
    )  # Field name made lowercase.
    enum1969 = models.TextField(
        db_column="Enum1969", blank=True, null=True
    )  # Field name made lowercase.
    text1970 = models.TextField(
        db_column="Text1970", blank=True, null=True
    )  # Field name made lowercase.
    milyenmasproblema = models.BigIntegerField(
        db_column="MilyenMasProblema", blank=True, null=True
    )  # Field name made lowercase.
    tavolsag = models.TextField(
        db_column="Tavolsag", blank=True, null=True
    )  # Field name made lowercase.
    felmeresidij = models.TextField(
        db_column="FelmeresiDij", blank=True, null=True
    )  # Field name made lowercase.
    felmeresidopontja2 = models.TextField(
        db_column="FelmeresIdopontja2", blank=True, null=True
    )  # Field name made lowercase.
    miazugyfelfoszempontja3 = models.TextField(
        db_column="MiAzUgyfelFoSzempontja3", blank=True, null=True
    )  # Field name made lowercase.
    egyebszempontok3 = models.BigIntegerField(
        db_column="EgyebSzempontok3", blank=True, null=True
    )  # Field name made lowercase.
    cim2 = models.TextField(
        db_column="Cim2", blank=True, null=True
    )  # Field name made lowercase.
    utazasiidokozponttol = models.TextField(
        db_column="UtazasiIdoKozponttol", blank=True, null=True
    )  # Field name made lowercase.
    mehetadijbekero = models.TextField(
        db_column="MehetADijbekero", blank=True, null=True
    )  # Field name made lowercase.
    dijbekeromegjegyzes = models.TextField(
        db_column="DijbekeroMegjegyzes", blank=True, null=True
    )  # Field name made lowercase.
    dijbekeroszama = models.TextField(
        db_column="DijbekeroSzama", blank=True, null=True
    )  # Field name made lowercase.
    dijbekeropdf = models.TextField(
        db_column="DijbekeroPdf", blank=True, null=True
    )  # Field name made lowercase.
    felmero = models.TextField(
        db_column="Felmero", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzesamunkalapra = models.TextField(
        db_column="MegjegyzesAMunkalapra", blank=True, null=True
    )  # Field name made lowercase.
    szovegesertekeles = models.TextField(
        db_column="SzovegesErtekeles", blank=True, null=True
    )  # Field name made lowercase.
    pontszam = models.TextField(
        db_column="Pontszam", blank=True, null=True
    )  # Field name made lowercase.
    szovegesertekeles2 = models.TextField(
        db_column="SzovegesErtekeles2", blank=True, null=True
    )  # Field name made lowercase.
    text2006 = models.TextField(
        db_column="Text2006", blank=True, null=True
    )  # Field name made lowercase.
    enum2007 = models.TextField(
        db_column="Enum2007", blank=True, null=True
    )  # Field name made lowercase.
    datetime2008 = models.TextField(
        db_column="DateTime2008", blank=True, null=True
    )  # Field name made lowercase.
    enum2009 = models.TextField(
        db_column="Enum2009", blank=True, null=True
    )  # Field name made lowercase.
    beepitok = models.BigIntegerField(
        db_column="Beepitok", blank=True, null=True
    )  # Field name made lowercase.
    enum2016 = models.TextField(
        db_column="Enum2016", blank=True, null=True
    )  # Field name made lowercase.
    text2017 = models.TextField(
        db_column="Text2017", blank=True, null=True
    )  # Field name made lowercase.
    file2018 = models.TextField(
        db_column="File2018", blank=True, null=True
    )  # Field name made lowercase.
    enum2019 = models.TextField(
        db_column="Enum2019", blank=True, null=True
    )  # Field name made lowercase.
    set2020 = models.BigIntegerField(
        db_column="Set2020", blank=True, null=True
    )  # Field name made lowercase.
    datetime2021 = models.TextField(
        db_column="DateTime2021", blank=True, null=True
    )  # Field name made lowercase.
    datetime2022 = models.TextField(
        db_column="DateTime2022", blank=True, null=True
    )  # Field name made lowercase.
    enum2023 = models.TextField(
        db_column="Enum2023", blank=True, null=True
    )  # Field name made lowercase.
    file2024 = models.TextField(
        db_column="File2024", blank=True, null=True
    )  # Field name made lowercase.
    miertlettsikertelenabeepites = models.TextField(
        db_column="MiertLettSikertelenABeepites", blank=True, null=True
    )  # Field name made lowercase.
    miertlettsikertelenabeepitesszovegesen = models.TextField(
        db_column="MiertLettSikertelenABeepitesSzovegesen", blank=True, null=True
    )  # Field name made lowercase.
    mennyirevoltmegelegedve = models.TextField(
        db_column="MennyireVoltMegelegedve", blank=True, null=True
    )  # Field name made lowercase.
    pontszam2 = models.TextField(
        db_column="Pontszam2", blank=True, null=True
    )  # Field name made lowercase.
    szovegesertekeles3 = models.TextField(
        db_column="SzovegesErtekeles3", blank=True, null=True
    )  # Field name made lowercase.
    alaprajz = models.TextField(
        db_column="Alaprajz", blank=True, null=True
    )  # Field name made lowercase.
    lezarasoka = models.BigIntegerField(
        db_column="LezarasOka", blank=True, null=True
    )  # Field name made lowercase.
    lezarasszovegesen = models.TextField(
        db_column="LezarasSzovegesen", blank=True, null=True
    )  # Field name made lowercase.
    telepules = models.TextField(
        db_column="Telepules", blank=True, null=True
    )  # Field name made lowercase.
    iranyitoszam = models.TextField(
        db_column="Iranyitoszam", blank=True, null=True
    )  # Field name made lowercase.
    forras = models.TextField(
        db_column="Forras", blank=True, null=True
    )  # Field name made lowercase.
    megye = models.TextField(
        db_column="Megye", blank=True, null=True
    )  # Field name made lowercase.
    orszag = models.TextField(
        db_column="Orszag", blank=True, null=True
    )  # Field name made lowercase.
    felmeresidopontja3 = models.TextField(
        db_column="FelmeresIdopontja3", blank=True, null=True
    )  # Field name made lowercase.
    milyenrendszerttervezel = models.TextField(
        db_column="MilyenRendszertTervezel", blank=True, null=True
    )  # Field name made lowercase.
    milyenventilatorttervezel = models.TextField(
        db_column="MilyenVentilatortTervezel", blank=True, null=True
    )  # Field name made lowercase.
    hanydarabventilatorttervezel = models.TextField(
        db_column="HanyDarabVentilatortTervezel", blank=True, null=True
    )  # Field name made lowercase.
    qfahelye2 = models.TextField(
        db_column="QfaHelye2", blank=True, null=True
    )  # Field name made lowercase.
    melyikhelyisegbekerulhelyi = models.TextField(
        db_column="MelyikHelyisegbeKerulHelyi", blank=True, null=True
    )  # Field name made lowercase.
    elektromosbekotes = models.TextField(
        db_column="ElektromosBekotes", blank=True, null=True
    )  # Field name made lowercase.
    milyenventillatorttervezel = models.TextField(
        db_column="MilyenVentillatortTervezel", blank=True, null=True
    )  # Field name made lowercase.
    melyikhelyisegbekerulkozpontifalattoreses = models.TextField(
        db_column="MelyikHelyisegbeKerulKozpontiFalattoreses", blank=True, null=True
    )  # Field name made lowercase.
    melyikhelyisegbekerulkozpontimeglevoventilatorhelyere = models.TextField(
        db_column="MelyikHelyisegbeKerulKozpontiMeglevoVentilatorHelyere",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    melyikhelyisegbekerulkozpontituzfalonkivezetve = models.TextField(
        db_column="MelyikHelyisegbeKerulKozpontiTuzfalonKivezetve",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    melyikhelyisegbekerulkozpontimennyezetre = models.TextField(
        db_column="MelyikHelyisegbeKerulKozpontiMennyezetre", blank=True, null=True
    )  # Field name made lowercase.
    elektromosbekoteskozponti = models.TextField(
        db_column="ElektromosBekotesKozponti", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzeskozponti = models.TextField(
        db_column="MegjegyzesKozponti", blank=True, null=True
    )  # Field name made lowercase.
    tipusdbvorticemfo = models.TextField(
        db_column="TipusdbVorticeMfo", blank=True, null=True
    )  # Field name made lowercase.
    tipusdbawentakw100t = models.TextField(
        db_column="TipusdbAwentaKw100t", blank=True, null=True
    )  # Field name made lowercase.
    tipusdbvents100 = models.TextField(
        db_column="TipusdbVents100", blank=True, null=True
    )  # Field name made lowercase.
    tipusdbsor6 = models.TextField(
        db_column="TipusdbSor6", blank=True, null=True
    )  # Field name made lowercase.
    melyikhelyisegbekerulmasodlagosfalattoreses = models.TextField(
        db_column="MelyikHelyisegbeKerulMasodlagosFalattoreses", blank=True, null=True
    )  # Field name made lowercase.
    melyikhelyisegbekerulmasodlagosmeglevoszellozohelyere = models.TextField(
        db_column="MelyikHelyisegbeKerulMasodlagosMeglevoSzellozoHelyere",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    melyikhelyisegbekerulmasodlagosmeglevoventilator = models.TextField(
        db_column="MelyikHelyisegbeKerulMasodlagosMeglevoVentilator",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    melyikhelyisegbekerulmasodlagostetonkeresztulkivezetve = models.TextField(
        db_column="MelyikHelyisegbeKerulMasodlagosTetonKeresztulKivezetve",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    melyikhelyisegbekerulmasodlagostuzfalonkivezetve = models.TextField(
        db_column="MelyikHelyisegbeKerulMasodlagosTuzfalonKivezetve",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    melyikhelyisegbekerulmasodlagosmennyezetre = models.TextField(
        db_column="MelyikHelyisegbeKerulMasodlagosMennyezetre", blank=True, null=True
    )  # Field name made lowercase.
    elektromosbekotesmasodlagos = models.TextField(
        db_column="ElektromosBekotesMasodlagos", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzesmasodlagos = models.TextField(
        db_column="MegjegyzesMasodlagos", blank=True, null=True
    )  # Field name made lowercase.
    helyefurdoszoba = models.TextField(
        db_column="HelyeFurdoszoba", blank=True, null=True
    )  # Field name made lowercase.
    helyekonyha = models.TextField(
        db_column="HelyeKonyha", blank=True, null=True
    )  # Field name made lowercase.
    helyewc = models.TextField(
        db_column="HelyeWc", blank=True, null=True
    )  # Field name made lowercase.
    helyemosokonyha = models.TextField(
        db_column="HelyeMosokonyha", blank=True, null=True
    )  # Field name made lowercase.
    helyekisebbfurdoszoba = models.TextField(
        db_column="HelyeKisebbFurdoszoba", blank=True, null=True
    )  # Field name made lowercase.
    helyenagyobbfurdoszoba = models.TextField(
        db_column="HelyeNagyobbFurdoszoba", blank=True, null=True
    )  # Field name made lowercase.
    helyeemeletifurdoszoba = models.TextField(
        db_column="HelyeEmeletiFurdoszoba", blank=True, null=True
    )  # Field name made lowercase.
    helyefoldszintifurdoszoba = models.TextField(
        db_column="HelyeFoldszintiFurdoszoba", blank=True, null=True
    )  # Field name made lowercase.
    helye2furdoszobaba = models.TextField(
        db_column="Helye2Furdoszobaba", blank=True, null=True
    )  # Field name made lowercase.
    helye3furdoszobaba = models.TextField(
        db_column="Helye3Furdoszobaba", blank=True, null=True
    )  # Field name made lowercase.
    egyebmegjegyzeslegelvezeto = models.TextField(
        db_column="EgyebMegjegyzesLegelvezeto", blank=True, null=True
    )  # Field name made lowercase.
    d100pvc = models.TextField(
        db_column="D100Pvc", blank=True, null=True
    )  # Field name made lowercase.
    d125pvc = models.TextField(
        db_column="D125Pvc", blank=True, null=True
    )  # Field name made lowercase.
    d100sono = models.TextField(
        db_column="D100Sono", blank=True, null=True
    )  # Field name made lowercase.
    d125sono = models.TextField(
        db_column="D125Sono", blank=True, null=True
    )  # Field name made lowercase.
    idomok90 = models.TextField(
        db_column="Idomok90", blank=True, null=True
    )  # Field name made lowercase.
    idomok45 = models.TextField(
        db_column="Idomok45", blank=True, null=True
    )  # Field name made lowercase.
    idomoktoldo = models.TextField(
        db_column="IdomokToldo", blank=True, null=True
    )  # Field name made lowercase.
    idomoktidom = models.TextField(
        db_column="IdomokTIdom", blank=True, null=True
    )  # Field name made lowercase.
    idomokyidom = models.TextField(
        db_column="IdomokYIdom", blank=True, null=True
    )  # Field name made lowercase.
    megjegyzescsovezes = models.TextField(
        db_column="MegjegyzesCsovezes", blank=True, null=True
    )  # Field name made lowercase.
    emm716db = models.TextField(
        db_column="Emm716Db", blank=True, null=True
    )  # Field name made lowercase.
    holleszazemm716 = models.TextField(
        db_column="HolLeszAzEmm716", blank=True, null=True
    )  # Field name made lowercase.
    emm916db = models.TextField(
        db_column="Emm916Db", blank=True, null=True
    )  # Field name made lowercase.
    holleszazemm916 = models.TextField(
        db_column="HolLeszAzEmm916", blank=True, null=True
    )  # Field name made lowercase.
    ear201db2 = models.TextField(
        db_column="Ear201Db2", blank=True, null=True
    )  # Field name made lowercase.
    holleszazear201 = models.TextField(
        db_column="HolLeszAzEar201", blank=True, null=True
    )  # Field name made lowercase.
    ear202gazosdb = models.TextField(
        db_column="Ear202GazosDb", blank=True, null=True
    )  # Field name made lowercase.
    holleszazear202 = models.TextField(
        db_column="HolLeszAzEar202", blank=True, null=True
    )  # Field name made lowercase.
    ablakoslegbevezetokemm716 = models.TextField(
        db_column="AblakosLegbevezetokEmm716", blank=True, null=True
    )  # Field name made lowercase.
    ablakoslegbevezetokemm916 = models.TextField(
        db_column="AblakosLegbevezetokEmm916", blank=True, null=True
    )  # Field name made lowercase.
    ablakoslegbevezetokear201 = models.TextField(
        db_column="AblakosLegbevezetokEar201", blank=True, null=True
    )  # Field name made lowercase.
    ablakoslegbevezetokear202 = models.TextField(
        db_column="AblakosLegbevezetokEar202", blank=True, null=True
    )  # Field name made lowercase.
    eth1853db = models.TextField(
        db_column="Eth1853Db", blank=True, null=True
    )  # Field name made lowercase.
    holleszazeth1853 = models.TextField(
        db_column="HolLeszAzEth1853", blank=True, null=True
    )  # Field name made lowercase.
    eth1858gazosdb = models.TextField(
        db_column="Eth1858GazosDb", blank=True, null=True
    )  # Field name made lowercase.
    holleszazeth1858gazos = models.TextField(
        db_column="HolLeszAzEth1858Gazos", blank=True, null=True
    )  # Field name made lowercase.
    egyebkiegeszitokinfo = models.TextField(
        db_column="EgyebKiegeszitokInfo", blank=True, null=True
    )  # Field name made lowercase.
    ajtoszellozodb = models.TextField(
        db_column="AjtoszellozoDb", blank=True, null=True
    )  # Field name made lowercase.
    ajtogyuruszine = models.TextField(
        db_column="AjtogyuruSzine", blank=True, null=True
    )  # Field name made lowercase.
    melyikajtok3 = models.TextField(
        db_column="MelyikAjtok3", blank=True, null=True
    )  # Field name made lowercase.
    szellozoracskialakitasadb = models.TextField(
        db_column="SzellozoRacsKialakitasaDb", blank=True, null=True
    )  # Field name made lowercase.
    szellozoracshelye2 = models.TextField(
        db_column="SzellozoracsHelye2", blank=True, null=True
    )  # Field name made lowercase.
    tetoszellozocsereptipusszin = models.TextField(
        db_column="TetoszellozoCserepTipusszin", blank=True, null=True
    )  # Field name made lowercase.
    visszaaramlasgatlodb1db = models.TextField(
        db_column="VisszaaramlasGatloDb1Db", blank=True, null=True
    )  # Field name made lowercase.
    visszaaramlasgatlodb2db = models.TextField(
        db_column="VisszaaramlasGatloDb2Db", blank=True, null=True
    )  # Field name made lowercase.
    visszaaramlasgatlodb3db = models.TextField(
        db_column="VisszaaramlasGatloDb3Db", blank=True, null=True
    )  # Field name made lowercase.
    visszaaramlasgatlohelye = models.TextField(
        db_column="VisszaaramlasGatloHelye", blank=True, null=True
    )  # Field name made lowercase.
    keszitsdkepeketestoltsdfeloket = models.TextField(
        db_column="KeszitsdKepeketEsToltsdFelOket", blank=True, null=True
    )  # Field name made lowercase.
    keszitsvideotestoltsdfel = models.TextField(
        db_column="KeszitsVideotEsToltsdFel", blank=True, null=True
    )  # Field name made lowercase.
    keszitsszovegesleirastabeepitesselkapcsolatban = models.TextField(
        db_column="KeszitsSzovegesLeirastABeepitesselKapcsolatban",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    garanciaravonatkozomegjegyzes = models.TextField(
        db_column="GaranciaraVonatkozoMegjegyzes", blank=True, null=True
    )  # Field name made lowercase.
    melyikhelyisegbekerulkozpontimeglevoszellozohelyere = models.TextField(
        db_column="MelyikHelyisegbeKerulKozpontiMeglevoSzellozoHelyere",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    melyikhelyisegbekerulkozpontitetonkeresztulkivezetve = models.TextField(
        db_column="MelyikHelyisegbeKerulKozpontiTetonKeresztulKivezetve",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    felmero2 = models.TextField(
        db_column="Felmero2", blank=True, null=True
    )  # Field name made lowercase.
    dijbekeropdf2 = models.TextField(
        db_column="DijbekeroPdf2", blank=True, null=True
    )  # Field name made lowercase.
    dijbekeroszama2 = models.TextField(
        db_column="DijbekeroSzama2", blank=True, null=True
    )  # Field name made lowercase.
    dijbekeromegjegyzes2 = models.TextField(
        db_column="DijbekeroMegjegyzes2", blank=True, null=True
    )  # Field name made lowercase.
    dijbekerouzenetek = models.TextField(
        db_column="DijbekeroUzenetek", blank=True, null=True
    )  # Field name made lowercase.
    fizetesimod2 = models.TextField(
        db_column="FizetesiMod2", blank=True, null=True
    )  # Field name made lowercase.
    kiallitasdatuma = models.TextField(
        db_column="KiallitasDatuma", blank=True, null=True
    )  # Field name made lowercase.
    fizetesihatarido = models.TextField(
        db_column="FizetesiHatarido", blank=True, null=True
    )  # Field name made lowercase.
    mennyirevoltmegelegedve2 = models.TextField(
        db_column="MennyireVoltMegelegedve2", blank=True, null=True
    )  # Field name made lowercase.
    pontszam3 = models.TextField(
        db_column="Pontszam3", blank=True, null=True
    )  # Field name made lowercase.
    szovegesertekeles4 = models.TextField(
        db_column="SzovegesErtekeles4", blank=True, null=True
    )  # Field name made lowercase.
    ingatlankepe = models.TextField(
        db_column="IngatlanKepe", blank=True, null=True
    )  # Field name made lowercase.
    munkalap = models.TextField(
        db_column="Munkalap", blank=True, null=True
    )  # Field name made lowercase.
    bruttofelmeresidij = models.TextField(
        db_column="BruttoFelmeresiDij", blank=True, null=True
    )  # Field name made lowercase.
    munkalapmegjegyzes = models.TextField(
        db_column="MunkalapMegjegyzes", blank=True, null=True
    )  # Field name made lowercase.
    felmeresvisszaigazolva = models.TextField(
        db_column="FelmeresVisszaigazolva", blank=True, null=True
    )  # Field name made lowercase.
    szamlapdf = models.TextField(
        db_column="SzamlaPdf", blank=True, null=True
    )  # Field name made lowercase.
    szamlasorszama2 = models.TextField(
        db_column="SzamlaSorszama2", blank=True, null=True
    )  # Field name made lowercase.
    kiallitasdatuma2 = models.TextField(
        db_column="KiallitasDatuma2", blank=True, null=True
    )  # Field name made lowercase.
    szamlauzenetek = models.TextField(
        db_column="SzamlaUzenetek", blank=True, null=True
    )  # Field name made lowercase.
    kerdesazajanlattalkapcsolatban = models.TextField(
        db_column="KerdesAzAjanlattalKapcsolatban", blank=True, null=True
    )  # Field name made lowercase.
    ajanlatpdf = models.TextField(
        db_column="AjanlatPdf", blank=True, null=True
    )  # Field name made lowercase.
    szamlamegjegyzes = models.TextField(
        db_column="SzamlaMegjegyzes", blank=True, null=True
    )  # Field name made lowercase.
    felmeresadatok = models.TextField(
        db_column="FelmeresAdatok", blank=True, null=True
    )  # Field name made lowercase.
    utvonalakozponttol = models.TextField(
        db_column="UtvonalAKozponttol", blank=True, null=True
    )  # Field name made lowercase.
    streetviewurl = models.TextField(
        db_column="StreetViewUrl", blank=True, null=True
    )  # Field name made lowercase.
    tipus = models.TextField(
        db_column="Tipus", blank=True, null=True
    )  # Field name made lowercase.
    ventilatortipusa = models.TextField(
        db_column="VentilatorTipusa", blank=True, null=True
    )  # Field name made lowercase.
    keziszamlazas = models.BigIntegerField(
        db_column="KeziSzamlazas", blank=True, null=True
    )  # Field name made lowercase.
    rendelesszama = models.TextField(
        db_column="RendelesSzama", blank=True, null=True
    )  # Field name made lowercase.
    munkalap2 = models.TextField(
        db_column="Munkalap2", blank=True, null=True
    )  # Field name made lowercase.
    felmeresid = models.TextField(
        db_column="Felmeresid", blank=True, null=True
    )  # Field name made lowercase.
    hash = models.TextField(
        db_column="Hash", blank=True, null=True
    )  # Field name made lowercase.
    nextaction = models.TextField(
        db_column="NextAction", blank=True, null=True
    )  # Field name made lowercase.
    nextactionuserid = models.TextField(
        db_column="NextActionUserId", blank=True, null=True
    )  # Field name made lowercase.
    nextactiontodotype = models.TextField(
        db_column="NextActionToDoType", blank=True, null=True
    )  # Field name made lowercase.
    internalurl = models.TextField(
        db_column="InternalUrl", blank=True, null=True
    )  # Field name made lowercase.
    lastevent = models.TextField(
        db_column="LastEvent", blank=True, null=True
    )  # Field name made lowercase.
    statusgroup = models.TextField(
        db_column="StatusGroup", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "pen_minicrm_adatlapok"
