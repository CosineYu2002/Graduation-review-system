from urllib.parse import urljoin, urlencode
from bs4 import BeautifulSoup, Tag, ResultSet
import requests
import re


class CourseCrawler:
    def __init__(
        self,
        department: str,
        course_name: list[str],
        dept_root_url: str = "https://class-qry.acad.ncku.edu.tw/crm/course_map/department.php?",
        course_root_url: str = "https://class-qry.acad.ncku.edu.tw/crm/course_map/",
    ):
        self.department = department
        self.dept_root_url = dept_root_url
        self.course_root_url = course_root_url
        self.course_name = course_name
        params = {"dept": department}
        self.base_url = self.dept_root_url + urlencode(params)
        self.init_session()

    def init_session(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
                "Referer": "https://class-qry.acad.ncku.edu.tw/",
            }
        )

    def fetch_course_links(self) -> dict[str, list[str]]:
        resp = self.session.get(self.base_url)
        soup = BeautifulSoup(resp.text, "lxml")
        table = soup.find("table", class_="departmentCourseTable")
        assert isinstance(table, Tag), "Table not found or is not a Tag"
        links = {course: [] for course in self.course_name}

        course_name_set = set(self.course_name)
        for a in table.find_all("a"):
            assert isinstance(a, Tag), "Link is not a Tag"
            name = a.text.strip()
            name = re.sub(r"\[\w+\]", "", name)  # Remove course code in brackets
            href = a.get("href")
            if not href:
                continue

            for course in course_name_set:
                if course == name:
                    full_url = urljoin(self.course_root_url, href)  # type: ignore
                    if full_url not in links[course]:
                        links[course].append(full_url)

        return links

    def fetch_course_page(
        self, links: dict[str, list[str]]
    ) -> list[dict[str, int | list[str] | str]]:
        results = []
        for name, url_list in links.items():
            if len(url_list) == 0:
                results.append({"name": name, "credits": 0.0, "course_codes": []})
                continue

            result = {"name": name, "credits": 0.0, "course_codes": []}
            for url in url_list:
                resp = self.session.get(url)
                soup = BeautifulSoup(resp.text, "lxml")
                table = soup.find("table", class_="courseTable")
                assert isinstance(table, Tag), "Course table not found or is not a Tag"
                rows: ResultSet = table.find_all("tr")

                if len(rows) <= 1:
                    continue

                for row in rows[1:]:
                    cells = row.find_all("td")
                    if len(cells) < 5:
                        continue

                    course_code = cells[0].text.strip()
                    credits_str = cells[3].text.strip()
                    try:
                        credits = float(credits_str)
                    except ValueError:
                        raise ValueError(f"Invalid credits value: {credits_str}")

                    result["credits"] = credits
                    result["course_codes"].append(course_code)
                    break
            results.append(result)

        return results

    def run(self) -> list[dict[str, int | list[str] | str]]:
        course_links = self.fetch_course_links()
        return self.fetch_course_page(course_links)


if __name__ == "__main__":
    course_list = [
        "電路學（一）",
        "不存在",
        "電機概論實驗",
    ]

    crawler = CourseCrawler("E2", course_list)
    result = crawler.run()
    print(result)
