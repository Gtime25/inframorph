# Demo Azure Infrastructure with Security and Cost Issues
# This file is intentionally created with issues for testing InfraMorph

# Resource Group
resource "azurerm_resource_group" "demo_rg" {
  name     = "demo-resource-group"
  location = "East US"
}

# Virtual Network
resource "azurerm_virtual_network" "demo_vnet" {
  name                = "demo-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.demo_rg.location
  resource_group_name = azurerm_resource_group.demo_rg.name
}

# Subnet
resource "azurerm_subnet" "demo_subnet" {
  name                 = "demo-subnet"
  resource_group_name  = azurerm_resource_group.demo_rg.name
  virtual_network_name = azurerm_virtual_network.demo_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Network Security Group with Security Issues
resource "azurerm_network_security_group" "demo_nsg" {
  name                = "demo-nsg"
  location            = azurerm_resource_group.demo_rg.location
  resource_group_name = azurerm_resource_group.demo_rg.name

  # SECURITY ISSUE: Open SSH access from anywhere
  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"  # SECURITY ISSUE: Open to all IPs
    destination_address_prefix = "*"
  }

  # SECURITY ISSUE: Open HTTP access from anywhere
  security_rule {
    name                       = "HTTP"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"  # SECURITY ISSUE: Open to all IPs
    destination_address_prefix = "*"
  }

  # SECURITY ISSUE: Open HTTPS access from anywhere
  security_rule {
    name                       = "HTTPS"
    priority                   = 1003
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"  # SECURITY ISSUE: Open to all IPs
    destination_address_prefix = "*"
  }
}

# Virtual Machine with Cost Issues
resource "azurerm_virtual_machine" "demo_vm" {
  name                  = "demo-vm"
  location              = azurerm_resource_group.demo_rg.location
  resource_group_name   = azurerm_resource_group.demo_rg.name
  network_interface_ids = [azurerm_network_interface.demo_nic.id]
  vm_size               = "Standard_D4s_v3"  # COST ISSUE: Over-provisioned for demo

  # SECURITY ISSUE: No encryption specified
  storage_os_disk {
    name              = "demo-osdisk"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"  # COST ISSUE: Not using premium storage
    disk_size_gb      = 100  # COST ISSUE: Large disk for demo
  }

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  os_profile {
    computer_name  = "demo-vm"
    admin_username = "admin"
    admin_password = "Password123!"  # SECURITY ISSUE: Hardcoded password
  }

  os_profile_linux_config {
    disable_password_authentication = false  # SECURITY ISSUE: Password authentication enabled
  }

  tags = {
    Environment = "demo"
  }
}

# Network Interface
resource "azurerm_network_interface" "demo_nic" {
  name                = "demo-nic"
  location            = azurerm_resource_group.demo_rg.location
  resource_group_name = azurerm_resource_group.demo_rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.demo_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.demo_pip.id
  }
}

# Public IP
resource "azurerm_public_ip" "demo_pip" {
  name                = "demo-pip"
  location            = azurerm_resource_group.demo_rg.location
  resource_group_name = azurerm_resource_group.demo_rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

# Storage Account with Security Issues
resource "azurerm_storage_account" "demo_storage" {
  name                     = "demostorage12345"  # NAMING ISSUE: Generic name
  resource_group_name      = azurerm_resource_group.demo_rg.name
  location                 = azurerm_resource_group.demo_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # SECURITY ISSUE: Public access enabled
  allow_blob_public_access = true  # SECURITY ISSUE: Public blob access

  # SECURITY ISSUE: No encryption specified
  # encryption {
  #   services {
  #     blob {
  #       enabled = true
  #     }
  #   }
  # }

  tags = {
    Environment = "demo"
  }
}

# SQL Server with Security Issues
resource "azurerm_sql_server" "demo_sql" {
  name                         = "demo-sql-server"
  resource_group_name          = azurerm_resource_group.demo_rg.name
  location                     = azurerm_resource_group.demo_rg.location
  version                      = "12.0"
  administrator_login          = "admin"
  administrator_login_password = "Password123!"  # SECURITY ISSUE: Hardcoded password

  # SECURITY ISSUE: Public access enabled
  public_network_access_enabled = true  # SECURITY ISSUE: Public network access

  tags = {
    Environment = "demo"
  }
}

# SQL Database
resource "azurerm_sql_database" "demo_db" {
  name                = "demo-database"
  resource_group_name = azurerm_resource_group.demo_rg.name
  location            = azurerm_resource_group.demo_rg.location
  server_name         = azurerm_sql_server.demo_sql.name

  # COST ISSUE: Using expensive tier
  edition = "Standard"  # COST ISSUE: Could use Basic for demo
  requested_service_objective_name = "S1"  # COST ISSUE: Over-provisioned

  # SECURITY ISSUE: No encryption specified
  # transparent_data_encryption_enabled = true

  tags = {
    Environment = "demo"
  }
}

# App Service Plan with Cost Issues
resource "azurerm_app_service_plan" "demo_plan" {
  name                = "demo-app-plan"
  location            = azurerm_resource_group.demo_rg.location
  resource_group_name = azurerm_resource_group.demo_rg.name
  kind                = "Linux"
  reserved            = true

  # COST ISSUE: Using expensive tier
  sku {
    tier = "Standard"  # COST ISSUE: Could use Basic for demo
    size = "S1"        # COST ISSUE: Over-provisioned
  }

  tags = {
    Environment = "demo"
  }
}

# Web App
resource "azurerm_app_service" "demo_app" {
  name                = "demo-web-app"
  location            = azurerm_resource_group.demo_rg.location
  resource_group_name = azurerm_resource_group.demo_rg.name
  app_service_plan_id = azurerm_app_service_plan.demo_plan.id

  # SECURITY ISSUE: No HTTPS enforcement
  https_only = false  # SECURITY ISSUE: HTTP allowed

  site_config {
    linux_fx_version = "NODE|14-lts"
  }

  tags = {
    Environment = "demo"
  }
} 