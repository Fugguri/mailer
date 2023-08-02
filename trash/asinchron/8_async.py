import asyncio
import requests
url = "https://loremflickr.com/320/240"


def get_file(url):
    r = requests.get(url, allow_redirects=True)
    return r


def write_file(responce):
    filename = responce.url.split("/")
    with open(filename, "wb") as file:
        file.write(responce.content)


def main():
    pass


if __name__ == "__main__":
    main()
