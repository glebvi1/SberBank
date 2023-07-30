from rolepermissions.roles import AbstractUserRole


class SimpleUser(AbstractUserRole):
    available_permissions = {
        "SimpleUser": True,
    }


class SystemAdmin(AbstractUserRole):
    available_permissions = {
        "SystemAdmin": True,
    }


class BannedUser(AbstractUserRole):
    available_permissions = {
        "BannedUser": True,
    }


class VIPUser(AbstractUserRole):
    available_permissions = {
        "VIPUser": True,
    }
