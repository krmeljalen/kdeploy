from kubernetes import client, config
from kubernetes.client.rest import ApiException

import kdeploy.helper as helper


class kkubernetes:
    def __init__(self):
        config.load_kube_config()
        self.client = client.CoreV1Api()

    def verify_docker_repo_label(self, secret_name, namespace="default"):
        try:
            # Try to read the secret
            self.client.read_namespaced_secret(secret_name, namespace)
            print(f"Kubernetes docker repo secret '{secret_name}' found.")
        except ApiException as e:
            if e.status == 404:
                helper.error(
                    f"Kubernetes docker repo secret '{secret_name}' does not exist in namespace '{namespace}'."
                )
            else:
                helper.error(f"An error occurred: {e}")

    def deploy_pod(self, manifest):
        print(f"Deploying Pod {manifest['app_name']}")
        pass

    def deploy_deployment(self, manifest):
        print(f"Deploying Deployment {manifest['app_name']}")
        pass

    def deploy_cronjob(self, manifest):
        print(f"Deploying Cronjob {manifest['app_name']}")
        schedule = manifest["kubernetes"]["schedule"]
        pass

    def deploy(self, manifest):
        kind = manifest["kubernetes"]["kind"]

        if kind == "Pod":
            self.deploy_pod(manifest)
        if kind == "Deployment":
            self.deploy_deployment(manifest)
        if kind == "CronJob":
            self.deploy_cronjob(manifest)
