# terraform {
#   backend "azurerm" {
#     resource_group_name  = "rg-cicd-tfstate"
#     storage_account_name = "stcicdtfstate"   
#     container_name       = "tfstate"
#     key                  = "cicd/terraform.tfstate"
#   }
# }
