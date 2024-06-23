import sys
import yaml
import argparse


def error(msg):
    print(f"Error: {msg}")
    sys.exit(1)


def process_manifest():
    try:
        with open("manifest.yaml", "r") as file:
            manifest_data = yaml.safe_load(file)
    except FileNotFoundError:
        error("manifest.yaml not found")
    except:
        error("manifest.yaml could not be parsed")

    # Verify basic keys
    for key in [
        "docker_repo",
        "docker_secret_label",
        "app_name",
        "app_version",
        "kubernetes",
    ]:
        if key not in manifest_data.keys():
            error(f"missing '{key}' in manifest.yaml")

    # Verify mandatory kubernetes needed keys
    if "kind" not in manifest_data["kubernetes"].keys():
        error(f"missing mandatory '{key}' in 'kubernetes' dict in manifest.yaml")

    if manifest_data["kubernetes"]["kind"] not in ["Deployment", "Pod", "CronJob"]:
        error(f"wrong kubernetes 'kind' specified in manifest.yaml")

    # Verify kubernetes cronjob keys
    if manifest_data["kubernetes"]["kind"] == "CronJob":
        if "schedule" not in manifest_data["kubernetes"]:
            error(f"missing 'schedule' for kubernetes CronJob kind in manifest.yaml")

    return manifest_data


def parse_arguments():
    parser = argparse.ArgumentParser(description="Kdeploy - Kubernetes deploy tool")
    parser.add_argument("-d", action="store_true", help="Destroy app deployment")

    # Parse the arguments
    args = parser.parse_args()

    # Check if the -d flag is present
    if args.d:
        return "destroy"
    else:
        return "deploy"
