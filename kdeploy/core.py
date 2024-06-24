import kdeploy.helper as helper
import kdeploy.kdocker as kdocker
import kdeploy.kkubernetes as kkubernetes


def run():
    mode = helper.parse_arguments()
    manifest = helper.process_manifest()

    # Deploy mode
    if mode == "deploy":
        # Set vars
        image_tag = helper.generate_image_tag(manifest)

        # Process docker image
        kdocker_client = kdocker.kdocker()
        kdocker_client.build_docker_image(image_tag)
        kdocker_client.push_docker_image(image_tag)

        # Initiate kubernetes deploy
        kkubernetes_client = kkubernetes.kkubernetes()

        # If we dont have custom kubernetes file, use predefined
        if "path" not in manifest["kubernetes"].keys():
            docker_repo_label = manifest["docker_repo_label"]
            kkubernetes_client.verify_docker_repo_label(docker_repo_label)
            kkubernetes_client.deploy(manifest)
        else:
            kkubernetes_client.custom_deploy(manifest)

    # Destroy mode
    if mode == "destroy":
        app_name = manifest["app_name"]
        # Needs work


if __name__ == "__main__":
    run()
