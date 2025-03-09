# pylint: disable=missing-function-docstring,missing-module-docstring
import io
import re

def convert_to_seconds(timestamp):
    if timestamp == '':
        return 0
    secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(timestamp.split('.'))))
    return secs


def parse_line(line):
    try:
        url = parse_url_from_line(line)
        end_timestamp = re.match(".*till ([0-9]{1,2}.[0-9]{1,2})", line)
        if end_timestamp is None:
            end_timestamp = 0
        else:
            end_timestamp = convert_end_timestamp_to_seconds(end_timestamp)
        return url, end_timestamp
    except Exception as e:
        print(e)
        return  "",0

def convert_end_timestamp_to_seconds(end_timestamp):
    end_timestamp = end_timestamp.group(1)
    end_timestamp = convert_to_seconds(end_timestamp)
    return end_timestamp

def parse_url_from_line(line):
    url = re.match("(https?://[^\s]+)", line).group(0)
    url = re.sub("&list=.*", "", url)
    return url


def read_email():
    email_content = []
    print("Paste the email below:")
    try:
        while True:
            line = input()
            email_content.append(line)
    except KeyboardInterrupt:
        pass

    return email_content


def print_found_urls(urls, logger):
    logger.info(f"1. Found the following URIs, {len(urls)} in total:")
    for i in urls:
        logger.info(i)


def parse_all_email_lines(email_content):
    urls = []
    for line in email_content:
        with io.open('email.txt', 'a', encoding='utf-8') as f:
            f.write(line + "\n")
        url, end_timestamp = parse_line(line)
        if url != '':
            urls.append((url, end_timestamp))
    return urls


def find_urls_in_email(email_content, logger):
    urls = parse_all_email_lines(email_content)
    #urls = list(filter(None, urls))
    for url in urls:
        logger.info("Downloading %s", url)
    return urls


def get_urls_in_email(logger):
    email_content = read_email()
    urls = find_urls_in_email(email_content, logger)
    print_found_urls(urls, logger)
    return urls
