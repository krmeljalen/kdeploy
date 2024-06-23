import os
import docker
import kdeploy.helper as helper


class kdocker:
    def __init__(self):
        self.client = docker.from_env()

    def build_docker_image(self, image_tag, dockerfile_path="./Dockerfile"):
        # Ensure the Dockerfile path is valid
        if not os.path.exists(dockerfile_path):
            helper.error(f"Dockerfile path {dockerfile_path} does not exist.")

        # Build the image
        try:
            print("Building Docker image...")
            image, build_logs = self.client.images.build(
                path=os.path.dirname(dockerfile_path),
                tag=image_tag,
                dockerfile=os.path.basename(dockerfile_path),
            )
            for log in build_logs:
                if "stream" in log:
                    print(log["stream"].strip())
            print(f"Successfully built image {image_tag}")
        except docker.errors.BuildError as err:
            helper.error(f"Error occurred while building image: {err}")
        except docker.errors.APIError as err:
            helper.error(f"Error occurred with the Docker API: {err}")

    def push_docker_image(self, image_tag):
        # Push the image
        try:
            print(f"Pushing Docker image {image_tag} to repository...")
            push_logs = self.client.images.push(image_tag, stream=True, decode=True)
            for log in push_logs:
                if "error" in log:
                    helper.error(f"Error: {log['error']}")
            print(f"Successfully pushed image {image_tag}")
        except docker.errors.APIError as err:
            helper.error(f"Error occurred while pushing image: {err}")
