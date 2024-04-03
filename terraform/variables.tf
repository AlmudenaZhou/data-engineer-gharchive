variable "project_id" {
  type        = string
  description = "The name of the project"
  default     = "capstone-project-417800"
}

variable "location" {
  type = string
  description = "The default location"
  default = "US"
}

variable "region" {
  type        = string
  description = "The default compute region"
  default     = "us-west2"
}

variable "zone" {
  type        = string
  description = "The default compute zone"
  default     = "us-west2-a"
}

variable "bucket_name" {
  type = string
  description = "datalake unique name"
  default = "gharchive_capstone_project"
}


variable "bq_dataset_name" {
  type = string
  description = "big query dataset name"
  default = "gharchive_capstone_project"
}


variable "credentials" {
  description = "Path to the keyfile containing GCP credentials."
  type        = string
  default     = "./secrets.json"
}


