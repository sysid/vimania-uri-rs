import logging


log = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(format="%(name)s [%(levelname)s] %(message)s", level=logging.DEBUG)
    import vimania_uri_rs  # must be after logging setup

    log.info("Hello, World!")
    # print(vimania_uri_rs.reverse_line("Hello, Thomas!"))
    title = vimania_uri_rs.get_url_title("https://www.google.com")
    print(title)
