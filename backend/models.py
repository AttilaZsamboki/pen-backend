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
    question = models.ForeignKey('Questions', models.DO_NOTHING, db_column='question')
    value = models.TextField(blank=True, null=True)
    adatlap = models.ForeignKey('Felmeresek', models.DO_NOTHING, blank=True, null=True)
    section = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pen_felmeres_questions'

class FelmeresNotes(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.TextField()
    type = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    adatlap_id = models.TextField()

    class Meta:
        managed = False
        db_table = "pen_felmeresek_notes"

class Products(models.Model):
    id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    sku = models.TextField(db_column='SKU', blank=True, null=True)  # Field name made lowercase.
    type = models.TextField(db_column='Type', blank=True, null=True)  # Field name made lowercase.
    barcodes = models.TextField(db_column='Barcodes', blank=True, null=True)  # Field name made lowercase.
    alternative_sku = models.TextField(db_column='Alternative_SKU', blank=True, null=True)  # Field name made lowercase.
    minimum_stock_quantity = models.FloatField(db_column='Minimum_Stock_Quantity', blank=True, null=True)  # Field name made lowercase.
    optimal_stock_quantity = models.FloatField(db_column='Optimal_Stock_Quantity', blank=True, null=True)  # Field name made lowercase.
    category = models.TextField(db_column='Category', blank=True, null=True)  # Field name made lowercase.
    parent_id = models.TextField(db_column='Parent_ID', blank=True, null=True)  # Field name made lowercase.
    parent_sku = models.TextField(db_column='Parent_SKU', blank=True, null=True)  # Field name made lowercase.
    bundles_sku = models.TextField(db_column='Bundles_SKU', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    short_description = models.TextField(db_column='Short_Description', blank=True, null=True)  # Field name made lowercase.
    images = models.BigIntegerField(db_column='Images', blank=True, null=True)  # Field name made lowercase.
    unit = models.FloatField(db_column='Unit', blank=True, null=True)  # Field name made lowercase.
    moq = models.FloatField(db_column='MOQ', blank=True, null=True)  # Field name made lowercase.
    uom = models.FloatField(db_column='UOM', blank=True, null=True)  # Field name made lowercase.
    length = models.FloatField(db_column='Length', blank=True, null=True)  # Field name made lowercase.
    width = models.FloatField(db_column='Width', blank=True, null=True)  # Field name made lowercase.
    height = models.FloatField(db_column='Height', blank=True, null=True)  # Field name made lowercase.
    weight = models.BigIntegerField(db_column='Weight', blank=True, null=True)  # Field name made lowercase.
    net_weight = models.FloatField(db_column='Net_Weight', blank=True, null=True)  # Field name made lowercase.
    webshop_sort_order = models.BigIntegerField(db_column='Webshop_Sort_Order', blank=True, null=True)  # Field name made lowercase.
    commodity_code = models.TextField(db_column='Commodity_Code', blank=True, null=True)  # Field name made lowercase.
    excisable_product = models.BigIntegerField(db_column='Excisable_Product', blank=True, null=True)  # Field name made lowercase.
    combined_nomenclature = models.FloatField(db_column='Combined_Nomenclature', blank=True, null=True)  # Field name made lowercase.
    quantity_multiplier = models.FloatField(db_column='Quantity_Multiplier', blank=True, null=True)  # Field name made lowercase.
    supplementary_unit = models.FloatField(db_column='Supplementary_Unit', blank=True, null=True)  # Field name made lowercase.
    country_of_origin = models.FloatField(db_column='Country_Of_Origin', blank=True, null=True)  # Field name made lowercase.
    warranty_period = models.FloatField(db_column='Warranty_Period', blank=True, null=True)  # Field name made lowercase.
    warranty_period_unit = models.TextField(db_column='Warranty_Period_Unit', blank=True, null=True)  # Field name made lowercase.
    virtual = models.BigIntegerField(db_column='Virtual', blank=True, null=True)  # Field name made lowercase.
    fragile = models.TextField(db_column='Fragile', blank=True, null=True)  # Field name made lowercase.
    product_class = models.TextField(db_column='Product_Class', blank=True, null=True)  # Field name made lowercase.
    upsell_products = models.TextField(db_column='Upsell_Products', blank=True, null=True)  # Field name made lowercase.
    upsell_categories = models.TextField(db_column='Upsell_Categories', blank=True, null=True)  # Field name made lowercase.
    tags = models.TextField(db_column='Tags', blank=True, null=True)  # Field name made lowercase.
    virtual_net_cost = models.FloatField(db_column='Virtual_Net_Cost', blank=True, null=True)  # Field name made lowercase.
    virtual_net_cost_currency = models.TextField(db_column='Virtual_Net_Cost_Currency', blank=True, null=True)  # Field name made lowercase.
    tracking_type = models.TextField(db_column='Tracking_Type', blank=True, null=True)  # Field name made lowercase.
    manufacturer = models.TextField(db_column='Manufacturer', blank=True, null=True)  # Field name made lowercase.
    manufacturer_sku = models.TextField(db_column='Manufacturer_Sku', blank=True, null=True)  # Field name made lowercase.
    price_list_alapertelmezett_net_price_huf = models.BigIntegerField(db_column='Price_List___alapertelmezett___Net_Price_HUF', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    price_list_alapertelmezett_price_huf = models.FloatField(db_column='Price_List___alapertelmezett___Price_HUF', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    price_list_alapertelmezett_vat = models.TextField(db_column='Price_List___alapertelmezett___VAT', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    price_list_alapertelmezett_vat_field = models.BigIntegerField(db_column='Price_List___alapertelmezett___VAT_', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row. Field renamed because it ended with '_'.
    price_list_alapertelmezett_quantity_discount = models.FloatField(db_column='Price_List___alapertelmezett___Quantity_Discount', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    price_list_alapertelmezett_formula = models.FloatField(db_column='Price_List___alapertelmezett___Formula', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    price_list_alapertelmezett_price_type = models.TextField(db_column='Price_List___alapertelmezett___Price_Type', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_net_price_huf = models.FloatField(db_column='Sale_Price_List___alapertelmezett___Net_Price_HUF', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_price_huf = models.FloatField(db_column='Sale_Price_List___alapertelmezett___Price_HUF', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_vat = models.FloatField(db_column='Sale_Price_List___alapertelmezett___VAT', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_vat_field = models.FloatField(db_column='Sale_Price_List___alapertelmezett___VAT_', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row. Field renamed because it ended with '_'.
    sale_price_list_alapertelmezett_from_date = models.FloatField(db_column='Sale_Price_List___alapertelmezett___From_Date', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_to_date = models.FloatField(db_column='Sale_Price_List___alapertelmezett___To_Date', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_quantity_discount = models.FloatField(db_column='Sale_Price_List___alapertelmezett___Quantity_Discount', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_formula = models.FloatField(db_column='Sale_Price_List___alapertelmezett___Formula', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_price_type = models.FloatField(db_column='Sale_Price_List___alapertelmezett___Price_Type', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    warehouse_raktar_1_allowed = models.BigIntegerField(db_column='Warehouse___Raktar_1___Allowed', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    warehouse_raktar_1_minimum_stock_quantity = models.FloatField(db_column='Warehouse___Raktar_1____Minimum_Stock_Quantity', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    warehouse_raktar_1_optimal_stock_quantity = models.FloatField(db_column='Warehouse___Raktar_1____Optimal_Stock_Quantity', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    warehouse_selejt_allowed = models.BigIntegerField(db_column='Warehouse___Selejt___Allowed', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    warehouse_selejt_minimum_stock_quantity = models.FloatField(db_column='Warehouse___Selejt____Minimum_Stock_Quantity', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    warehouse_selejt_optimal_stock_quantity = models.FloatField(db_column='Warehouse___Selejt____Optimal_Stock_Quantity', blank=True, null=True)  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.

    class Meta:
        managed = False
        db_table = 'pen_products'

class ProductAttributes(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    place = models.BooleanField(blank=True, null=True)
    place_options = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pen_product_attributes'

class Filters(models.Model):
    name = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    sort_by = models.TextField(blank=True, null=True)
    sort_order = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pen_filters'

class FilterItems(models.Model):
    field = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=225, blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    filter = models.ForeignKey('Filters', models.CASCADE)
    label = models.TextField(blank=True, null=True)
    options = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pen_filter_items'

class Questions(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    connection = models.CharField(max_length=255, blank=True, null=True)
    options = models.JSONField(blank=True, null=True)
    mandatory = models.BooleanField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pen_questions'

class Templates(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pen_templates'

class ProductTemplate(models.Model):
    template = models.ForeignKey('Templates', models.CASCADE, primary_key=True)
    product = models.ForeignKey('Products', models.DO_NOTHING)  # The composite primary key (product_id, template_id) found, that is not supported. The first column is selected.

    class Meta:
        managed = False
        db_table = 'pen_product_template'
        unique_together = (('product', 'template'),)


class Felmeresek(models.Model):
    id = models.AutoField(primary_key=True)
    adatlap_id = models.IntegerField()
    template = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True, default="DRAFT")
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pen_felmeresek'

class FelmeresItems(models.Model):
    name = models.TextField(blank=True, null=True)
    place = models.BooleanField(blank=True, null=True)
    placeOptions = models.JSONField(db_column="place_options", blank=True, null=True)  # This field type is a guess.
    product = models.ForeignKey('Products', models.DO_NOTHING, db_column="product_id", blank=True, null=True)
    inputValues = models.JSONField(db_column="input_values",blank=True, null=True)
    netPrice = models.IntegerField(db_column="net_price", blank=True, null=True)
    adatlap = models.ForeignKey('Felmeresek', models.DO_NOTHING, db_column="adatlap_id")
    type = models.CharField(max_length=255, blank=True, null=True)
    valueType = models.CharField(max_length=255, blank=True, null=True, default="fixed", db_column="value_type")
    source = models.CharField(max_length=100, blank=True, null=True, default="Manual")

    class Meta:
        managed = False
        db_table = 'pen_felmeres_items'

class Counties(models.Model):
    telepules = models.TextField(db_column='Telepules',primary_key=True)  # Field name made lowercase.
    jogallasa = models.TextField(blank=True, null=True)
    megye = models.TextField(db_column='Megye_megnevezese_', blank=True, null=True)  # Field name made lowercase. Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'counties'

class Offers(models.Model):
    id = models.AutoField(primary_key=True)
    offer_id = models.IntegerField(blank=True, null=True)
    adatlap = models.IntegerField(db_column="adatlap_id")

    class Meta:
        managed = False
        db_table = 'pen_offers'

class QuestionProducts(models.Model):
    product = models.ForeignKey('Products', models.DO_NOTHING)  # The composite primary key (product_id, question_id) found, that is not supported. The first column is selected.
    question = models.ForeignKey('Questions', models.CASCADE, primary_key=True)

    class Meta:
        managed = False
        db_table = 'pen_question_products'
        unique_together = (('product', 'question'),)

class ErpAuthTokens(models.Model):
    token = models.CharField(max_length=255, blank=True, null=True)
    expire = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pen_erp_auth_tokens'

class Orders(models.Model):
    adatlap_id = models.IntegerField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pen_orders'

class Order(models.Model):
    row_type = models.TextField(db_column='Row_Type', blank=True, null=True)  # Field name made lowercase.
    order_id = models.TextField(db_column='Order_ID', blank=True, null=True)  # Field name made lowercase.
    sku = models.TextField(db_column='SKU', blank=True, null=True)  # Field name made lowercase.
    product_name = models.TextField(db_column='Product_Name', blank=True, null=True)  # Field name made lowercase.
    default_supplier_unit_price = models.FloatField(db_column='Default_Supplier_Unit_Price', blank=True, null=True)  # Field name made lowercase.
    default_supplier_currency = models.TextField(db_column='Default_Supplier_Currency', blank=True, null=True)  # Field name made lowercase.
    quantity = models.FloatField(db_column='Quantity', blank=True, null=True)  # Field name made lowercase.
    unit_price = models.FloatField(db_column='Unit_Price', blank=True, null=True)  # Field name made lowercase.
    discount = models.FloatField(db_column='Discount', blank=True, null=True)  # Field name made lowercase.
    tax = models.FloatField(db_column='Tax', blank=True, null=True)  # Field name made lowercase.
    subtotal = models.FloatField(db_column='Subtotal', blank=True, null=True)  # Field name made lowercase.
    landed_cost = models.FloatField(db_column='Landed_Cost', blank=True, null=True)  # Field name made lowercase.
    cogs = models.FloatField(db_column='Cogs', blank=True, null=True)  # Field name made lowercase.
    margin = models.FloatField(db_column='Margin', blank=True, null=True)  # Field name made lowercase.
    margin_field = models.FloatField(db_column='Margin_', blank=True, null=True)  # Field name made lowercase. Field renamed because it ended with '_'.
    item_note = models.FloatField(db_column='Item_Note', blank=True, null=True)  # Field name made lowercase.
    weight = models.FloatField(db_column='Weight', blank=True, null=True)  # Field name made lowercase.
    webshop_id = models.TextField(db_column='Webshop_ID', blank=True, null=True)  # Field name made lowercase.
    return_reason = models.TextField(db_column='Return_Reason', blank=True, null=True)  # Field name made lowercase.
    package_number = models.FloatField(db_column='Package_Number', blank=True, null=True)  # Field name made lowercase.
    order_total = models.FloatField(db_column='Order_Total', blank=True, null=True)  # Field name made lowercase.
    currency = models.TextField(db_column='Currency', blank=True, null=True)  # Field name made lowercase.
    source = models.TextField(db_column='Source', blank=True, null=True)  # Field name made lowercase.
    source_name = models.TextField(db_column='Source_Name', blank=True, null=True)  # Field name made lowercase.
    order_status = models.TextField(db_column='Order_Status', blank=True, null=True)  # Field name made lowercase.
    order_date = models.TextField(db_column='Order_Date', blank=True, null=True)  # Field name made lowercase.
    customer_identifier = models.FloatField(db_column='Customer_Identifier', blank=True, null=True)  # Field name made lowercase.
    memo = models.TextField(db_column='Memo', blank=True, null=True)  # Field name made lowercase.
    billing_email = models.TextField(db_column='Billing_Email', blank=True, null=True)  # Field name made lowercase.
    billing_address_1 = models.TextField(db_column='Billing_Address_1', blank=True, null=True)  # Field name made lowercase.
    billing_address_2 = models.TextField(db_column='Billing_Address_2', blank=True, null=True)  # Field name made lowercase.
    billing_country = models.TextField(db_column='Billing_Country', blank=True, null=True)  # Field name made lowercase.
    billing_city = models.TextField(db_column='Billing_City', blank=True, null=True)  # Field name made lowercase.
    billing_zip_code = models.BigIntegerField(db_column='Billing_Zip_Code', blank=True, null=True)  # Field name made lowercase.
    billing_last_name = models.TextField(db_column='Billing_Last_Name', blank=True, null=True)  # Field name made lowercase.
    billing_first_name = models.TextField(db_column='Billing_First_Name', blank=True, null=True)  # Field name made lowercase.
    billing_tax_number = models.TextField(db_column='Billing_Tax_Number', blank=True, null=True)  # Field name made lowercase.
    billing_company = models.TextField(db_column='Billing_Company', blank=True, null=True)  # Field name made lowercase.
    manual_invoicing = models.BooleanField(db_column='Manual_Invoicing', blank=True, null=True)  # Field name made lowercase.
    manual_proforma = models.BooleanField(db_column='Manual_Proforma', blank=True, null=True)  # Field name made lowercase.
    shipping_email = models.TextField(db_column='Shipping_Email', blank=True, null=True)  # Field name made lowercase.
    shipping_address_1 = models.TextField(db_column='Shipping_Address_1', blank=True, null=True)  # Field name made lowercase.
    shipping_address_2 = models.TextField(db_column='Shipping_Address_2', blank=True, null=True)  # Field name made lowercase.
    shipping_country = models.TextField(db_column='Shipping_Country', blank=True, null=True)  # Field name made lowercase.
    shipping_city = models.TextField(db_column='Shipping_City', blank=True, null=True)  # Field name made lowercase.
    shipping_zip_code = models.TextField(db_column='Shipping_Zip_Code', blank=True, null=True)  # Field name made lowercase.
    shipping_last_name = models.TextField(db_column='Shipping_Last_Name', blank=True, null=True)  # Field name made lowercase.
    shipping_first_name = models.TextField(db_column='Shipping_First_Name', blank=True, null=True)  # Field name made lowercase.
    shipping_company = models.TextField(db_column='Shipping_Company', blank=True, null=True)  # Field name made lowercase.
    delivery_note = models.TextField(db_column='Delivery_Note', blank=True, null=True)  # Field name made lowercase.
    shipping_method = models.TextField(db_column='Shipping_Method', blank=True, null=True)  # Field name made lowercase.
    payment_method = models.TextField(db_column='Payment_Method', blank=True, null=True)  # Field name made lowercase.
    discount_value = models.BigIntegerField(db_column='Discount_Value', blank=True, null=True)  # Field name made lowercase.
    exchange_rate = models.BigIntegerField(db_column='Exchange_Rate', blank=True, null=True)  # Field name made lowercase.
    payment_status = models.TextField(db_column='Payment_Status', blank=True, null=True)  # Field name made lowercase.
    warehouse = models.TextField(db_column='Warehouse', blank=True, null=True)  # Field name made lowercase.
    delivery_date = models.FloatField(db_column='Delivery_Date', blank=True, null=True)  # Field name made lowercase.
    proforma_invoice_id = models.TextField(db_column='Proforma_Invoice_ID', blank=True, null=True)  # Field name made lowercase.
    proforma_invoice_id_2 = models.FloatField(db_column='Proforma_Invoice_ID_2', blank=True, null=True)  # Field name made lowercase.
    invoice_id = models.TextField(db_column='Invoice_ID', blank=True, null=True)  # Field name made lowercase.
    reverse_invoice_id = models.TextField(db_column='Reverse_Invoice_ID', blank=True, null=True)  # Field name made lowercase.
    prepayment_reverse_invoice_id = models.FloatField(db_column='Prepayment_Reverse_Invoice_ID', blank=True, null=True)  # Field name made lowercase.
    prepayment_reverse_invoice_id_2 = models.FloatField(db_column='Prepayment_Reverse_Invoice_ID_2', blank=True, null=True)  # Field name made lowercase.
    tags = models.TextField(db_column='Tags', blank=True, null=True)  # Field name made lowercase.
    customer_classes = models.TextField(db_column='Customer_Classes', blank=True, null=True)  # Field name made lowercase.
    created_by = models.TextField(db_column='Created_By', blank=True, null=True)  # Field name made lowercase.
    default_customer_class = models.TextField(db_column='Default_Customer_Class', blank=True, null=True)  # Field name made lowercase.
    paid_at = models.TextField(db_column='Paid_At', blank=True, null=True)  # Field name made lowercase.
    cancel_reason = models.TextField(db_column='Cancel_Reason', blank=True, null=True)  # Field name made lowercase.
    cancelled_by = models.TextField(db_column='Cancelled_By', blank=True, null=True)  # Field name made lowercase.
    cancelled_at = models.TextField(db_column='Cancelled_At', blank=True, null=True)  # Field name made lowercase.
    completed_at = models.TextField(db_column='Completed_At', blank=True, null=True)  # Field name made lowercase.
    id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pen_order'

class PaymentMethods(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pen_payment_methods'