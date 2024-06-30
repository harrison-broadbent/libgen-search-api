import requests
from bs4 import BeautifulSoup

# WHY
# The SearchRequest module contains all the internal logic for the library.
#
# This encapsulates the logic,
# ensuring users can work at a higher level of abstraction.

# USAGE
# req = search_request.SearchRequest("[QUERY]", search_type="[title]")


class SearchRequest:

    col_names = [
        "ID",
        "Author",
        "Title",
        "Publisher",
        "Year",
        "Pages",
        "Language",
        "Size",
        "Extension",
        "Mirror_1",
        "Mirror_2",
        "Mirror_3",
        "Mirror_4",
        "Mirror_5",
        "Edit",
    ]

    def __init__(self, query, search_type="title"):
        self.query = query
        self.search_type = search_type

        if len(self.query) < 3:
            raise Exception("Query is too short")

    def strip_i_tag_from_soup(self, soup):
        subheadings = soup.find_all("i")
        for subheading in subheadings:
            subheading.decompose()

    def get_search_page(self):
        query_parsed = "%20".join(self.query.split(" "))
        if self.search_type.lower() == "title":
            search_url = (
                f"https://libgen.is/search.php?req={query_parsed}&column=title"
            )
        elif self.search_type.lower() == "author":
            search_url = (
                f"https://libgen.is/search.php?req={query_parsed}&column=author"
            )
        search_page = requests.get(search_url)
        return search_page, search_url
    
    def get_next_page(self, url):  # collecting information tables from results pages
        soup = BeautifulSoup(requests.get(url).text, "lxml")
        self.strip_i_tag_from_soup(soup)
        table = soup.find_all("table")[2]
        return table


    def aggregate_request_data(self):
        search_page, search_url = self.get_search_page()
        soup = BeautifulSoup(search_page.text, "lxml")
        self.strip_i_tag_from_soup(soup)

        # number of results pages 
        page_count = int(soup.find_all("table")[1].find_next("font").text.split()[0]) // 25

        # Libgen results contain 3 tables
        # Table2: Table of data to scrape.
        # get_next_pages() collects these tables to information_tables
        info_tables = [soup.find_all("table")[2]]
        if page_count > 1:
            [info_tables.append(self.get_next_page(f"{search_url}&page={i + 2}")) for i in range(page_count)]

        # Determines whether the link url (for the mirror)
        # or link text (for the title) should be preserved.
        # Both the book title and mirror links have a "title" attribute,
        # but only the mirror links have it filled.(title vs title="libgen.io")

        # iterating through tables and rows and appending raw data
        raw_data = []  
        for table in info_tables:
            for row in table.find_all("tr")[1:]:
                raw_data.append([
                        td.a["href"]
                        if td.find("a")
                        and td.find("a").has_attr("title")
                        and td.find("a")["title"] != ""
                        else "".join(td.stripped_strings) for td in row.find_all("td")]
                    )

        output_data = [dict(zip(self.col_names, row)) for row in raw_data]
        return output_data
