from django.db import models
from .utils.minicrm_str_to_text import status_map
from .utils.gmail import gmail_authenticate, send_email


# Create your models here.
class Logs(models.Model):
    id = models.AutoField(primary_key=True)
    script_name = models.TextField()
    time = models.DateTimeField()
    status = models.TextField()
    value = models.TextField()
    details = models.TextField()
    data = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "logs"

    def save(self, *args, **kwargs):
        service = gmail_authenticate()
        if self.status == "ERROR":
            send_email(
                service=service,
                destination="zsamboki.attila.jr@gmail.com",
                obj="Sikertelen script: " + self.script_name,
                body=f"{self.value} \n {f'Részletek: {self.details}' if self.details else ''}",
            )
        super(Logs, self).save(*args, **kwargs)


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
    images = models.TextField(
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
    sale_price_list_alapertelmezett_vat = models.TextField(
        db_column="Sale_Price_List___alapertelmezett___VAT", blank=True, null=True
    )  # Field name made lowercase. Field renamed because it contained more than one '_' in a row.
    sale_price_list_alapertelmezett_vat_field = models.TextField(
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
    product = models.IntegerField(
        db_column="product_id"
    )  # The composite primary key (product_id, template_id) found, that is not supported. The first column is selected.
    type = models.CharField(max_length=100, default="Item")

    class Meta:
        managed = False
        db_table = "pen_product_template"
        unique_together = (("product", "template", "type"),)


class Felmeresek(models.Model):
    id = models.AutoField(primary_key=True)
    adatlap_id = models.ForeignKey(
        "MinicrmAdatlapok",
        models.DO_NOTHING,
        db_column="adatlap_id",
    )
    template: Templates = models.ForeignKey(
        "Templates", models.DO_NOTHING, db_column="template", blank=True, null=True
    )
    type = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True, default="DRAFT")
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    garancia = models.CharField(max_length=255, blank=True, null=True)
    garancia_reason = models.TextField(blank=True, null=True)
    hourly_wage = models.FloatField(blank=True, null=True)
    is_conditional = models.BooleanField(blank=True, null=True, default=False)
    condition = models.TextField(blank=True, null=True)

    @property
    def netOrderTotal(self):
        return sum(
            item.netTotal for item in self.felmeresitems_set.exclude(type="Discount")
        ) + sum(item.value * item.amount for item in self.felmeresmunkadijak_set.all())

    @property
    def grossOrderTotal(self):
        total = self.netOrderTotal * 1.27
        discount = self.felmeresitems_set.filter(type="Discount")
        if discount.exists() and discount.first().netPrice != 0:
            return total * (1 - (discount.first().netPrice / 100))
        return total

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

    @property
    def netTotal(self):
        if self.valueType == "fixed":
            return self.netPrice * sum([i["ammount"] for i in self.inputValues])
        elif self.valueType == "percent":
            order_total = sum(
                [
                    i.netPrice * sum([j["ammount"] for j in i.inputValues])
                    for i in self.adatlap.felmeresitems_set.all()
                    if i.valueType != "percent"
                ]
            )
            return (self.netPrice / 100) * order_total
        else:
            return 0

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
    id = models.IntegerField(primary_key=True)
    adatlap = models.ForeignKey("MinicrmAdatlapok", models.DO_NOTHING)

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
    adatlap_id = models.IntegerField(db_column="ProjectId", blank=True, null=True)
    order_id = models.IntegerField(db_column="Id", primary_key=True)

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


class MiniCrmAdatlapok(models.Model):
    Id = models.IntegerField(primary_key=True)
    CategoryId = models.IntegerField(blank=True, null=True)
    ContactId = models.IntegerField(blank=True, null=True)
    MainContactId = models.IntegerField(blank=True, null=True)
    StatusId = models.IntegerField(blank=True, null=True)
    UserId = models.BigIntegerField(blank=True, null=True)
    Name = models.TextField(blank=True, null=True)
    StatusUpdatedAt = models.TextField(blank=True, null=True)
    IsPrivate = models.TextField(blank=True, null=True)
    Invited = models.TextField(blank=True, null=True)
    Deleted = models.TextField(blank=True, null=True)
    CreatedBy = models.BigIntegerField(blank=True, null=True)
    CreatedAt = models.DateTimeField(blank=True, null=True)
    UpdatedBy = models.BigIntegerField(blank=True, null=True)
    UpdatedAt = models.TextField(blank=True, null=True)
    Referrer = models.TextField(blank=True, null=True)
    WhyNotUs = models.TextField(blank=True, null=True)
    WhyUs = models.TextField(blank=True, null=True)
    ImportDate = models.TextField(blank=True, null=True)
    Related_BusinessId = models.TextField(blank=True, null=True)
    ReferenceId = models.TextField(blank=True, null=True)
    Number = models.TextField(blank=True, null=True)
    Issued = models.TextField(blank=True, null=True)
    Performance = models.TextField(blank=True, null=True)
    Prompt = models.TextField(blank=True, null=True)
    Paid = models.TextField(blank=True, null=True)
    Amount = models.TextField(blank=True, null=True)
    InvoiceType = models.TextField(blank=True, null=True)
    InvoicePdf = models.TextField(blank=True, null=True)
    ListSubscriptions = models.BigIntegerField(blank=True, null=True)
    PushToken = models.TextField(blank=True, null=True)
    PushDevice = models.TextField(blank=True, null=True)
    UUId = models.TextField(blank=True, null=True)
    UninstalledAt = models.TextField(blank=True, null=True)
    PhoneVer = models.TextField(blank=True, null=True)
    OSVer = models.TextField(blank=True, null=True)
    AppVer = models.TextField(blank=True, null=True)
    AutoSales_SalesStatus = models.TextField(blank=True, null=True)
    AutoSales_Qualification = models.TextField(blank=True, null=True)
    AutoSales_ReachedStatus = models.TextField(blank=True, null=True)
    AutoSales_LastToDoModification = models.TextField(blank=True, null=True)
    SatisfactionRating = models.TextField(blank=True, null=True)
    ReachedMobileActivity = models.TextField(blank=True, null=True)
    MobileLastLogin = models.TextField(blank=True, null=True)
    EmailModule_EmailCount = models.TextField(blank=True, null=True)
    EmailModule_OpenRate = models.TextField(blank=True, null=True)
    EmailModule_ClickRate = models.TextField(blank=True, null=True)
    MobileLoggedIn = models.BigIntegerField(blank=True, null=True)
    Webshop_ReachedStatus = models.TextField(blank=True, null=True)
    Webshop_LifeTimeValue = models.TextField(blank=True, null=True)
    Webshop_NumberOfOrders = models.TextField(blank=True, null=True)
    Webshop_NumberOfProducts = models.TextField(blank=True, null=True)
    Webshop_FirstOrderDate = models.TextField(blank=True, null=True)
    Webshop_LastOrderDate = models.TextField(blank=True, null=True)
    Webshop_LastOrderAmount = models.TextField(blank=True, null=True)
    Webshop_LastOrderStatus = models.TextField(blank=True, null=True)
    Webshop_Disabled = models.BigIntegerField(blank=True, null=True)
    Webshop_RegistrationDate = models.TextField(blank=True, null=True)
    Webshop_LostBasketContent = models.TextField(blank=True, null=True)
    Webshop_LostBasketDate = models.TextField(blank=True, null=True)
    Webshop_LostBasketValue = models.TextField(blank=True, null=True)
    Webshop_AllLostBasket = models.TextField(blank=True, null=True)
    AutoSalesV2_Qualification = models.TextField(blank=True, null=True)
    AutoSalesV2_Rating = models.TextField(blank=True, null=True)
    AutoSalesV2_SalesStatus = models.TextField(blank=True, null=True)
    SalesStepV2 = models.TextField(blank=True, null=True)
    NewsletterV2 = models.BigIntegerField(blank=True, null=True)
    AutoSalesV2_ReachedStatus = models.TextField(blank=True, null=True)
    EmailOpen_Phone = models.TextField(blank=True, null=True)
    EmailOpen_Tablet = models.TextField(blank=True, null=True)
    EmailOpen_iPhone = models.TextField(blank=True, null=True)
    EmailOpen_iPad = models.TextField(blank=True, null=True)
    EmailOpen_Android = models.TextField(blank=True, null=True)
    AutoSalesV3_Qualification = models.TextField(blank=True, null=True)
    AutoSalesV3_IsHot = models.BigIntegerField(blank=True, null=True)
    AutoSalesV3_SalesStatus = models.TextField(blank=True, null=True)
    AutoSalesV3_ReachedStatus = models.TextField(blank=True, null=True)
    AutoSalesV3_ReachedStatusGroup = models.TextField(blank=True, null=True)
    AutoSalesV3_LeadStep = models.TextField(blank=True, null=True)
    AutoSalesV3_CustomerStep = models.TextField(blank=True, null=True)
    Write_Protected = models.TextField(blank=True, null=True)
    NavStatus = models.TextField(blank=True, null=True)
    NavStatusMessage = models.TextField(blank=True, null=True)
    Newsletter_Subscriber = models.BigIntegerField(blank=True, null=True)
    CustomerCard_ActivationDate = models.TextField(blank=True, null=True)
    CustomerCard_AveragePurchase = models.TextField(blank=True, null=True)
    CustomerCard_Birthday = models.TextField(blank=True, null=True)
    CustomerCard_CardNumber = models.TextField(blank=True, null=True)
    CustomerCard_CardStatus = models.TextField(blank=True, null=True)
    CustomerCard_CardType = models.TextField(blank=True, null=True)
    CustomerCard_Comment = models.TextField(blank=True, null=True)
    CustomerCard_MoneyBalance = models.TextField(blank=True, null=True)
    CustomerCard_Nameday = models.TextField(blank=True, null=True)
    CustomerCard_PointBalance = models.TextField(blank=True, null=True)
    CustomerCard_RegisteredBusiness = models.TextField(blank=True, null=True)
    CustomerCard_Sex = models.TextField(blank=True, null=True)
    CustomerCard_UserId = models.TextField(blank=True, null=True)
    CustomerCard_ValidCoupons = models.TextField(blank=True, null=True)
    CustomerCard_ValidPasses = models.TextField(blank=True, null=True)
    CustomerCard_RegistrationDate = models.TextField(blank=True, null=True)
    CustomerCard_LifeTimeValue = models.TextField(blank=True, null=True)
    CustomerCard_NumberOfOrders = models.TextField(blank=True, null=True)
    CustomerCard_LastOrderDate = models.TextField(blank=True, null=True)
    ProjectManagement_Deadline = models.TextField(blank=True, null=True)
    ProjectManagement_ExpectedRevenue = models.TextField(blank=True, null=True)
    ProjectManagement_Type = models.TextField(blank=True, null=True)
    ProjectManagement_DesiredOutcome = models.TextField(blank=True, null=True)
    Serial_Number = models.TextField(blank=True, null=True)
    InboundInvoice_NavStatus = models.TextField(blank=True, null=True)
    InboundInvoice_NavNumber = models.TextField(blank=True, null=True)
    Holiday_Start = models.TextField(blank=True, null=True)
    Holiday_End = models.TextField(blank=True, null=True)
    Holiday_Substitute = models.TextField(blank=True, null=True)
    Interests = models.BigIntegerField(blank=True, null=True)
    Type = models.TextField(blank=True, null=True)
    Category = models.TextField(blank=True, null=True)
    Deadline = models.TextField(blank=True, null=True)
    OfferDate = models.TextField(blank=True, null=True)
    OfferPrice = models.TextField(blank=True, null=True)
    Datetime2 = models.TextField(blank=True, null=True)
    Checkbox29 = models.BigIntegerField(blank=True, null=True)
    Checkbox31 = models.BigIntegerField(blank=True, null=True)
    Checkbox34 = models.BigIntegerField(blank=True, null=True)
    Checkbox37 = models.BigIntegerField(blank=True, null=True)
    Checkbox38 = models.BigIntegerField(blank=True, null=True)
    Checkbox39 = models.BigIntegerField(blank=True, null=True)
    Checkbox35 = models.BigIntegerField(blank=True, null=True)
    Enum1 = models.TextField(blank=True, null=True)
    Datetime44 = models.TextField(blank=True, null=True)
    Datetime45 = models.TextField(blank=True, null=True)
    Datetime3 = models.TextField(blank=True, null=True)
    Enum5 = models.TextField(blank=True, null=True)
    Enum6 = models.TextField(blank=True, null=True)
    Enum7 = models.TextField(blank=True, null=True)
    Set8 = models.BigIntegerField(blank=True, null=True)
    Enum9 = models.TextField(blank=True, null=True)
    Set10 = models.BigIntegerField(blank=True, null=True)
    Enum11 = models.TextField(blank=True, null=True)
    Set12 = models.BigIntegerField(blank=True, null=True)
    Int14 = models.TextField(blank=True, null=True)
    Int15 = models.TextField(blank=True, null=True)
    Int16 = models.TextField(blank=True, null=True)
    Int17 = models.TextField(blank=True, null=True)
    Varchar18 = models.TextField(blank=True, null=True)
    Enum19 = models.TextField(blank=True, null=True)
    Enum20 = models.TextField(blank=True, null=True)
    Enum21 = models.TextField(blank=True, null=True)
    Enum22 = models.TextField(blank=True, null=True)
    Enum23 = models.TextField(blank=True, null=True)
    Set25 = models.BigIntegerField(blank=True, null=True)
    Int26 = models.TextField(blank=True, null=True)
    Set27 = models.BigIntegerField(blank=True, null=True)
    Int40 = models.TextField(blank=True, null=True)
    Checkbox42 = models.BigIntegerField(blank=True, null=True)
    Enum1098 = models.TextField(blank=True, null=True)
    Text1099 = models.TextField(blank=True, null=True)
    DateTime1100 = models.TextField(blank=True, null=True)
    Text1101 = models.TextField(blank=True, null=True)
    Text1102 = models.TextField(blank=True, null=True)
    Enum1103 = models.TextField(blank=True, null=True)
    Enum1104 = models.TextField(blank=True, null=True)
    Enum1105 = models.TextField(blank=True, null=True)
    Text1106 = models.TextField(blank=True, null=True)
    Enum1107 = models.TextField(blank=True, null=True)
    AlaprajzFeltoltese = models.TextField(blank=True, null=True)
    LapraszereltSzellozo = models.BigIntegerField(blank=True, null=True)
    KapcsolatfelvetelOkanakRovidLeirasa = models.TextField(blank=True, null=True)
    ALakasbanTalalhatoGazkazanCirko = models.BigIntegerField(blank=True, null=True)
    OknoplastViszontelado = models.TextField(blank=True, null=True)
    Enum1115 = models.TextField(blank=True, null=True)
    Enum1116 = models.TextField(blank=True, null=True)
    Int1117 = models.TextField(blank=True, null=True)
    Set1118 = models.BigIntegerField(blank=True, null=True)
    Enum1119 = models.TextField(blank=True, null=True)
    Enum1121 = models.TextField(blank=True, null=True)
    DateTime1122 = models.TextField(blank=True, null=True)
    Text1124 = models.TextField(blank=True, null=True)
    Felmeres = models.TextField(blank=True, null=True)
    FelmeresIdopontja = models.TextField(blank=True, null=True)
    Enum1130 = models.TextField(blank=True, null=True)
    Enum1131 = models.TextField(blank=True, null=True)
    Int1132 = models.TextField(blank=True, null=True)
    Set1133 = models.BigIntegerField(blank=True, null=True)
    Leiras = models.TextField(blank=True, null=True)
    Problemak = models.BigIntegerField(blank=True, null=True)
    MitProbaltalMar = models.BigIntegerField(blank=True, null=True)
    JoinUrl = models.TextField(blank=True, null=True)
    KovetkezoWebinarium = models.TextField(blank=True, null=True)
    MilyenProblemaraKeresMegoldast = models.BigIntegerField(blank=True, null=True)
    MitProbaltMar = models.BigIntegerField(blank=True, null=True)
    SzabadSzovegesLeiras = models.TextField(blank=True, null=True)
    Url = models.TextField(blank=True, null=True)
    WebinariumraJelentkezett = models.BigIntegerField(blank=True, null=True)
    ResztVett = models.BigIntegerField(blank=True, null=True)
    WebinariumMegjegyzes = models.TextField(blank=True, null=True)
    FelmeresMegtortent = models.BigIntegerField(blank=True, null=True)
    FelmerestKert = models.BigIntegerField(blank=True, null=True)
    Kedvezmeny = models.TextField(blank=True, null=True)
    LakasElhelyezkedese = models.TextField(blank=True, null=True)
    Epitoanyag = models.TextField(blank=True, null=True)
    EpitmenyKora = models.TextField(blank=True, null=True)
    APeneszedesParalecsapodasMegjelenese = models.BigIntegerField(blank=True, null=True)
    NyilaszarokTipusa = models.TextField(blank=True, null=True)
    APeneszedesselParalecsapodassalErintettHelyisegek = models.BigIntegerField(
        blank=True, null=True
    )
    APeneszedesElofordulasaFokent = models.TextField(blank=True, null=True)
    LakasAlapterulete = models.TextField(blank=True, null=True)
    LakasBelmagassaga = models.TextField(blank=True, null=True)
    KulsoTartoFalakVastagsaga = models.TextField(blank=True, null=True)
    KulsoSzigetelesVastagsaga = models.TextField(blank=True, null=True)
    ALakasFodemeMennyezete = models.TextField(blank=True, null=True)
    LakoHelyisegekSzamaSzobakNappali = models.TextField(blank=True, null=True)
    VizesHelyisegekSzamaFurdoWcKonyhaMosokonyhaStb = models.TextField(
        blank=True, null=True
    )
    EgyebHelyisegekSzamaTaroloKamraGardrobStb = models.TextField(blank=True, null=True)
    KuszobABelteriAjtokon = models.TextField(blank=True, null=True)
    LakasFutese = models.TextField(blank=True, null=True)
    ALakasbanTalalhatoGazkeszulekek = models.BigIntegerField(blank=True, null=True)
    ALakasbanTalalhatoSzellozesiLehetosegek = models.BigIntegerField(
        blank=True, null=True
    )
    ALakasbanLakoSzemelyekSzama = models.TextField(blank=True, null=True)
    AlaprajzFeltoltese2 = models.TextField(blank=True, null=True)
    PeneszedesrolFenykep = models.TextField(blank=True, null=True)
    EgyebHasznosKep = models.TextField(blank=True, null=True)
    FenykepAKazanrol = models.TextField(blank=True, null=True)
    ACsaladbanVan = models.BigIntegerField(blank=True, null=True)
    FelmerolapotKitoltotte = models.BigIntegerField(blank=True, null=True)
    MikorKuldtunkAjanlatot = models.TextField(blank=True, null=True)
    Enum1183 = models.TextField(blank=True, null=True)
    Text1184 = models.TextField(blank=True, null=True)
    Enum1185 = models.TextField(blank=True, null=True)
    Int1186 = models.TextField(blank=True, null=True)
    File1188 = models.TextField(blank=True, null=True)
    DateTime1189 = models.TextField(blank=True, null=True)
    Enum1190 = models.TextField(blank=True, null=True)
    Text1191 = models.TextField(blank=True, null=True)
    DateTime1192 = models.TextField(blank=True, null=True)
    AFeladatLeirasaABeepitoknek = models.TextField(blank=True, null=True)
    KiMerteFel = models.BigIntegerField(blank=True, null=True)
    FelmeresiJegyzetek = models.TextField(blank=True, null=True)
    BeepitesiJegyzetek = models.TextField(blank=True, null=True)
    KepekABeepitesrol = models.TextField(blank=True, null=True)
    KepekABeepiteshez01 = models.TextField(blank=True, null=True)
    KepekABeepiteshez02 = models.TextField(blank=True, null=True)
    KepekABeepiteshez03 = models.TextField(blank=True, null=True)
    KepekABeepitesrol02 = models.TextField(blank=True, null=True)
    VentiTipus = models.TextField(blank=True, null=True)
    HazVLakas = models.TextField(blank=True, null=True)
    AblakosLegbevezetok = models.TextField(blank=True, null=True)
    FaliLegbevezetok = models.TextField(blank=True, null=True)
    HolLesznekALegbevezetok = models.TextField(blank=True, null=True)
    HolLeszFali = models.TextField(blank=True, null=True)
    HanyAjtoFuras = models.TextField(blank=True, null=True)
    MelyikAjtok = models.TextField(blank=True, null=True)
    SzellozoRacsHelye = models.TextField(blank=True, null=True)
    HanyBelsoFalAtbontasLesz = models.TextField(blank=True, null=True)
    EgyebKotojelesSorkbaRendezve = models.TextField(blank=True, null=True)
    MegjegyzesAVentiHelyerolABeepitoknek = models.TextField(blank=True, null=True)
    NettoAr = models.TextField(blank=True, null=True)
    BruttoAr = models.TextField(blank=True, null=True)
    NettoArFt = models.TextField(blank=True, null=True)
    BruttoAr2 = models.TextField(blank=True, null=True)
    BruttoArBetuvelKiirva = models.TextField(blank=True, null=True)
    Ebbol957 = models.TextField(blank=True, null=True)
    Ebbol916 = models.TextField(blank=True, null=True)
    N780as = models.TextField(blank=True, null=True)
    HolLesz916os = models.TextField(blank=True, null=True)
    HolLesz957es = models.TextField(blank=True, null=True)
    N716os = models.TextField(blank=True, null=True)
    EgyebMunkakCsakABeepitokLatjak = models.TextField(blank=True, null=True)
    ParaerzekelosBcx = models.TextField(blank=True, null=True)
    Hova = models.TextField(blank=True, null=True)
    HolLeszA = models.TextField(blank=True, null=True)
    Hova2 = models.TextField(blank=True, null=True)
    ParaEsMozgasErzekelosBxc = models.TextField(blank=True, null=True)
    MozgaserzekelosBxc = models.TextField(blank=True, null=True)
    Hova3 = models.TextField(blank=True, null=True)
    Zsirszuro = models.TextField(blank=True, null=True)
    HolLeszZajcsillapitoBetet = models.TextField(blank=True, null=True)
    ZajcsillapitoBetetFali = models.TextField(blank=True, null=True)
    V2aV4aVamTipusa = models.TextField(blank=True, null=True)
    HolLeszAVentiEsHogyLeszKialakitvaAjanlatonEzLatszik = models.TextField(
        blank=True, null=True
    )
    KialakitasrolEgyebInfoABeepitoknek = models.TextField(blank=True, null=True)
    MegjegyzesAKabelezeshezABeepitoknek = models.TextField(blank=True, null=True)
    Cim = models.TextField(blank=True, null=True)
    MegjegyzesACimmelKapcsolatban = models.TextField(blank=True, null=True)
    HolLeszEar201es = models.TextField(blank=True, null=True)
    Ear201Db = models.TextField(blank=True, null=True)
    HolLeszEar200as = models.TextField(blank=True, null=True)
    Ear200asDb = models.TextField(blank=True, null=True)
    HolLeszRedonytokos = models.TextField(blank=True, null=True)
    RedonytokosLegbevezetoDb = models.TextField(blank=True, null=True)
    MegjALegbevezetokhozSzinEsovedoStb = models.TextField(blank=True, null=True)
    EgyebInfoALegbevezetokBeepitesehez = models.TextField(blank=True, null=True)
    KulonlegesSzinHelyEsovedoStb = models.TextField(blank=True, null=True)
    EgyebInfoARedonytokosBeepitesehez = models.TextField(blank=True, null=True)
    OsszesenHanyDb201200Mind = models.TextField(blank=True, null=True)
    AjtoszellozoKarikaSzine = models.TextField(blank=True, null=True)
    N716osSzine = models.TextField(blank=True, null=True)
    N916osSzine = models.TextField(blank=True, null=True)
    HaKellCsovezniMibolMennyiKell2 = models.TextField(blank=True, null=True)
    GaranciavalArralKapcsolatosMegjegyzes = models.TextField(blank=True, null=True)
    PluszVisszaaramlasGatlokDb = models.TextField(blank=True, null=True)
    HovaKellAPlusszVisszaaramlasGatlo = models.TextField(blank=True, null=True)
    Int1320 = models.TextField(blank=True, null=True)
    Enum1322 = models.TextField(blank=True, null=True)
    Text1323 = models.TextField(blank=True, null=True)
    Enum1326 = models.TextField(blank=True, null=True)
    Text1335 = models.TextField(blank=True, null=True)
    LegutolsoAjanlat = models.TextField(blank=True, null=True)
    KepAPeneszesFalszakaszrol = models.TextField(blank=True, null=True)
    MegjegyzesAPeneszedesselKapcsolatba = models.TextField(blank=True, null=True)
    AblakokAjtokKulsoBelsoSzine = models.TextField(blank=True, null=True)
    MegjegyzesAzAblakokkalAjtokkalKapcsolatba = models.TextField(blank=True, null=True)
    AzAlaprajznakTartalmazniaKell = models.BigIntegerField(blank=True, null=True)
    NemKapGariSzerzodest = models.BigIntegerField(blank=True, null=True)
    HolVanAram2 = models.TextField(blank=True, null=True)
    VentilatorKapcsolasanakKialakitasa2 = models.TextField(blank=True, null=True)
    KepABeepiteshez04 = models.TextField(blank=True, null=True)
    Enum1361 = models.TextField(blank=True, null=True)
    Text1362 = models.TextField(blank=True, null=True)
    Enum1363 = models.TextField(blank=True, null=True)
    File1365 = models.TextField(blank=True, null=True)
    Text1367 = models.TextField(blank=True, null=True)
    Text1368 = models.TextField(blank=True, null=True)
    Enum1370 = models.TextField(blank=True, null=True)
    TervrajzFeltoltes = models.TextField(blank=True, null=True)
    HirlevelreFeliratkozas = models.BigIntegerField(blank=True, null=True)
    GdprNyilatkozat = models.BigIntegerField(blank=True, null=True)
    MikorraTerveziAFelujitast = models.TextField(blank=True, null=True)
    MiAzUgyfelFoSzempontja = models.TextField(blank=True, null=True)
    IlyenVoltKep1 = models.TextField(blank=True, null=True)
    IlyenVoltKep2 = models.TextField(blank=True, null=True)
    KivitelezesInfo = models.TextField(blank=True, null=True)
    IlyenLettKep1 = models.TextField(blank=True, null=True)
    IlyenLettKep2 = models.TextField(blank=True, null=True)
    MelyikBrigadVolt = models.TextField(blank=True, null=True)
    ElszamolasDatum = models.TextField(blank=True, null=True)
    ElszamolasiOsszeg = models.TextField(blank=True, null=True)
    PenzugyiMegjegyzes = models.TextField(blank=True, null=True)
    AnyagKoltseg = models.TextField(blank=True, null=True)
    ReklamacioInfo = models.TextField(blank=True, null=True)
    ReklamacioKoltsege = models.TextField(blank=True, null=True)
    FelmeresDatuma = models.TextField(blank=True, null=True)
    EgyebSzempontok = models.BigIntegerField(blank=True, null=True)
    DateTime1415 = models.TextField(blank=True, null=True)
    Text1416 = models.TextField(blank=True, null=True)
    Int1417 = models.TextField(blank=True, null=True)
    Set1418 = models.BigIntegerField(blank=True, null=True)
    Enum1419 = models.TextField(blank=True, null=True)
    Set1420 = models.BigIntegerField(blank=True, null=True)
    DateTime1421 = models.TextField(blank=True, null=True)
    File1422 = models.TextField(blank=True, null=True)
    File1423 = models.TextField(blank=True, null=True)
    Enum1424 = models.TextField(blank=True, null=True)
    Enum1425 = models.TextField(blank=True, null=True)
    Set1426 = models.BigIntegerField(blank=True, null=True)
    File1427 = models.TextField(blank=True, null=True)
    DateTime1428 = models.TextField(blank=True, null=True)
    Enum1429 = models.TextField(blank=True, null=True)
    DateTime1430 = models.TextField(blank=True, null=True)
    Enum1431 = models.TextField(blank=True, null=True)
    Text1432 = models.TextField(blank=True, null=True)
    DateTime1433 = models.TextField(blank=True, null=True)
    File1434 = models.TextField(blank=True, null=True)
    Set1435 = models.BigIntegerField(blank=True, null=True)
    DateTime1436 = models.TextField(blank=True, null=True)
    ParkolasiLehetosegek = models.BigIntegerField(blank=True, null=True)
    FelmeresiJegyzetek2 = models.TextField(blank=True, null=True)
    VentiTipusa = models.TextField(blank=True, null=True)
    Melyikhelyisegbenleszaventilista = models.TextField(blank=True, null=True)
    Hogyleszkialakitvaaventi = models.TextField(blank=True, null=True)
    MegjegyzesACsovezeshez = models.TextField(blank=True, null=True)
    Megjegyzesaventihelyerolabeepitoknek = models.TextField(blank=True, null=True)
    N780as2 = models.TextField(blank=True, null=True)
    HovaKerulA780as = models.TextField(blank=True, null=True)
    N957esDb = models.TextField(blank=True, null=True)
    HovaKerulA957es = models.TextField(blank=True, null=True)
    ZajcsillapitoBetetFaliDb = models.TextField(blank=True, null=True)
    HolLeszZajcsillapitoBetet2 = models.TextField(blank=True, null=True)
    EgyebInfoALegbevezetokBeepitesehez2 = models.TextField(blank=True, null=True)
    RajzABeepiteshez = models.TextField(blank=True, null=True)
    UjSzovegdobozAFeladatLeirasaABeepitoknek = models.TextField(blank=True, null=True)
    ParkolasiLehetosegek2 = models.BigIntegerField(blank=True, null=True)
    MiAzUgyfelFoSzempontja2 = models.TextField(blank=True, null=True)
    EgyebSzempontok2 = models.BigIntegerField(blank=True, null=True)
    ErtekesitesiInfok = models.TextField(blank=True, null=True)
    KepABeepiteshez05 = models.TextField(blank=True, null=True)
    IngatlanHasznalat2 = models.TextField(blank=True, null=True)
    KivitelezesCime = models.TextField(blank=True, null=True)
    MegjegyzesACimmelKapcsolatban2 = models.TextField(blank=True, null=True)
    ProjektLeiras = models.TextField(blank=True, null=True)
    FelmeresTeljesOsszeg = models.TextField(blank=True, null=True)
    Felmeres18000 = models.BigIntegerField(blank=True, null=True)
    SzervezetiTerulet = models.TextField(blank=True, null=True)
    ProjektStart = models.TextField(blank=True, null=True)
    ProjektVege = models.TextField(blank=True, null=True)
    ProjektKoltsegeNetto = models.TextField(blank=True, null=True)
    HaviKoltsegNetto = models.TextField(blank=True, null=True)
    KapcsolodoLink1 = models.TextField(blank=True, null=True)
    KapcsolodoLink2 = models.TextField(blank=True, null=True)
    IngatlanHasznalata = models.TextField(blank=True, null=True)
    MegjegyzesCimmelKapcsolatban = models.TextField(blank=True, null=True)
    NemKapszGariSzerzodest = models.BigIntegerField(blank=True, null=True)
    BeepitesDatuma = models.TextField(blank=True, null=True)
    KepABeepiteshez01 = models.TextField(blank=True, null=True)
    KepABeepiteshez02 = models.TextField(blank=True, null=True)
    KepABeepiteshez03 = models.TextField(blank=True, null=True)
    KepABeepiteshez06 = models.TextField(blank=True, null=True)
    KepABeepiteshez07 = models.TextField(blank=True, null=True)
    HovaKerul716os = models.TextField(blank=True, null=True)
    N716osSzineHaNemFeher = models.TextField(blank=True, null=True)
    HovaKerul916os = models.TextField(blank=True, null=True)
    N916osSzineHaNemFeher = models.TextField(blank=True, null=True)
    KulonlegesSzinHelyEsovedoStb2 = models.TextField(blank=True, null=True)
    HolLeszEar201es2 = models.TextField(blank=True, null=True)
    HolLeszEar200as2 = models.TextField(blank=True, null=True)
    KulonlegesSzinHelyEsovedoStb3 = models.TextField(blank=True, null=True)
    OsszesFaliLegbevezetok2 = models.TextField(blank=True, null=True)
    OsszesenHanyDb716916Mind2 = models.TextField(blank=True, null=True)
    N716osDb2 = models.TextField(blank=True, null=True)
    N916osDb3 = models.TextField(blank=True, null=True)
    OsszesenHanyDb201200Mind3 = models.TextField(blank=True, null=True)
    Ear201esDb2 = models.TextField(blank=True, null=True)
    Ear200asDb3 = models.TextField(blank=True, null=True)
    HanyAjtofuras = models.TextField(blank=True, null=True)
    MelyikAjtok2 = models.TextField(blank=True, null=True)
    AjtoszellozoKarikaSzineHaNemFeher = models.TextField(blank=True, null=True)
    PluszVisszaaramlasGatlokDb2 = models.TextField(blank=True, null=True)
    HovaKellAPluszVisszaaramlasGatlo = models.TextField(blank=True, null=True)
    EgyebMunkakArajanlatonIsRajtaLesz = models.TextField(blank=True, null=True)
    EgyebMunkakCsakABeepitokLatjak2 = models.TextField(blank=True, null=True)
    NyiltKazanjaVan2 = models.BigIntegerField(blank=True, null=True)
    AHaznakKozpontiSzellozoVentilatoraVan = models.BigIntegerField(
        blank=True, null=True
    )
    HanyOrasMunkaAlapBeallitas36 = models.TextField(blank=True, null=True)
    GaranciavalArralKapcsolatosMegjegyzes2 = models.TextField(blank=True, null=True)
    IdopontTemaja = models.TextField(blank=True, null=True)
    File1590 = models.TextField(blank=True, null=True)
    DateTime1591 = models.TextField(blank=True, null=True)
    Enum1592 = models.TextField(blank=True, null=True)
    DateTime1593 = models.TextField(blank=True, null=True)
    DateTime1594 = models.TextField(blank=True, null=True)
    Text1595 = models.TextField(blank=True, null=True)
    Enum1596 = models.TextField(blank=True, null=True)
    String1597 = models.TextField(blank=True, null=True)
    DateTime1598 = models.TextField(blank=True, null=True)
    Float1599 = models.TextField(blank=True, null=True)
    DateTime1600 = models.TextField(blank=True, null=True)
    File1601 = models.TextField(blank=True, null=True)
    Text1602 = models.TextField(blank=True, null=True)
    ElolegOsszege = models.TextField(blank=True, null=True)
    ElolegFizetveDatum = models.TextField(blank=True, null=True)
    VegszamlaOsszege = models.TextField(blank=True, null=True)
    VegszamlaFizetveDatum = models.TextField(blank=True, null=True)
    FelmeresDijbekeroKikuldve = models.TextField(blank=True, null=True)
    MitVett = models.TextField(blank=True, null=True)
    FeladatLeirasaBeepitoknek = models.TextField(blank=True, null=True)
    FeladatLeirasaBeepitoknek2 = models.TextField(blank=True, null=True)
    BeepitesUtaniJegyzet = models.TextField(blank=True, null=True)
    HolLeszAVentiEsHogyLeszKialakitvaAjanlatonEzLatszik2 = models.TextField(
        blank=True, null=True
    )
    KialakitasrolEgyebInfoABeepitoknek2 = models.TextField(blank=True, null=True)
    HaKellCsovezniMibolMennyiKell = models.TextField(blank=True, null=True)
    ParaerzekelosBcx2 = models.TextField(blank=True, null=True)
    HolLeszAParaerzekelosBcx = models.TextField(blank=True, null=True)
    MozgaserzekelosBxc2 = models.TextField(blank=True, null=True)
    HolLeszAMozgaserzekelosBxc = models.TextField(blank=True, null=True)
    ParaEsMozgasErzekelosBxc2 = models.TextField(blank=True, null=True)
    HolLeszAParaEsMozgaserzekelosBxc = models.TextField(blank=True, null=True)
    Zsirszuro2 = models.TextField(blank=True, null=True)
    HolLeszAZsirszuro = models.TextField(blank=True, null=True)
    GaranciavalArralKapcsolatosMegjegyzes3 = models.TextField(blank=True, null=True)
    HogyLeszKialakitva = models.TextField(blank=True, null=True)
    EgyediKialakitas = models.TextField(blank=True, null=True)
    HanyDarabMfo = models.TextField(blank=True, null=True)
    MfoKivezetesHolLesz = models.TextField(blank=True, null=True)
    MasHelyenBontas = models.TextField(blank=True, null=True)
    Felmeres2 = models.TextField(blank=True, null=True)
    MelyikHelyisegbeKerulUb = models.TextField(blank=True, null=True)
    MasodlagosVentilatorTipusa = models.TextField(blank=True, null=True)
    MasodlagosVentilatorInfoB = models.TextField(blank=True, null=True)
    AjanlatErtekeNettoHuf = models.TextField(blank=True, null=True)
    AjanlatErtekeBrutto = models.TextField(blank=True, null=True)
    Emelet = models.TextField(blank=True, null=True)
    NyiltEgesteruKemenyesGazkazan2 = models.TextField(blank=True, null=True)
    KepABeepiteshez08 = models.TextField(blank=True, null=True)
    KepABeepiteshez09 = models.TextField(blank=True, null=True)
    MasodlagosVentilatorHelyeUb = models.BigIntegerField(blank=True, null=True)
    KozpontiVentilatorTipusa = models.TextField(blank=True, null=True)
    HolLeszAVenti = models.TextField(blank=True, null=True)
    AFalAtbontasHelyeU = models.BigIntegerField(blank=True, null=True)
    FalAtbontasDbU = models.TextField(blank=True, null=True)
    KarikaSzine = models.TextField(blank=True, null=True)
    PluszVisszaaramlasGatlo = models.TextField(blank=True, null=True)
    JavitasDatum = models.TextField(blank=True, null=True)
    TetoszellozoCserep = models.BigIntegerField(blank=True, null=True)
    LemondtaABeepitest = models.BigIntegerField(blank=True, null=True)
    AjanlatAfaTartalma = models.TextField(blank=True, null=True)
    AjanlatSablonTipusa = models.TextField(blank=True, null=True)
    EmailSorozatotKert = models.BigIntegerField(blank=True, null=True)
    AjanloNeveKampany = models.TextField(blank=True, null=True)
    String1679 = models.TextField(blank=True, null=True)
    FizetendoNetto18eFt = models.TextField(blank=True, null=True)
    FizetendoBrutto = models.TextField(blank=True, null=True)
    PasszivRendszer = models.BigIntegerField(blank=True, null=True)
    NyiltKazanjaVan = models.BigIntegerField(blank=True, null=True)
    Ahaznakkoszpontiszellozoventilatoravan = models.BigIntegerField(
        blank=True, null=True
    )
    HirlevelreFeliratkozas2 = models.BigIntegerField(blank=True, null=True)
    GdprNyilatkozat2 = models.BigIntegerField(blank=True, null=True)
    HogyanTalaltRankAjanloNeve = models.TextField(blank=True, null=True)
    KiEpitetteBe = models.BigIntegerField(blank=True, null=True)
    NettoBeepitesiDij = models.TextField(blank=True, null=True)
    PenzugyilegRendezett = models.BigIntegerField(blank=True, null=True)
    KepABeepiteshez010 = models.TextField(blank=True, null=True)
    Set1698 = models.BigIntegerField(blank=True, null=True)
    HanyadikEmeltHaNincsLift = models.TextField(blank=True, null=True)
    MelyikHelyisegbeKerulU = models.TextField(blank=True, null=True)
    HogyLeszKialakitvaU = models.TextField(blank=True, null=True)
    EgyediKialakitasU = models.TextField(blank=True, null=True)
    MegjegyzesACsovezeshez2 = models.TextField(blank=True, null=True)
    QfaHelye = models.TextField(blank=True, null=True)
    Aram = models.TextField(blank=True, null=True)
    AramEgyedi = models.TextField(blank=True, null=True)
    VentilatorTipusaU = models.TextField(blank=True, null=True)
    HanyDarabVentilatorU = models.TextField(blank=True, null=True)
    MasodlagosVentilatorHelyeU = models.BigIntegerField(blank=True, null=True)
    HogyLeszKialakitvaU2 = models.TextField(blank=True, null=True)
    EgyediKialakitasU2 = models.TextField(blank=True, null=True)
    MegjegyzesAMasodlagosVentilatorBeepitesehez = models.TextField(
        blank=True, null=True
    )
    HolLeszAVentilatorU = models.TextField(blank=True, null=True)
    HolLeszAVentilatorEgyediU = models.TextField(blank=True, null=True)
    FalAtbontasHelyeU = models.BigIntegerField(blank=True, null=True)
    FalAtbontasHelyeEgyediU = models.TextField(blank=True, null=True)
    TetoszellozoCserep2 = models.BigIntegerField(blank=True, null=True)
    EmeletiLakas = models.BigIntegerField(blank=True, null=True)
    HirlevelnelTobbInfotKert = models.BigIntegerField(blank=True, null=True)
    EmailSorozat = models.BigIntegerField(blank=True, null=True)
    EgyebIndok = models.TextField(blank=True, null=True)
    FizetesiMod = models.TextField(blank=True, null=True)
    FelmeresSzamlas = models.BigIntegerField(blank=True, null=True)
    BeepitesFizetesiMod = models.TextField(blank=True, null=True)
    BeepitesSzamlas = models.BigIntegerField(blank=True, null=True)
    FelmeresOsszegeEgyeb = models.TextField(blank=True, null=True)
    BruttoBeepitesiDij = models.TextField(blank=True, null=True)
    GaranciaJavitasIdopontja = models.TextField(blank=True, null=True)
    KepABeepiteshez011 = models.TextField(blank=True, null=True)
    KepABeepiteshez012 = models.TextField(blank=True, null=True)
    KepABeepiteshez10 = models.TextField(blank=True, null=True)
    Enum1740 = models.TextField(blank=True, null=True)
    Enum1741 = models.TextField(blank=True, null=True)
    Enum1742 = models.TextField(blank=True, null=True)
    Text1743 = models.TextField(blank=True, null=True)
    MilyenProblemavalFordultHozzank = models.TextField(blank=True, null=True)
    File1763 = models.TextField(blank=True, null=True)
    Int1764 = models.TextField(blank=True, null=True)
    DateTime1765 = models.TextField(blank=True, null=True)
    Float1766 = models.TextField(blank=True, null=True)
    Enum1767 = models.TextField(blank=True, null=True)
    DateTime1768 = models.TextField(blank=True, null=True)
    Enum1769 = models.TextField(blank=True, null=True)
    Text1770 = models.TextField(blank=True, null=True)
    DateTime1771 = models.TextField(blank=True, null=True)
    Set1772 = models.BigIntegerField(blank=True, null=True)
    Set1773 = models.BigIntegerField(blank=True, null=True)
    Set1774 = models.BigIntegerField(blank=True, null=True)
    Enum1775 = models.TextField(blank=True, null=True)
    Text1776 = models.TextField(blank=True, null=True)
    Enum1777 = models.TextField(blank=True, null=True)
    Enum1778 = models.TextField(blank=True, null=True)
    Set1779 = models.BigIntegerField(blank=True, null=True)
    Enum1780 = models.TextField(blank=True, null=True)
    Enum1781 = models.TextField(blank=True, null=True)
    File1782 = models.TextField(blank=True, null=True)
    Int1783 = models.TextField(blank=True, null=True)
    Float1784 = models.TextField(blank=True, null=True)
    DateTime1785 = models.TextField(blank=True, null=True)
    String1786 = models.TextField(blank=True, null=True)
    Enum1787 = models.TextField(blank=True, null=True)
    Set1788 = models.BigIntegerField(blank=True, null=True)
    Enum1789 = models.TextField(blank=True, null=True)
    Int1790 = models.TextField(blank=True, null=True)
    Text1791 = models.TextField(blank=True, null=True)
    DateTime1792 = models.TextField(blank=True, null=True)
    Set1793 = models.BigIntegerField(blank=True, null=True)
    Int1794 = models.TextField(blank=True, null=True)
    Enum1795 = models.TextField(blank=True, null=True)
    Enum1796 = models.TextField(blank=True, null=True)
    Enum1797 = models.TextField(blank=True, null=True)
    Enum1798 = models.TextField(blank=True, null=True)
    Enum1799 = models.TextField(blank=True, null=True)
    DateTime1800 = models.TextField(blank=True, null=True)
    Enum1801 = models.TextField(blank=True, null=True)
    Enum1802 = models.TextField(blank=True, null=True)
    Text1803 = models.TextField(blank=True, null=True)
    Int1804 = models.TextField(blank=True, null=True)
    Int1805 = models.TextField(blank=True, null=True)
    Enum1806 = models.TextField(blank=True, null=True)
    Enum1807 = models.TextField(blank=True, null=True)
    File1808 = models.TextField(blank=True, null=True)
    Text1809 = models.TextField(blank=True, null=True)
    String1810 = models.TextField(blank=True, null=True)
    DateTime1811 = models.TextField(blank=True, null=True)
    File1812 = models.TextField(blank=True, null=True)
    Enum1813 = models.TextField(blank=True, null=True)
    String1814 = models.TextField(blank=True, null=True)
    Float1815 = models.TextField(blank=True, null=True)
    DateTime1816 = models.TextField(blank=True, null=True)
    DateTime1817 = models.TextField(blank=True, null=True)
    File1818 = models.TextField(blank=True, null=True)
    File1819 = models.TextField(blank=True, null=True)
    File1820 = models.TextField(blank=True, null=True)
    File1821 = models.TextField(blank=True, null=True)
    Enum1822 = models.TextField(blank=True, null=True)
    Enum1823 = models.TextField(blank=True, null=True)
    Enum1824 = models.TextField(blank=True, null=True)
    Enum1825 = models.TextField(blank=True, null=True)
    Text1826 = models.TextField(blank=True, null=True)
    Text1827 = models.TextField(blank=True, null=True)
    Text1828 = models.TextField(blank=True, null=True)
    File1829 = models.TextField(blank=True, null=True)
    Text1830 = models.TextField(blank=True, null=True)
    Text1831 = models.TextField(blank=True, null=True)
    Enum1832 = models.TextField(blank=True, null=True)
    Enum1833 = models.TextField(blank=True, null=True)
    DateTime1834 = models.TextField(blank=True, null=True)
    Int1835 = models.TextField(blank=True, null=True)
    Float1836 = models.TextField(blank=True, null=True)
    Enum1837 = models.TextField(blank=True, null=True)
    Text1838 = models.TextField(blank=True, null=True)
    Enum1839 = models.TextField(blank=True, null=True)
    Enum1840 = models.TextField(blank=True, null=True)
    File1841 = models.TextField(blank=True, null=True)
    Enum1842 = models.TextField(blank=True, null=True)
    DateTime1843 = models.TextField(blank=True, null=True)
    DateTime1844 = models.TextField(blank=True, null=True)
    File1845 = models.TextField(blank=True, null=True)
    Enum1846 = models.TextField(blank=True, null=True)
    Enum1847 = models.TextField(blank=True, null=True)
    Enum1848 = models.TextField(blank=True, null=True)
    Enum1849 = models.TextField(blank=True, null=True)
    Enum1850 = models.TextField(blank=True, null=True)
    File1851 = models.TextField(blank=True, null=True)
    Enum1852 = models.TextField(blank=True, null=True)
    Enum1853 = models.TextField(blank=True, null=True)
    Enum1854 = models.TextField(blank=True, null=True)
    File1855 = models.TextField(blank=True, null=True)
    Enum1856 = models.TextField(blank=True, null=True)
    Enum1857 = models.TextField(blank=True, null=True)
    Int1858 = models.TextField(blank=True, null=True)
    DateTime1859 = models.TextField(blank=True, null=True)
    Int1860 = models.TextField(blank=True, null=True)
    Float1861 = models.TextField(blank=True, null=True)
    Enum1862 = models.TextField(blank=True, null=True)
    File1863 = models.TextField(blank=True, null=True)
    DateTime1864 = models.TextField(blank=True, null=True)
    String1865 = models.TextField(blank=True, null=True)
    String1866 = models.TextField(blank=True, null=True)
    File1867 = models.TextField(blank=True, null=True)
    File1868 = models.TextField(blank=True, null=True)
    Text1869 = models.TextField(blank=True, null=True)
    File1870 = models.TextField(blank=True, null=True)
    Enum1871 = models.TextField(blank=True, null=True)
    Enum1872 = models.TextField(blank=True, null=True)
    DateTime1873 = models.TextField(blank=True, null=True)
    DateTime1874 = models.TextField(blank=True, null=True)
    Set1875 = models.BigIntegerField(blank=True, null=True)
    Text1876 = models.TextField(blank=True, null=True)
    DateTime1877 = models.TextField(blank=True, null=True)
    DateTime1878 = models.TextField(blank=True, null=True)
    Int1879 = models.TextField(blank=True, null=True)
    Float1880 = models.TextField(blank=True, null=True)
    File1881 = models.TextField(blank=True, null=True)
    File1882 = models.TextField(blank=True, null=True)
    Enum1883 = models.TextField(blank=True, null=True)
    Float1884 = models.TextField(blank=True, null=True)
    Float1885 = models.TextField(blank=True, null=True)
    String1886 = models.TextField(blank=True, null=True)
    File1887 = models.TextField(blank=True, null=True)
    Text1888 = models.TextField(blank=True, null=True)
    Text1889 = models.TextField(blank=True, null=True)
    Set1890 = models.BigIntegerField(blank=True, null=True)
    Set1891 = models.BigIntegerField(blank=True, null=True)
    File1892 = models.TextField(blank=True, null=True)
    File1893 = models.TextField(blank=True, null=True)
    File1894 = models.TextField(blank=True, null=True)
    Enum1895 = models.TextField(blank=True, null=True)
    Enum1896 = models.TextField(blank=True, null=True)
    DateTime1897 = models.TextField(blank=True, null=True)
    Int1898 = models.TextField(blank=True, null=True)
    Float1899 = models.TextField(blank=True, null=True)
    Enum1900 = models.TextField(blank=True, null=True)
    File1901 = models.TextField(blank=True, null=True)
    DateTime1902 = models.TextField(blank=True, null=True)
    DateTime1903 = models.TextField(blank=True, null=True)
    String1904 = models.TextField(blank=True, null=True)
    File1905 = models.TextField(blank=True, null=True)
    Text1906 = models.TextField(blank=True, null=True)
    File1907 = models.TextField(blank=True, null=True)
    File1908 = models.TextField(blank=True, null=True)
    DateTime1909 = models.TextField(blank=True, null=True)
    String1910 = models.TextField(blank=True, null=True)
    Enum1911 = models.TextField(blank=True, null=True)
    Int1912 = models.TextField(blank=True, null=True)
    Enum1913 = models.TextField(blank=True, null=True)
    File1914 = models.TextField(blank=True, null=True)
    Float1915 = models.TextField(blank=True, null=True)
    Float1916 = models.TextField(blank=True, null=True)
    Float1917 = models.TextField(blank=True, null=True)
    Enum1918 = models.TextField(blank=True, null=True)
    Enum1919 = models.TextField(blank=True, null=True)
    Enum1920 = models.TextField(blank=True, null=True)
    Enum1921 = models.TextField(blank=True, null=True)
    Enum1922 = models.TextField(blank=True, null=True)
    DateTime1923 = models.TextField(blank=True, null=True)
    String1924 = models.TextField(blank=True, null=True)
    Enum1925 = models.TextField(blank=True, null=True)
    Float1926 = models.TextField(blank=True, null=True)
    DateTime1927 = models.TextField(blank=True, null=True)
    Enum1928 = models.TextField(blank=True, null=True)
    DateTime1929 = models.TextField(blank=True, null=True)
    File1930 = models.TextField(blank=True, null=True)
    File1931 = models.TextField(blank=True, null=True)
    File1932 = models.TextField(blank=True, null=True)
    Int1933 = models.TextField(blank=True, null=True)
    Float1934 = models.TextField(blank=True, null=True)
    Enum1935 = models.TextField(blank=True, null=True)
    Enum1936 = models.TextField(blank=True, null=True)
    Float1937 = models.TextField(blank=True, null=True)
    DateTime1938 = models.TextField(blank=True, null=True)
    Float1939 = models.TextField(blank=True, null=True)
    Float1940 = models.TextField(blank=True, null=True)
    File1941 = models.TextField(blank=True, null=True)
    Text1942 = models.TextField(blank=True, null=True)
    Float1944 = models.TextField(blank=True, null=True)
    DateTime1945 = models.TextField(blank=True, null=True)
    Enum1951 = models.TextField(blank=True, null=True)
    DateTime1953 = models.TextField(blank=True, null=True)
    ElutasitasOka = models.BigIntegerField(blank=True, null=True)
    MegjegyzesLeiras = models.TextField(blank=True, null=True)
    FelmeresiKepek = models.TextField(blank=True, null=True)
    Enum1969 = models.TextField(blank=True, null=True)
    Text1970 = models.TextField(blank=True, null=True)
    MilyenMasProblema = models.BigIntegerField(blank=True, null=True)
    Tavolsag = models.TextField(blank=True, null=True)
    FelmeresiDij = models.IntegerField(blank=True, null=True)
    FelmeresIdopontja2 = models.DateTimeField(blank=True, null=True)
    MiAzUgyfelFoSzempontja3 = models.TextField(blank=True, null=True)
    EgyebSzempontok3 = models.TextField(blank=True, null=True)
    Cim2 = models.TextField(blank=True, null=True)
    UtazasiIdoKozponttol = models.TextField(blank=True, null=True)
    MehetADijbekero = models.TextField(blank=True, null=True)
    DijbekeroMegjegyzes = models.TextField(blank=True, null=True)
    DijbekeroSzama = models.TextField(blank=True, null=True)
    DijbekeroPdf = models.TextField(blank=True, null=True)
    Felmero = models.TextField(blank=True, null=True)
    MegjegyzesAMunkalapra = models.TextField(blank=True, null=True)
    SzovegesErtekeles = models.TextField(blank=True, null=True)
    Pontszam = models.TextField(blank=True, null=True)
    SzovegesErtekeles2 = models.TextField(blank=True, null=True)
    Text2006 = models.TextField(blank=True, null=True)
    Enum2007 = models.TextField(blank=True, null=True)
    DateTime2008 = models.TextField(blank=True, null=True)
    Enum2009 = models.TextField(blank=True, null=True)
    Beepitok = models.TextField(blank=True, null=True)
    Enum2016 = models.TextField(blank=True, null=True)
    Text2017 = models.TextField(blank=True, null=True)
    File2018 = models.TextField(blank=True, null=True)
    Enum2019 = models.TextField(blank=True, null=True)
    Set2020 = models.BigIntegerField(blank=True, null=True)
    DateTime2021 = models.TextField(blank=True, null=True)
    DateTime2022 = models.TextField(blank=True, null=True)
    Enum2023 = models.TextField(blank=True, null=True)
    File2024 = models.TextField(blank=True, null=True)
    MiertLettSikertelenABeepites = models.TextField(blank=True, null=True)
    MiertLettSikertelenABeepitesSzovegesen = models.TextField(blank=True, null=True)
    MennyireVoltMegelegedve = models.TextField(blank=True, null=True)
    Pontszam2 = models.TextField(blank=True, null=True)
    SzovegesErtekeles3 = models.TextField(blank=True, null=True)
    Alaprajz = models.TextField(blank=True, null=True)
    LezarasOka = models.BigIntegerField(blank=True, null=True)
    LezarasSzovegesen = models.TextField(blank=True, null=True)
    Telepules = models.TextField(blank=True, null=True)
    Iranyitoszam = models.TextField(blank=True, null=True)
    Forras = models.TextField(blank=True, null=True)
    Megye = models.TextField(blank=True, null=True)
    Orszag = models.TextField(blank=True, null=True)
    FelmeresIdopontja3 = models.TextField(blank=True, null=True)
    MilyenRendszertTervezel = models.TextField(blank=True, null=True)
    MilyenVentilatortTervezel = models.TextField(blank=True, null=True)
    HanyDarabVentilatortTervezel = models.TextField(blank=True, null=True)
    QfaHelye2 = models.TextField(blank=True, null=True)
    MelyikHelyisegbeKerulHelyi = models.TextField(blank=True, null=True)
    ElektromosBekotes = models.TextField(blank=True, null=True)
    MilyenVentillatortTervezel = models.TextField(blank=True, null=True)
    MelyikHelyisegbeKerulKozpontiFalattoreses = models.TextField(blank=True, null=True)
    MelyikHelyisegbeKerulKozpontiMeglevoVentilatorHelyere = models.TextField(
        blank=True, null=True
    )
    MelyikHelyisegbeKerulKozpontiTuzfalonKivezetve = models.TextField(
        blank=True, null=True
    )
    MelyikHelyisegbeKerulKozpontiMennyezetre = models.TextField(blank=True, null=True)
    ElektromosBekotesKozponti = models.TextField(blank=True, null=True)
    MegjegyzesKozponti = models.TextField(blank=True, null=True)
    TipusdbVorticeMfo = models.TextField(blank=True, null=True)
    TipusdbAwentaKw100t = models.TextField(blank=True, null=True)
    TipusdbVents100 = models.TextField(blank=True, null=True)
    TipusdbSor6 = models.TextField(blank=True, null=True)
    MelyikHelyisegbeKerulMasodlagosFalattoreses = models.TextField(
        blank=True, null=True
    )
    MelyikHelyisegbeKerulMasodlagosMeglevoSzellozoHelyere = models.TextField(
        blank=True, null=True
    )
    MelyikHelyisegbeKerulMasodlagosMeglevoVentilator = models.TextField(
        blank=True, null=True
    )
    MelyikHelyisegbeKerulMasodlagosTetonKeresztulKivezetve = models.TextField(
        blank=True, null=True
    )
    MelyikHelyisegbeKerulMasodlagosTuzfalonKivezetve = models.TextField(
        blank=True, null=True
    )
    MelyikHelyisegbeKerulMasodlagosMennyezetre = models.TextField(blank=True, null=True)
    ElektromosBekotesMasodlagos = models.TextField(blank=True, null=True)
    MegjegyzesMasodlagos = models.TextField(blank=True, null=True)
    HelyeFurdoszoba = models.TextField(blank=True, null=True)
    HelyeKonyha = models.TextField(blank=True, null=True)
    HelyeWc = models.TextField(blank=True, null=True)
    HelyeMosokonyha = models.TextField(blank=True, null=True)
    HelyeKisebbFurdoszoba = models.TextField(blank=True, null=True)
    HelyeNagyobbFurdoszoba = models.TextField(blank=True, null=True)
    HelyeEmeletiFurdoszoba = models.TextField(blank=True, null=True)
    HelyeFoldszintiFurdoszoba = models.TextField(blank=True, null=True)
    Helye2Furdoszobaba = models.TextField(blank=True, null=True)
    Helye3Furdoszobaba = models.TextField(blank=True, null=True)
    EgyebMegjegyzesLegelvezeto = models.TextField(blank=True, null=True)
    D100Pvc = models.TextField(blank=True, null=True)
    D125Pvc = models.TextField(blank=True, null=True)
    D100Sono = models.TextField(blank=True, null=True)
    D125Sono = models.TextField(blank=True, null=True)
    Idomok90 = models.TextField(blank=True, null=True)
    Idomok45 = models.TextField(blank=True, null=True)
    IdomokToldo = models.TextField(blank=True, null=True)
    IdomokTIdom = models.TextField(blank=True, null=True)
    IdomokYIdom = models.TextField(blank=True, null=True)
    MegjegyzesCsovezes = models.TextField(blank=True, null=True)
    Emm716Db = models.TextField(blank=True, null=True)
    HolLeszAzEmm716 = models.TextField(blank=True, null=True)
    Emm916Db = models.TextField(blank=True, null=True)
    HolLeszAzEmm916 = models.TextField(blank=True, null=True)
    Ear201Db2 = models.TextField(blank=True, null=True)
    HolLeszAzEar201 = models.TextField(blank=True, null=True)
    Ear202GazosDb = models.TextField(blank=True, null=True)
    HolLeszAzEar202 = models.TextField(blank=True, null=True)
    AblakosLegbevezetokEmm716 = models.TextField(blank=True, null=True)
    AblakosLegbevezetokEmm916 = models.TextField(blank=True, null=True)
    AblakosLegbevezetokEar201 = models.TextField(blank=True, null=True)
    AblakosLegbevezetokEar202 = models.TextField(blank=True, null=True)
    Eth1853Db = models.TextField(blank=True, null=True)
    HolLeszAzEth1853 = models.TextField(blank=True, null=True)
    Eth1858GazosDb = models.TextField(blank=True, null=True)
    HolLeszAzEth1858Gazos = models.TextField(blank=True, null=True)
    EgyebKiegeszitokInfo = models.TextField(blank=True, null=True)
    AjtoszellozoDb = models.TextField(blank=True, null=True)
    AjtogyuruSzine = models.TextField(blank=True, null=True)
    MelyikAjtok3 = models.TextField(blank=True, null=True)
    SzellozoRacsKialakitasaDb = models.TextField(blank=True, null=True)
    SzellozoracsHelye2 = models.TextField(blank=True, null=True)
    TetoszellozoCserepTipusszin = models.TextField(blank=True, null=True)
    VisszaaramlasGatloDb1Db = models.TextField(blank=True, null=True)
    VisszaaramlasGatloDb2Db = models.TextField(blank=True, null=True)
    VisszaaramlasGatloDb3Db = models.TextField(blank=True, null=True)
    VisszaaramlasGatloHelye = models.TextField(blank=True, null=True)
    KeszitsdKepeketEsToltsdFelOket = models.TextField(blank=True, null=True)
    KeszitsVideotEsToltsdFel = models.TextField(blank=True, null=True)
    KeszitsSzovegesLeirastABeepitesselKapcsolatban = models.TextField(
        blank=True, null=True
    )
    GaranciaraVonatkozoMegjegyzes = models.TextField(blank=True, null=True)
    MelyikHelyisegbeKerulKozpontiMeglevoSzellozoHelyere = models.TextField(
        blank=True, null=True
    )
    MelyikHelyisegbeKerulKozpontiTetonKeresztulKivezetve = models.TextField(
        blank=True, null=True
    )
    Felmero2 = models.TextField(blank=True, null=True)
    DijbekeroPdf2 = models.TextField(blank=True, null=True)
    DijbekeroSzama2 = models.TextField(blank=True, null=True)
    DijbekeroMegjegyzes2 = models.TextField(blank=True, null=True)
    DijbekeroUzenetek = models.TextField(blank=True, null=True)
    FizetesiMod2 = models.TextField(blank=True, null=True)
    KiallitasDatuma = models.TextField(blank=True, null=True)
    FizetesiHatarido = models.TextField(blank=True, null=True)
    MennyireVoltMegelegedve2 = models.TextField(blank=True, null=True)
    Pontszam3 = models.TextField(blank=True, null=True)
    SzovegesErtekeles4 = models.TextField(blank=True, null=True)
    IngatlanKepe = models.TextField(blank=True, null=True)
    Munkalap = models.TextField(blank=True, null=True)
    BruttoFelmeresiDij = models.TextField(blank=True, null=True)
    MunkalapMegjegyzes = models.TextField(blank=True, null=True)
    FelmeresVisszaigazolva = models.TextField(blank=True, null=True)
    SzamlaPdf = models.TextField(blank=True, null=True)
    SzamlaSorszama2 = models.TextField(blank=True, null=True)
    KiallitasDatuma2 = models.TextField(blank=True, null=True)
    SzamlaUzenetek = models.TextField(blank=True, null=True)
    KerdesAzAjanlattalKapcsolatban = models.TextField(blank=True, null=True)
    AjanlatPdf = models.TextField(blank=True, null=True)
    SzamlaMegjegyzes = models.TextField(blank=True, null=True)
    FelmeresAdatok = models.TextField(blank=True, null=True)
    UtvonalAKozponttol = models.TextField(blank=True, null=True)
    StreetViewUrl = models.TextField(blank=True, null=True)
    Tipus = models.TextField(blank=True, null=True)
    RendelesSzama = models.TextField(blank=True, null=True)
    Munkalap2 = models.TextField(blank=True, null=True)
    Felmeresid = models.TextField(blank=True, null=True)
    FelmeresLink = models.TextField(blank=True, null=True)
    KiMerteFel2 = models.TextField(blank=True, null=True)
    FelmeresDatuma2 = models.TextField(blank=True, null=True)
    ClouderpMegrendeles = models.TextField(blank=True, null=True)
    Megye2 = models.TextField(blank=True, null=True)
    Utcakep = models.TextField(blank=True, null=True)
    IngatlanKepe2 = models.TextField(blank=True, null=True)
    FizetesiMod3 = models.TextField(blank=True, null=True)
    VentilatorTipusa = models.TextField(blank=True, null=True)
    KapcsolodoFelmeres = models.TextField(blank=True, null=True)
    ArajanlatMegjegyzes = models.TextField(blank=True, null=True)
    TervezettFelmresIdopont = models.TextField(blank=True, null=True)
    MiertMentunkKiFeleslegesen = models.BigIntegerField(blank=True, null=True)
    Hash = models.TextField(blank=True, null=True)
    NextAction = models.TextField(blank=True, null=True)
    NextActionUserId = models.TextField(blank=True, null=True)
    NextActionToDoType = models.TextField(blank=True, null=True)
    InternalUrl = models.TextField(blank=True, null=True)
    LastEvent = models.TextField(blank=True, null=True)
    StatusGroup = models.TextField(blank=True, null=True)
    VisszafizetesDatuma = models.TextField(blank=True, null=True)
    GaranciaTipusa = models.TextField(blank=True, null=True)
    KiepitesFeltetele = models.TextField(blank=True, null=True)
    KiepitesFeltetelLeirasa = models.TextField(blank=True, null=True)
    KiepitesFelteteleIgazolva = models.TextField(blank=True, null=True)
    DijbekeroSzama3 = models.IntegerField(blank=True, null=True)
    Iranyitoszam2 = models.TextField(blank=True, null=True)
    Telepules2 = models.TextField(blank=True, null=True)
    Cim3 = models.TextField(blank=True, null=True)
    BejelentesTipusa = models.TextField(blank=True, null=True)
    NettoFelmeresiDij = models.FloatField(blank=True, null=True)
    SzamlaMegjegyzes2 = models.TextField(blank=True, null=True)
    KarbantartasNettoDij = models.FloatField(blank=True, null=True)
    DijbekeroMegjegyzes3 = models.TextField(blank=True, null=True)
    Orszag2 = models.CharField(max_length=50, blank=True, null=True)
    BejelentesSzovege = models.TextField(blank=True, null=True)
    GaranciaFelmerestVegzi = models.CharField(max_length=50, blank=True, null=True)
    FelmeresDatuma3 = models.DateTimeField(blank=True, null=True)
    SzamlazasIngatlanCimre2 = models.CharField(max_length=100, blank=True, null=True)

    @property
    def StatusIdStr(self):
        if self.StatusId and self.StatusId in status_map.keys():
            return status_map[self.StatusId]
        return ""

    class Meta:
        managed = False
        db_table = "pen_minicrm_adatlapok"


class MiniCrmRequests(models.Model):
    time = models.DateTimeField(blank=True, null=True)
    endpoint = models.TextField(blank=True, null=True)
    script = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "minicrm_requests"


class Munkadij(models.Model):
    VALUE_TYPES = [("hour", "Óradíj"), ("fix", "Összeg")]
    type = models.CharField(max_length=255, blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    value_type = models.CharField(max_length=100, choices=VALUE_TYPES, default="hour")
    num_people = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_munkadij"


class FelmeresMunkadijak(models.Model):
    felmeres = models.ForeignKey("Felmeresek", models.CASCADE, blank=True, null=True)
    munkadij = models.ForeignKey("Munkadij", models.DO_NOTHING, blank=True, null=True)
    amount = models.IntegerField()
    value = models.FloatField()

    class Meta:
        managed = False
        db_table = "pen_felmeres_munkadijak"


class MiniCrmTodos(models.Model):
    projectid = models.IntegerField(db_column="ProjectId")  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "pen_minicrm_todos"


class Salesmen(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    zip = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = "pen_salesmen"


class Slots(models.Model):
    external_id = models.TextField()
    at = models.DateTimeField(blank=True, null=True)
    user: Salesmen = models.ForeignKey(
        "Salesmen", models.DO_NOTHING, blank=True, null=True
    )
    booked = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_slots"


class Settings(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_settings"


class ScriptRetries(models.Model):
    log = models.ForeignKey("Logs", models.DO_NOTHING, blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "script_retries"


class Routes(models.Model):
    origin_zip = models.CharField(max_length=50)
    dest_zip = models.CharField(max_length=50)
    distance = models.FloatField(blank=True, null=True)
    duration = models.FloatField()

    class Meta:
        managed = False
        db_table = "pen_routes"


class UserSkills(models.Model):
    skill = models.OneToOneField(
        "Skills", models.DO_NOTHING, primary_key=True
    )  # The composite primary key (skill_id, user_id) found, that is not supported. The first column is selected.
    user = models.ForeignKey("Salesmen", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "pen_user_skills"
        unique_together = (("skill", "user"),)


class Skills(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_skills"


class BestSlots(models.Model):
    slot: Slots = models.ForeignKey("Slots", models.CASCADE, blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_best_slots"


class SchedulerSettings(models.Model):
    name = models.TextField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_scheduler_settings"


class UnschedulableTimes(models.Model):
    reason = models.TextField(blank=True, null=True)
    user = models.ForeignKey("Salesmen", models.CASCADE, blank=True, null=True)
    from_field = models.DateTimeField(
        db_column="from", blank=True, null=True
    )  # Field renamed because it was a Python reserved word.
    to = models.DateTimeField(blank=True, null=True)
    repeat_time = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pen_unschedulable_times"
