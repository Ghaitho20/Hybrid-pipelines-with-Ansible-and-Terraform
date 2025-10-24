variable "azure_subscription_id" {
  default = "8686b74f-045d-478a-8a33-7f755e36eecf"
}

variable "azure_tenant_id" {
  default = "0b3f3971-44be-4993-bc74-d7486d2490d2"
}

variable "azure_client_id" {
  default = "ab184b92-0195-437b-965b-0c4f7c3a4c9b"
}

# Remove the secret from the file
variable "azure_client_secret" {
  default = ""  
}


variable "vm_size" {
  default = "Standard_B1s"
}

variable "admin_username" {
  default = "azureuser"
}

variable "ssh_public_key" {
   default = "~/.ssh/id_rsa.pub"  
}
