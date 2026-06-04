class P:
    """Permission codes. Add new ones here, assign to roles in the migration seed."""

    # users
    USERS_READ = "users.read"
    USERS_CREATE = "users.create"
    USERS_UPDATE = "users.update"
    USERS_DELETE = "users.delete"

    # roles
    ROLES_READ = "roles.read"
    ROLES_ASSIGN = "roles.assign"

    # products
    PRODUCTS_READ = "products.read"
    PRODUCTS_CREATE = "products.create"
    PRODUCTS_UPDATE = "products.update"
    PRODUCTS_DELETE = "products.delete"

    # orders  (own = only yours, all = everyone's)
    ORDERS_READ_OWN = "orders.read.own"
    ORDERS_READ_ALL = "orders.read.all"
    ORDERS_UPDATE_OWN = "orders.update.own"
    ORDERS_UPDATE_ALL = "orders.update.all"
