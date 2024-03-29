variable "cred_file" {
    default = "/home/asmorodskyi/gce_credentials.json"
}

provider "google" {
    credentials = var.cred_file
    project     = var.project
}

data "external" "gce_cred" {
    program = [ "cat", var.cred_file ]
    query =  { }
}

variable "instance_count" {
    default = "1"
}

variable "name" {
    default = "openqa-vm"
}

variable "type" {
    default = "n1-standard-2"
}

variable "region" {
    default = "europe-west1-b"
}

variable "image_id" {
    default = ""
}

variable "project" {
    default = "suse-sle-qa"
}

variable "extra-disk-size" {
    default = "1000"
}

variable "extra-disk-type" {
    default = "pd-ssd"
}

variable "create-extra-disk" {
    default=false
}

variable "uefi" {
    default=false
}

resource "random_id" "service" {
    count = var.instance_count
    keepers = {
        name = var.name
    }
    byte_length = 8
}

resource "google_compute_instance" "openqa" {
    count        = var.instance_count
    name         = "${var.name}-${element(random_id.service.*.hex, count.index)}"
    machine_type = var.type
    zone         = var.region

    boot_disk {
        device_name = "${var.name}-${element(random_id.service.*.hex, count.index)}"
        initialize_params {
            image = var.image_id
        }
    }

    metadata = {
            sshKeys = "susetest:${file("/home/asmorodskyi/.ssh/id_rsa.pub")}"
            openqa_created_by = var.name
            openqa_created_date = "${timestamp()}"
            openqa_created_id = "${element(random_id.service.*.hex, count.index)}"
            openqa_ttl = "8640300"
        }

    network_interface {
        network = "default"
            access_config {
        }
    }

    service_account {
        email = data.external.gce_cred.result["client_email"]
        scopes = ["cloud-platform"]
    }

    dynamic "shielded_instance_config" {
        for_each = var.uefi ? [ "UEFI" ] : []
        content {
            enable_secure_boot = "true"
            enable_vtpm = "true"
            enable_integrity_monitoring = "true"
        }
    }
}

resource "google_compute_attached_disk" "default" {
    count    =  var.create-extra-disk ? var.instance_count: 0
    disk     = element(google_compute_disk.default.*.self_link, count.index)
    instance = element(google_compute_instance.openqa.*.self_link, count.index)
}

resource "google_compute_disk" "default" {
    name                      = "ssd-disk-${element(random_id.service.*.hex, count.index)}"
    count                     = var.create-extra-disk ? var.instance_count : 0
    type                      = var.extra-disk-type
    zone                      = var.region
    size                      = var.extra-disk-size
    physical_block_size_bytes = 4096
    labels = {
        openqa_created_by = var.name
        openqa_created_id = "${element(random_id.service.*.hex, count.index)}"
    }
}

output "public_ip" {
    value = "${google_compute_instance.openqa.*.network_interface.0.access_config.0.nat_ip}"
}

output "vm_name" {
    value = "${google_compute_instance.openqa.*.name}"
}
