variable "azure_subscription_id" {
  type        = string
  description = "Azure subscription ID"
}

variable "azure_tenant_id" {
  type        = string
  description = "Azure tenant ID"
}

variable "azure_client_id" {
  type        = string
  description = "Azure client ID"
}

variable "azure_client_secret" {
  type        = string
  description = "Azure client secret"
  sensitive   = true
}


variable "vm_size" {
  default = "Standard_B1s"
}

variable "admin_username" {
  default = "azureuser"
}

//this var will be injected in the pipeline as credentials 

variable "ssh_public_key" {
    description = "The public SSH key to access the VM"
    type        = string
   //default = file("~/.ssh/id_rsa.pub")  (only for testing locally )
}
