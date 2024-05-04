from .search_request import SearchRequest
import requests
from bs4 import BeautifulSoup

MIRROR_SOURCES = ["GET", "Cloudflare", "IPFS.io", "Infura"]
base_url = "http://library.lol{}"


class LibgenSearch:
    def search_title(self, query):
        search_request = SearchRequest(query, search_type="title")
        return search_request.aggregate_request_data()

    def search_author(self, query):
        search_request = SearchRequest(query, search_type="author")
        return search_request.aggregate_request_data()

    def search(self, query, search_type="title"):
        """
            return a list of result that include image url and download link
        """
        if search_type == "title":
            data = self.search_title(query)
        elif search_type == "author":
            data = self.search_author(query)
        else:
            raise ValueError("Invalid search_type : use title or author instead")

        result = []
        for item in data:
            item['description'] = resolve_description(item)
            item.update({"Mirror_1": resolve_download_and_image_link(item)})
            result.append(item)
        return result


def search_title_filtered(self, query, filters, exact_match=True):
    search_request = SearchRequest(query, search_type="title")
    results = search_request.aggregate_request_data()
    filtered_results = filter_results(
        results=results, filters=filters, exact_match=exact_match
    )
    return filtered_results


def search_author_filtered(self, query, filters, exact_match=True):
    search_request = SearchRequest(query, search_type="author")
    results = search_request.aggregate_request_data()
    filtered_results = filter_results(
        results=results, filters=filters, exact_match=exact_match
    )
    return filtered_results


def resolve_download_links(self, item):
    mirror_1 = item["Mirror_1"]
    page = requests.get(mirror_1)
    soup = BeautifulSoup(page.text, "html.parser")
    links = soup.find_all("a", string=MIRROR_SOURCES)
    download_links = {link.string: link["href"] for link in links}
    return download_links


def filter_results(results, filters, exact_match):
    """
    Returns a list of results that match the given filter criteria.
    When exact_match = true, we only include results that exactly match
    the filters (ie. the filters are an exact subset of the result).

    When exact-match = false,
    we run a case-insensitive check between each filter field and each result.

    exact_match defaults to TRUE -
    this is to maintain consistency with older versions of this library.
    """

    filtered_list = []
    if exact_match:
        for result in results:
            # check whether a candidate result matches the given filters
            if filters.items() <= result.items():
                filtered_list.append(result)

    else:
        filter_matches_result = False
        for result in results:
            for field, query in filters.items():
                if query.casefold() in result[field].casefold():
                    filter_matches_result = True
                else:
                    filter_matches_result = False
                    break
            if filter_matches_result:
                filtered_list.append(result)
    return filtered_list


def resolve_download_and_image_link(item):
    mirror_1 = item["Mirror_1"]
    page = requests.get(mirror_1)
    soup = BeautifulSoup(page.text, "html.parser")
    link = soup.find("a", string=['GET'])
    image_src = soup.find("img")['src']
    result = {link.string: link["href"], 'image_url': base_url.format(image_src)}
    return result


def resolve_description(item):
    mirror_1 = item["Mirror_1"]
    page = requests.get(mirror_1)
    soup = BeautifulSoup(page.text, "html.parser")
    tags = soup.find_all('div')
    for tag in tags:
        if "Description:" in tag.getText():
            return tag.getText()
