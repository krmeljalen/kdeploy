from kubernetes import client, config
from kubernetes.client.rest import ApiException

import kdeploy.helper as helper


class kkubernetes:
    def __init__(self, manifest):
        config.load_kube_config()
        self.client = client.CoreV1Api()

    def verify_docker_repo_label(self, label):
        label_selector = f"label={label}"
        try:
            # List all secrets in all namespaces with the given label selector
            secrets = self.client.list_secret_for_all_namespaces(
                label_selector=label_selector
            )

            # Check if any secrets match the label selector
            if secrets.items:
                for secret in secrets.items:
                    print(
                        f"Secret Name: {secret.metadata.name}, Namespace: {secret.metadata.namespace} found."
                    )
            else:
                helper.error(
                    f"No secret found with label '{label_selector}' on kubernetes cluster."
                )

        except ApiException as e:
            helper.error(
                f"Exception when calling CoreV1Api->list_secret_for_all_namespaces: {e}"
            )
