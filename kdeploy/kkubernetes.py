from kubernetes import client, config
from kubernetes.client.rest import ApiException

import kdeploy.helper as helper


class kkubernetes:
    def __init__(self):
        config.load_kube_config()
        self.client = client.CoreV1Api()

    def verify_docker_repo_label(self, secret_name, namespace="default"):
        try:
            self.client.read_namespaced_secret(secret_name, namespace)
            print(
                f"Kubernetes docker repo secret '{secret_name}' found in namespace '{namespace}'"
            )
        except ApiException as e:
            if e.status == 404:
                helper.error(
                    f"Kubernetes docker repo secret '{secret_name}' does not exist in namespace '{namespace}'"
                )
            else:
                helper.error(f"An error occurred: {e}")

    def deploy_pod(self, manifest, namespace="default"):
        app_name = manifest["app_name"]
        docker_repo_label = manifest["docker_repo_label"]
        image_tag = helper.generate_image_tag(manifest)

        print(f"Deploying Pod {app_name}")

        pod_manifest = client.V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=client.V1ObjectMeta(
                name=app_name, labels={"app.kubernetes.io/name": app_name}
            ),
            spec=client.V1PodSpec(
                restart_policy="Always",
                image_pull_secrets=[
                    client.V1LocalObjectReference(name=docker_repo_label)
                ],
                containers=[client.V1Container(name=app_name, image=image_tag)],
            ),
        )

        try:
            self.client.create_namespaced_pod(namespace=namespace, body=pod_manifest)
        except ApiException as e:
            helper.error(f"Failed to deploy Pod {app_name} Error: {e}")

        print(f"Pod {app_name} successfully deployed in namespace '{namespace}'")

    def deploy_deployment(self, manifest, namespace="default"):
        print(f"Deploying Deployment {manifest['app_name']}")
        pass

    def deploy_cronjob(self, manifest, namespace="default"):
        print(f"Deploying Cronjob {manifest['app_name']}")
        schedule = manifest["kubernetes"]["schedule"]
        pass

    def deploy_service(self, manifest, namespace="default"):
        if "ports" not in manifest["kubernetes"].keys():
            return

        app_name = manifest["app_name"]

        service_ports = []
        number = 1
        for port_pair in manifest["kubernetes"]["ports"]:
            for sport, dport in port_pair.items():
                service_ports.append(client.V1ServicePort(
                        name=f"svcport{number}",
                        port=sport,
                        protocol="TCP",
                        target_port=dport
                    ))
                number += 1

        service_manifest = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(
                name="obweb",
                labels={"app.kubernetes.io/name": app_name}
            ),
            spec=client.V1ServiceSpec(
                selector={"app.kubernetes.io/name": app_name},
                ports=service_ports
            )
        )
        try:
            self.client.create_namespaced_service(namespace=namespace, body=service_manifest)
            print(f"Service '{app_name}' created successfully.")
        except ApiException as e:
            print(f"Exception when creating Service: {e}")

    def deploy(self, manifest):
        kind = manifest["kubernetes"]["kind"]

        if kind == "CronJob":
            self.deploy_cronjob(manifest)
            return
        if kind == "Pod":
            self.deploy_pod(manifest)
            self.deploy_service(manifest)
            return
        if kind == "Deployment":
            self.deploy_deployment(manifest)
            self.deploy_service(manifest)
            return