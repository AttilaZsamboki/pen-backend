class OrdersRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "orders":
            return "orders_db"
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "orders":
            return "orders_db"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == "orders" or obj2._meta.app_label == "orders":
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "orders":
            return db == "orders_db"
        return db == "default"
