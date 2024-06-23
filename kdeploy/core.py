import kdeploy.helper as helper
import kdeploy.kdocker as kdocker
import kdeploy.kkubernetes as kkubernetes


def run():
    mode = helper.parse_arguments()
    manifest = helper.process_manifest()

    # Deploy mode
    if mode == "deploy":
        # Set vars
        app_name = manifest["app_name"]
        app_version = manifest["app_version"]
        docker_repo = manifest["docker_repo"]
        docker_repo_label = manifest["docker_repo_label"]

        image_tag = f"{docker_repo}/{app_name}:{app_version}"

        # Process docker image
        kdocker_client = kdocker.kdocker()
        kdocker_client.build_docker_image(image_tag)
        kdocker_client.push_docker_image(image_tag)

        # Initiate kubernetes deploy
        kkubernetes_client = kkubernetes.kkubernetes()
        kkubernetes_client.verify_docker_repo_label(docker_repo_label)
        kkubernetes_client.deploy(manifest)

    # Destroy mode
    if mode == "destroy":
        app_name = manifest["app_name"]


if __name__ == "__main__":
    run()
