# ***************** Universidad de los Andes ***********************
# ****** Departamento de Ingeniería de Sistemas y Computación ******
# ********** Arquitectura y diseño de Software - ISIS2503 **********
#
# Infraestructura de Microservicios
#
# Elementos a desplegar en AWS:
# 1. Grupos de seguridad:
#    - msd-traffic-api (puerto 8080)
#    - msd-traffic-apps (puerto 8080)
#    - msd-traffic-mongodb (puerto 27017)
#    - msd-traffic-db (puerto 5432)
#    - cbd-traffic-ssh (puerto 22)
#
# 2. Instancias EC2:
#    - msd-productos-db (PostgreSQL instalado y configurado)
#    - msd-pedidos-db (PostgreSQL instalado y configurado)
#    - msd-usuarios-db (PostgreSQL instalado y configurado)
#    - msd-productos-ms (Servicio de productos descargado)
#    - msd-pedidos-ms (Servicio de pedidos instalado y configurado)
#    - msd-usuarios-ms (Servicio de usuarios instalado y configurado)
#    - msd-kong (Kong API Gateway instalado y configurado)
# ******************************************************************

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.18.0"
    }
  }
}

# Variable. Define la región de AWS donde se desplegará la infraestructura.
variable "region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

# Variable. Define el prefijo usado para nombrar los recursos en AWS.
variable "project_prefix" {
  description = "Prefix used for naming AWS resources"
  type        = string
  default     = "msd"
}

# Variable. Define el tipo de instancia EC2 a usar para las máquinas virtuales.
variable "instance_type" {
  description = "EC2 instance type for application hosts"
  type        = string
  default     = "t3.micro"
}

# Proveedor. Define el proveedor de infraestructura (AWS) y la región.
provider "aws" {
  region = var.region
}

# Variables locales usadas en la configuración de Terraform.
locals {
  project_name = "${var.project_prefix}-microservices"
  repository   = "https://github.com/ISIS2503-202520-S2-G7-ctrlz/WMSProvesi.git"

  common_tags = {
    Project   = local.project_name
    ManagedBy = "Terraform"
  }
}

# Data Source. Busca la AMI más reciente de Ubuntu 24.04 usando los filtros especificados.
data "aws_ami" "ubuntu" {
    most_recent = true
    owners      = ["099720109477"]

    filter {
        name   = "name"
        values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
    }

    filter {
        name   = "virtualization-type"
        values = ["hvm"]
    }
}

# Recurso. Define el grupo de seguridad para el tráfico del API gateway (8000).
resource "aws_security_group" "traffic_api" {
    name        = "${var.project_prefix}-traffic-api"
    description = "Allow application traffic on port 8000"

    ingress {
        description = "HTTP access for gateway layer"
        from_port   = 8000
        to_port     = 8000
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = merge(local.common_tags, {
        Name = "${var.project_prefix}-traffic-api"
    })
}

# Recurso. Define el grupo de seguridad para el tráfico de los microservicios (8080).
resource "aws_security_group" "traffic_apps" {
    name        = "${var.project_prefix}-traffic-apps"
    description = "Allow application traffic on port 8080"

    ingress {
        description = "HTTP access for service layer"
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = merge(local.common_tags, {
        Name = "${var.project_prefix}-traffic-apps"
    })
}

# Recurso. Define el grupo de seguridad para el tráfico de las bases de datos (5432).
resource "aws_security_group" "traffic_db" {
  name        = "${var.project_prefix}-traffic-db"
  description = "Allow PostgreSQL access"

  ingress {
    description = "Traffic from anywhere to DB"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-traffic-db"
  })
}

# Recurso. Define el grupo de seguridad para el tráfico SSH (22) y permite todo el tráfico saliente.
resource "aws_security_group" "traffic_ssh" {
  name        = "${var.project_prefix}-traffic-ssh"
  description = "Allow SSH access"

  ingress {
    description = "SSH access from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-traffic-ssh"
  })
}

# Recurso. Define el grupo de seguridad para el tráfico de MongoDB.
resource "aws_security_group" "traffic_mongodb" {
    name        = "${var.project_prefix}-traffic-mongodb"
    description = "Allow application traffic on port 27017"

    ingress {
        description = "MongoDB access for database layer"
        from_port   = 27017
        to_port     = 27017
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = merge(local.common_tags, {
        Name = "${var.project_prefix}-traffic-mongodb"
    })
}

# Recurso. Define la instancia EC2 para la base de datos PostgreSQL de productos.
# Esta instancia incluye un script de creación para instalar y configurar PostgreSQL.
# El script crea un usuario y una base de datos, y ajusta la configuración para permitir conexiones remotas.
resource "aws_instance" "productos_db" {
  ami                         = "ami-051685736c7b35f95"
  instance_type               = var.instance_type
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.traffic_db.id, aws_security_group.traffic_ssh.id]

  user_data = <<-EOT
              #!/bin/bash

              docker run --restart=always -d -e POSTGRES_USER=provesi_user -e POSTGRES_DB=productos_db -e POSTGRES_PASSWORD=isis2503 -p 5432:5432 --name productos-db postgres
              EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-productos-db"
    Role = "productos-db"
  })
}

# Recurso. Define la instancia EC2 para la base de datos PostgreSQL de pedidos.
# Esta instancia incluye un script de creación para instalar y configurar PostgreSQL.
# El script crea un usuario y una base de datos, y ajusta la configuración para permitir conexiones remotas.
resource "aws_instance" "pedidos_db" {
  ami                         = "ami-051685736c7b35f95"
  instance_type               = var.instance_type
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.traffic_db.id, aws_security_group.traffic_ssh.id]

  user_data = <<-EOT
              #!/bin/bash

              docker run --restart=always -d -e POSTGRES_USER=provesi_user -e POSTGRES_DB=pedidos_db -e POSTGRES_PASSWORD=isis2503 -p 5432:5432 --name pedidos-db postgres
              EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-pedidos-db"
    Role = "pedidos-db"
  })
}

# Recurso. Define la instancia EC2 para el microservicio de productos (Django).
# Esta instancia incluye un script de creación para instalar el servicio de productos.
resource "aws_instance" "productos_ms" {
  ami                         = "ami-051685736c7b35f95"
  instance_type               = var.instance_type
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.traffic_apps.id, aws_security_group.traffic_ssh.id]

  user_data = <<-EOT
              #!/bin/bash

              sudo dnf install nano git -y

              mkdir -p /labs
              cd /labs

              if [ ! -d WMSProvesi ]; then
                git clone ${local.repository}
              fi

              cd WMSProvesi/productos
              sudo sed -i "s/<PRODUCTOS_DB_HOST>/${aws_instance.productos_db.private_ip}/g" Dockerfile
              EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-productos-ms"
    Role = "productos-ms"
  })

  depends_on = [aws_instance.productos_db]
}

# Recurso. Define la instancia EC2 para el microservicio de Pedidos (Django).
# Esta instancia incluye un script de creación para instalar el microservicio de Pedidos y aplicar las migraciones.
resource "aws_instance" "pedidos_ms" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.traffic_apps.id, aws_security_group.traffic_ssh.id]

  user_data = <<-EOT
              #!/bin/bash

              export PEDIDOS_DB_HOST=${aws_instance.pedidos_db.private_ip}
              echo "PEDIDOS_DB_HOST=${aws_instance.pedidos_db.private_ip}" | sudo tee -a /etc/environment

              export PRODUCTOS_HOST=${aws_instance.productos_ms.private_ip}
              echo "PRODUCTOS_HOST=${aws_instance.productos_ms.private_ip}" | sudo tee -a /etc/environment

              sudo apt-get update -y
              sudo apt-get install -y python3-pip git build-essential libpq-dev python3-dev

              mkdir -p /labs
              cd /labs

              if [ ! -d WMSProvesi ]; then
                git clone ${local.repository}
              fi
              
              cd WMSProvesi/pedidos

              sudo pip3 install --upgrade pip --break-system-packages
              sudo pip3 install -r requirements.txt --break-system-packages

              sudo python3 manage.py makemigrations
              sudo python3 manage.py migrate
              EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-pedidos-ms"
    Role = "pedidos-ms"
  })

  depends_on = [aws_instance.pedidos_db, aws_instance.productos_ms]
}

# Recurso. Define la instancia EC2 para Kong (API Gateway).
resource "aws_instance" "kong" {
  ami                         = "ami-051685736c7b35f95"
  instance_type               = var.instance_type
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.traffic_api.id, aws_security_group.traffic_ssh.id]

  user_data = <<-EOT
              #!/bin/bash

              sudo export PRODUCTOS_HOST=${aws_instance.productos_ms.private_ip}
              echo "PRODUCTOS_HOST=${aws_instance.productos_ms.private_ip}" | sudo tee -a /etc/environment
              sudo export PEDIDOS_HOST=${aws_instance.pedidos_ms.private_ip}
              echo "PEDIDOS_HOST=${aws_instance.pedidos_ms.private_ip}" | sudo tee -a /etc/environment


              sudo dnf install nano git -y
              sudo mkdir /labs
              cd /labs
              sudo git clone https://github.com/ISIS2503-202520-S2-G7-ctrlz/WMSProvesi.git
              cd WMSProvesi

              # Configurar el archivo kong.yaml con las IPs de los microservicios

              sudo sed -i "s/<PRODUCTOS_HOST>/${aws_instance.productos_ms.private_ip}/g" kong.yaml
              sudo sed -i "s/<PEDIDOS_HOST>/${aws_instance.pedidos_ms.private_ip}/g" kong.yaml
              docker network create kong-net
              docker run -d --name kong --network=kong-net --restart=always \
              -v "$(pwd):/kong/declarative/" -e "KONG_DATABASE=off" \
              -e "KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yaml" \
              -p 8000:8000 kong/kong-gateway
              EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-kong"
    Role = "api-gateway"
  })

  depends_on = [aws_instance.productos_ms, aws_instance.pedidos_ms]
}

# Salida. Muestra la dirección IP pública de la instancia de Kong (API Gateway).
output "kong_public_ip" {
  description = "Public IP address for the Kong API Gateway instance"
  value       = aws_instance.kong.public_ip
}

# Salida. Muestra las direcciones IP públicas de la instancia de Productos MS.
output "productos_ms_public_ip" {
  description = "Public IP address for the Productos Microservice instance"
  value       = aws_instance.productos_ms.public_ip
}

# Salida. Muestra las direcciones IP públicas de la instancia de Pedidos MS.
output "pedidos_ms_public_ip" {
  description = "Public IP address for the Pedidos Microservice instance"
  value       = aws_instance.pedidos_ms.public_ip
}

# Salida. Muestra las direcciones IP privadas de la instancia de la base de datos de Productos.
output "productos_db_private_ip" {
  description = "Private IP address for the Productos Database instance"
  value       = aws_instance.productos_db.private_ip
}

# Salida. Muestra las direcciones IP privadas de la instancia de la base de datos de Pedidos.
output "pedidos_db_private_ip" {   
  description = "Private IP address for the Pedidos Database instance"
  value       = aws_instance.pedidos_db.private_ip
}