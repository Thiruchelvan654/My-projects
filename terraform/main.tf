terraform {
  required_providers {
    kind = {
      source = "tehcyx/kind"
    }
  }
}

provider "kind" {}

resource "kind_cluster" "calico_lab" {
  name = "tf-lab"

  # Calico isn't installed yet, so the node can't become Ready.
  # Waiting for Ready here would hang, so we leave it off.
  wait_for_ready = false

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    networking {
      disable_default_cni = true
    }

    node {
      role = "control-plane"

      extra_port_mappings {
        container_port = 32432
        host_port      = 32432
        protocol       = "TCP"
      }
    }
  }
}

output "kubeconfig_path" {
  value = kind_cluster.calico_lab.kubeconfig_path
}
