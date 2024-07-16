import pytest
from libgen_api.libgen_search import LibgenSearch

title = "Pride and Prejudice"
author = "Agatha Christie"

ls = LibgenSearch()


class TestBasicSearching:
    def test_title_search(self):
        titles = ls.search_title(title)
        first_result = titles[0]

        assert title in first_result["Title"]

    def test_author_search(self):
        titles = ls.search_author(author)
        first_result = titles[0]

        assert author in first_result["Author"]


    def test_title_filtering(self):
        title_filters = {"Year": "2007", "Extension": "epub"}
        titles = ls.search_title_filtered(title, title_filters, exact_match=True)
        first_result = titles[0]

        assert (title in first_result["Title"]) & fields_match(
            title_filters, first_result
        )

    def test_author_filtering(self):
        author_filters = {"Language": "German", "Year": "2009"}
        titles = ls.search_author_filtered(author, author_filters, exact_match=True)
        first_result = titles[0]

        assert (author in first_result["Author"]) & fields_match(
            author_filters, first_result
        )

    def test_search(self):
        titles = ls.search(author, search_type="author")
        first_result = titles[0]

        assert author in first_result["Author"]

    def test_filtered_search(self):
        author_filters = {"Language": "German", "Year": "2009"}
        titles = ls.search_filtered(author, author_filters, search_type="author")
        first_result = titles[0]

        assert (author in first_result["Author"]) & fields_match(
            author_filters, first_result
        )
    
    # explicit test of exact filtering
    # should return no results as they will all get filtered out
    def test_exact_filtering(self):
        exact_filters = {"Extension": "PDF"}
        # if exact_match = True, this will filter out all results as
        # "pdf" is always written lower case on Library Genesis
        titles = ls.search_author_filtered(author, exact_filters, exact_match=True)

        assert len(titles) == 0

    def test_non_exact_filtering(self):
        non_exact_filters = {"Extension": "PDF"}
        titles = ls.search_author_filtered(author, non_exact_filters, exact_match=False)
        first_result = titles[0]

        assert (author in first_result["Author"]) & fields_match(
            non_exact_filters, first_result, exact=False
        )

    def test_non_exact_partial_filtering(self):
        partial_filters = {"Extension": "p", "Year": "200"}
        titles = ls.search_title_filtered(title, partial_filters, exact_match=False)
        first_result = titles[0]

        assert (title in first_result["Title"]) & fields_match(
            partial_filters, first_result, exact=False
        )

    def test_exact_partial_filtering(self):
        exact_partial_filters = {"Extension": "p"}
        titles = ls.search_title_filtered(
            title, exact_partial_filters, exact_match=True
        )

        assert len(titles) == 0

    def test_resolve_download_links(self):
        titles = ls.search_author(author)
        title_to_download = titles[0]
        dl_links = ls.resolve_download_links(title_to_download)

        # ensure each host is in the results and that they each have a url
        assert (["GET", "Cloudflare", "IPFS.io"] == list(dl_links.keys())) & (
            False not in [len(link) > 0 for key, link in dl_links.items()]
        )

    # should return an error if search query is less than 3 characters long
    def test_raise_error_on_short_search(self):
        with pytest.raises(Exception):
            titles = ls.search_title(title[0:2])

####################
# Helper Functions #
####################

# Check object fields for equality -
# -> Returns True if they match.
# -> Returns False otherwise.
#
# when exact-True, fields are checked strictly (==).
#
# when exact=False, fields are normalized to lower case,
# and checked whether filter value is a subset of the response.
def fields_match(filter_obj, response_obj, exact=True):
    for key, value in filter_obj.items():

        if exact is False:
            value = value.lower()
            response_obj[key] = response_obj[key].lower()
            if value not in response_obj[key]:
                return False

        elif response_obj[key] != value:
            return False
    return True
