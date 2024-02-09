import argparse

from movie_sites.filmaffinity import filmaffinity
from movie_sites.iafd import iafd
from movie_sites.imdb import imdb

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Movies (IMDB/Filmaffinity) scraping script."
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run the script in headless mode.",
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        required=True,
        help="URL to be searched.",
    )
    parser.add_argument(
        "-f",
        "--folder",
        type=str,
        default="./sumarios",
        help="Destination folder for the generated file.",
    )
    args = parser.parse_args()

    if "imdb.com" in args.url:
        imdb(args.headless, args.url, args.folder)
    elif "filmaffinity.com" in args.url:
        filmaffinity(args.headless, args.url, args.folder)
    elif "iafd.com" in args.url:
        iafd(args.headless, args.url, args.folder)
    else:
        print("The movie site provided is not supported.")
        exit(1)
