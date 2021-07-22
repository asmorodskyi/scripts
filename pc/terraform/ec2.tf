variable "region" {
    default = "us-east-1"
}

provider "aws" {
    region = var.region
}

variable "instance_count" {
    default = "1"
}

variable "type" {
    default = "t2.large"
}

variable "image_id" {
    default = "ami-016e32e9cd1b095f4"
}

resource "random_id" "service" {
    count = var.instance_count
    keepers = {
        name = "asm"
    }
    byte_length = 8
}

resource "aws_key_pair" "asm-keypair" {
    key_name   = "asm-${element(random_id.service.*.hex, 0)}"
    public_key = file("/home/asmorodskyi/.ssh/id_rsa.pub")
}

resource "aws_security_group" "asm_sg" {
    name        = "asm-${element(random_id.service.*.hex, 0)}"

    ingress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["213.151.95.130/32", "195.135.220.0/22", "195.250.132.144/29"]
    }

    egress {
        from_port       = 0
        to_port         = 0
        protocol        = "-1"
        cidr_blocks     = ["0.0.0.0/0"]
    }

    tags = {
            openqa_created_date = timestamp()
            openqa_created_id = element(random_id.service.*.hex, 0)
        }
}

resource "aws_instance" "asm-test" {
    count           = var.instance_count
    ami             = var.image_id
    instance_type   = var.type
    key_name        = aws_key_pair.asm-keypair.key_name
    security_groups = [aws_security_group.asm_sg.name]

    tags = {
            openqa_created_date = timestamp()
            openqa_created_id = element(random_id.service.*.hex, count.index)
            openqa_ttl = "8640300"
            }
}

output "public_ip" {
    value = aws_instance.asm-test.*.public_ip
}
