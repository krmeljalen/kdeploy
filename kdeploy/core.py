import kdeploy.kdocker as kdocker
import kdeploy.helper as helper


def run():
    mode = helper.parse_arguments()
    manifest = helper.process_manifest()

    # Deploy mode
    if mode == "deploy":
        app_name = manifest["app_name"]
        app_version = manifest["app_version"]
        docker_repo = manifest["docker_repo"]
        image_tag = f"{docker_repo}/{app_name}:{app_version}"

        # Process docker image
        kdocker_client = kdocker.kdocker(manifest)
        kdocker_client.build_docker_image(image_tag)
        kdocker_client.push_docker_image(image_tag)


if __name__ == "__main__":
    run()
