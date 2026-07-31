from pathlib import Path

TF = Path("docs/07-infrastructure-as-code-and-configuration-management/terraform-practical-walkthrough.md")
ANSIBLE = Path("docs/07-infrastructure-as-code-and-configuration-management/ansible-practical-walkthrough.md")

tf = TF.read_text(encoding="utf-8")

old_validation = '''  validation {
    condition = alltrue([
      for subnet in values(var.private_subnets) :
      can(cidrnetmask(subnet.cidr_block))
    ])
    error_message = "Every private subnet must use a valid IPv4 CIDR."
  }
}'''
new_validation = '''  validation {
    condition = alltrue([
      for subnet in values(var.private_subnets) :
      can(cidrnetmask(subnet.cidr_block))
    ])
    error_message = "Every private subnet must use a valid IPv4 CIDR."
  }

  validation {
    condition     = length(var.private_subnets) >= 2
    error_message = "At least two private subnets are required."
  }
}'''
if old_validation not in tf:
    raise SystemExit("Terraform private_subnets validation block not found")
tf = tf.replace(old_validation, new_validation, 1)

old_precondition = '''
  lifecycle {
    precondition {
      condition     = length(var.private_subnets) >= 2
      error_message = "The network requires at least two private subnets."
    }
  }
'''
if old_precondition not in tf:
    raise SystemExit("Terraform VPC lifecycle precondition block not found")
tf = tf.replace(old_precondition, "\n", 1)

old_expect = '  expect_failures = [module.network.aws_vpc.this]'
new_expect = '  expect_failures = [var.private_subnets]'
if old_expect not in tf:
    raise SystemExit("Terraform expect_failures target not found")
tf = tf.replace(old_expect, new_expect, 1)

TF.write_text(tf, encoding="utf-8", newline="\n")

ansible = ANSIBLE.read_text(encoding="utf-8")
replacements = {
'''        url: >-
          {{ payments_health_scheme }}://{{ payments_health_host }}:
          {{ payments_port }}{{ payments_health_path }}''':
'''        url: "{{ payments_health_scheme }}://{{ payments_health_host }}:{{ payments_port }}{{ payments_health_path }}"''',
'''        url: >-
          {{ payments_health_scheme }}://{{ payments_health_host }}:
          {{ payments_port }}{{ payments_version_path }}''':
'''        url: "{{ payments_health_scheme }}://{{ payments_health_host }}:{{ payments_port }}{{ payments_version_path }}"''',
'''    url: >-
      {{ payments_health_scheme }}://{{ payments_health_host }}:
      {{ payments_port }}{{ payments_version_path }}''':
'''    url: "{{ payments_health_scheme }}://{{ payments_health_host }}:{{ payments_port }}{{ payments_version_path }}"''',
}
for old, new in replacements.items():
    if old not in ansible:
        raise SystemExit(f"Ansible URL block not found: {old!r}")
    ansible = ansible.replace(old, new, 1)

ANSIBLE.write_text(ansible, encoding="utf-8", newline="\n")
