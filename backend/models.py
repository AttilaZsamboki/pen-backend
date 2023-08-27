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
    id = models.AutoField(primary_key=True)
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
    id = models.BigIntegerField(db_column='ID', blank=True, primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    sku = models.TextField(db_column='SKU', blank=True, null=True)  # Field name made lowercase.
    type = models.TextField(db_column='Type', blank=True, null=True)  # Field name made lowercase.
    barcodes = models.FloatField(db_column='Barcodes', blank=True, null=True)  # Field name made lowercase.
    alternative_sku = models.FloatField(db_column='Alternative_SKU', blank=True, null=True)  # Field name made lowercase.
    minimum_stock_quantity = models.FloatField(db_column='Minimum_Stock_Quantity', blank=True, null=True)  # Field name made lowercase.
    optimal_stock_quantity = models.FloatField(db_column='Optimal_Stock_Quantity', blank=True, null=True)  # Field name made lowercase.
    category = models.TextField(db_column='Category', blank=True, null=True)  # Field name made lowercase.
    parent_id = models.FloatField(db_column='Parent_ID', blank=True, null=True)  # Field name made lowercase.
    parent_sku = models.FloatField(db_column='Parent_SKU', blank=True, null=True)  # Field name made lowercase.
    bundles_sku = models.FloatField(db_column='Bundles_SKU', blank=True, null=True)  # Field name made lowercase.
    description = models.FloatField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    short_description = models.FloatField(db_column='Short_Description', blank=True, null=True)  # Field name made lowercase.
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
    commodity_code = models.FloatField(db_column='Commodity_Code', blank=True, null=True)  # Field name made lowercase.
    excisable_product = models.BigIntegerField(db_column='Excisable_Product', blank=True, null=True)  # Field name made lowercase.
    combined_nomenclature = models.FloatField(db_column='Combined_Nomenclature', blank=True, null=True)  # Field name made lowercase.
    quantity_multiplier = models.FloatField(db_column='Quantity_Multiplier', blank=True, null=True)  # Field name made lowercase.
    supplementary_unit = models.FloatField(db_column='Supplementary_Unit', blank=True, null=True)  # Field name made lowercase.
    country_of_origin = models.FloatField(db_column='Country_Of_Origin', blank=True, null=True)  # Field name made lowercase.
    warranty_period = models.FloatField(db_column='Warranty_Period', blank=True, null=True)  # Field name made lowercase.
    warranty_period_unit = models.TextField(db_column='Warranty_Period_Unit', blank=True, null=True)  # Field name made lowercase.
    virtual = models.BigIntegerField(db_column='Virtual', blank=True, null=True)  # Field name made lowercase.
    fragile = models.BigIntegerField(db_column='Fragile', blank=True, null=True)  # Field name made lowercase.
    product_class = models.FloatField(db_column='Product_Class', blank=True, null=True)  # Field name made lowercase.
    upsell_products = models.FloatField(db_column='Upsell_Products', blank=True, null=True)  # Field name made lowercase.
    upsell_categories = models.FloatField(db_column='Upsell_Categories', blank=True, null=True)  # Field name made lowercase.
    tags = models.FloatField(db_column='Tags', blank=True, null=True)  # Field name made lowercase.
    virtual_net_cost = models.FloatField(db_column='Virtual_Net_Cost', blank=True, null=True)  # Field name made lowercase.
    virtual_net_cost_currency = models.TextField(db_column='Virtual_Net_Cost_Currency', blank=True, null=True)  # Field name made lowercase.
    tracking_type = models.TextField(db_column='Tracking_Type', blank=True, null=True)  # Field name made lowercase.
    manufacturer = models.FloatField(db_column='Manufacturer', blank=True, null=True)  # Field name made lowercase.
    manufacturer_sku = models.FloatField(db_column='Manufacturer_Sku', blank=True, null=True)  # Field name made lowercase.
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
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    value = models.JSONField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pen_filters'


class Questions(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Products, models.DO_NOTHING, blank=True, null=True)
    connection = models.CharField(max_length=255, blank=True, null=True)
    options = models.JSONField(blank=True, null=True)

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
    product = models.ForeignKey('Products', models.DO_NOTHING)  # The composite primary key (product_id, template_id) found, that is not supported. The first column is selected.
    template = models.ForeignKey('Templates', models.CASCADE, primary_key=True)

    class Meta:
        managed = False
        db_table = 'pen_product_template'
        unique_together = (('product', 'template'),)


class Felmeresek(models.Model):
    adatlap_id = models.IntegerField(primary_key=True)
    template = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pen_felmeresek'

class FelmeresItems(models.Model):
    name = models.TextField(blank=True, null=True)
    place = models.BooleanField(blank=True, null=True)
    placeOptions = models.JSONField(db_column="place_options", blank=True, null=True)  # This field type is a guess.
    productId = models.IntegerField(db_column="product_id")
    inputValues = models.JSONField(db_column="input_values",blank=True, null=True)
    netPrice = models.IntegerField(db_column="net_price", blank=True, null=True)
    adatlap = models.ForeignKey('Felmeresek', models.DO_NOTHING, db_column="adatlap_id")

    class Meta:
        managed = False
        db_table = 'pen_felmeres_items'