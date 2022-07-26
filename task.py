import json
import requests


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


print("==>Testing cosign tool:==>")
username = input('Please Enter your Docker user:')
password = input("Please Enter your Docker Password:")
repo = input("Please Enter The public Docker Hub repository name:")


def authenticate_docker_user():
    login_url = f"https://hub.docker.com/v2/users/login"
    repo_url = f"https://hub.docker.com/v2/repositories/{username}/{repo}/"
    print("==>Logging into Your DockerHub Account")
    tok_req = requests.post(login_url, json={"username": username, "password": password})
    token = tok_req.json()["token"]
    headers = {"Authorization": f"JWT {token}"}
    print(f"==> Sending PATCH request to {repo_url}")
    payload = {"full_description": "TEST"}
    patch_req = requests.patch(repo_url, headers=headers, json=payload)

    return headers
# Get login token and create authorization header


headers = authenticate_docker_user()


def print_tags_list():
    print("print all tags in that repository")
# The program will enumerate and print all tags in that repository(2)
    response = requests.get(f'https://registry.hub.docker.com/v2/repositories/{username}/{repo}/tags', headers=headers)
    response_tags = json.loads(response.text)
    list_of_tags = []
    for tag in response_tags["results"]:
        tag_name = tag["name"]
        list_of_tags.append(tag_name)
    print(list_of_tags)


def get_token():
    response = requests.get(f'https://auth.docker.io/token?grant_type=password&username={username}&service'
                            f'=registry.docker.io&client_id=dockerized&scope=repository:{username}/{repo}'
                            f':pull&password=abc12345')
# jprint(response.json())
    response_dict = json.loads(response.text)
    auth_token = response_dict['access_token']
    return auth_token


# Verify cosign signature{"Critical":{"Identity":{"docker-reference":""},"Image":{"Docker-manifest-digest","Type"}


def check_for_signature(tag):
    auth_token = get_token()
    hed = {'Authorization': 'Bearer ' + auth_token}
    response = requests.get(f'https://registry.hub.docker.com/v2/{username}/{repo}/manifests/{tag}', headers=hed)
    print(f">> print the manifest of the {tag}")
    jprint(response.json())
    response_dict = json.loads(response.text)
    if "Critical" in response_dict:
        if "Type" in response_dict["Critical"]:
            print("That repository image has a cosign signature!!")
        else:
            print("That repository doesn't have a cosign signature")
    else:
        print("That repository doesn't have a cosign signature")


def print_tags_info():
    response = requests.get(f'https://registry.hub.docker.com/v2/repositories/{username}/{repo}/tags', headers=headers)
    response_tags = json.loads(response.text)
    for tag in response_tags["results"]:
        tag_name = tag["name"]
        check_for_signature(tag_name)


if __name__ == "__main__":
    print_tags_list()
    print_tags_info()
