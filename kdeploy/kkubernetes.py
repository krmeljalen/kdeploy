import yaml
from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException

import kdeploy.helper as helper


class kkubernetes:
    def __init__(self):
        config.load_kube_config()
        self.client = client.CoreV1Api()
        self.batch_client = client.BatchV1Api()
        self.apps_client = client.AppsV1Api()
        self.api_client = client.ApiClient()

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

    def deploy_cronjob(self, manifest, namespace="default"):
        app_name = manifest["app_name"]
        docker_repo_label = manifest["docker_repo_label"]
        image_tag = helper.generate_image_tag(manifest)
        cronjob_schedule = manifest["kubernetes"]["schedule"]

        print(f"Deploying Cronjob {app_name}")

        cronjob_manifest = client.V1beta1CronJob(
            api_version="batch/v1",
            kind="CronJob",
            metadata=client.V1ObjectMeta(name=app_name),
            spec=client.V1beta1CronJobSpec(
                schedule=cronjob_schedule,
                job_template=client.V1beta1JobTemplateSpec(
                    spec=client.V1JobSpec(
                        template=client.V1PodTemplateSpec(
                            spec=client.V1PodSpec(
                                image_pull_secrets=[
                                    client.V1LocalObjectReference(
                                        name=docker_repo_label
                                    )
                                ],
                                containers=[
                                    client.V1Container(name=app_name, image=image_tag)
                                ],
                                restart_policy="Never",
                            )
                        )
                    )
                ),
                successful_jobs_history_limit=1,
                failed_jobs_history_limit=1,
            ),
        )

        try:
            self.batch_client.create_namespaced_cron_job(
                namespace=namespace, body=cronjob_manifest
            )
        except ApiException as e:
            helper.error(f"Exception when creating CronJob: {e}")

        print(f"CronJob '{app_name}' created successfully.")

    def deploy_deployment(self, manifest, namespace="default"):
        app_name = manifest["app_name"]
        docker_repo_label = manifest["docker_repo_label"]
        image_tag = helper.generate_image_tag(manifest)

        print(f"Deploying Deployment {app_name}")

        # Define the Deployment manifest
        deployment_manifest = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(
                name=app_name, labels={"app.kubernetes.io/name": app_name}
            ),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(
                    match_labels={"app.kubernetes.io/name": app_name}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app.kubernetes.io/name": app_name}
                    ),
                    spec=client.V1PodSpec(
                        containers=[client.V1Container(name=app_name, image=image_tag)],
                        image_pull_secrets=[
                            client.V1LocalObjectReference(name=docker_repo_label)
                        ],
                    ),
                ),
            ),
        )

        try:
            # Create the Deployment in the default namespace
            self.apps_client.create_namespaced_deployment(
                namespace=namespace, body=deployment_manifest
            )
        except ApiException as e:
            helper.error(f"Exception when creating Deployment: {e}")

        print(f"Deployment '{app_name}' created successfully.")

    def deploy_service(self, manifest, namespace="default"):
        if "ports" not in manifest["kubernetes"].keys():
            return

        app_name = manifest["app_name"]

        service_ports = []
        number = 1
        for port_pair in manifest["kubernetes"]["ports"]:
            for sport, dport in port_pair.items():
                service_ports.append(
                    client.V1ServicePort(
                        name=f"svcport{number}",
                        port=sport,
                        protocol="TCP",
                        target_port=dport,
                    )
                )
                number += 1

        service_manifest = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(
                name="obweb", labels={"app.kubernetes.io/name": app_name}
            ),
            spec=client.V1ServiceSpec(
                selector={"app.kubernetes.io/name": app_name}, ports=service_ports
            ),
        )
        try:
            self.client.create_namespaced_service(
                namespace=namespace, body=service_manifest
            )
        except ApiException as e:
            helper.error(f"Exception when creating Service: {e}")

        print(f"Service '{app_name}' created successfully.")

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

    def custom_deploy(self, manifest, namespace="default"):
        app_name = manifest["app_name"]
        kubernetes_path = manifest["kubernetes"]["path"]

        try:
            utils.create_from_yaml(
                self.api_client, kubernetes_path, namespace=namespace
            )
        except Exception as e:
            helper.error(
                f"Failed deploying {app_name} from {kubernetes_path} in namespace {namespace} Error: {e}"
            )

        print(
            f"Application '{app_name}' from {kubernetes_path} deployed in namespace {namespace}."
        )
