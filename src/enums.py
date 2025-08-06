from enum import Enum


class UserRole(Enum):
    admin = "admin"
    manager = "manager"
    supervisor = "supervisor"


class ComputerType(Enum):
    workstation = "workstation"
    server = "server"
