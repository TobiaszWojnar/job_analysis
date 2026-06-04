from bs4 import BeautifulSoup
import re
from .base_strategy import BaseJobStrategy
from .strategy_helper import (
    get_text_helper,
    get_salary_type_helper,
    get_salary_helper,
    get_years_of_experience_helper,
)
from ...utils.category_utils import get_category_helper
from ..llm.llm_scraper import (
    get_responsibilities_with_llm,
    get_requirements_with_llm,
    get_benefits_with_llm,
    get_location_type_with_llm,
)


class JustJoinItStrategy(BaseJobStrategy):
    def get_title(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup.find("h1"))

    def get_company(self, soup: BeautifulSoup) -> str:
        company_h2 = soup.find("h2")
        if company_h2:
            return get_text_helper(company_h2)
        return ""

    def get_company_link(self, soup: BeautifulSoup) -> str:
        company_profile_link = soup.find(
            "a", string=re.compile("Company profile", re.IGNORECASE)
        )
        if company_profile_link:
            return company_profile_link.get("href")
        return ""

    def get_company_description(self, soup: BeautifulSoup) -> str:
        about_the_company_header = soup.find(
            "h3", string=re.compile("About the company", re.IGNORECASE)
        )
        if about_the_company_header and about_the_company_header.find_parent("div"):
            return get_text_helper(
                about_the_company_header.find_parent("div").find("div")
            )
        who_we_are_header = soup.find(
            "strong", string=re.compile("Who we are:", re.IGNORECASE)
        )
        if who_we_are_header and who_we_are_header.find_parent():
            return get_text_helper(
                who_we_are_header.find_parent().find_next_sibling("p")
            )
        return ""

    def get_category(self, soup: BeautifulSoup) -> str:
        breadcrumbs = soup.find("nav")
        category = get_category_helper(
            self.get_title(soup),
            self.get_tech_stack(soup),
            self.get_full_offer(soup),
            get_text_helper(breadcrumbs),
        )
        return category

    def get_tech_stack(self, soup: BeautifulSoup) -> str:
        # Find all h4 tags that are siblings or nested in a stack with specific MUI classes
        # or follow the "Tech stack" heading.
        tech_tags = soup.find_all(
            "h4", class_=re.compile("mui-1i3ah26|mui-pc1kzi", re.IGNORECASE)
        )
        if not tech_tags:
            # Try finding by section
            header = soup.find(string=re.compile("Tech stack", re.IGNORECASE))
            if header and header.find_parent("div"):
                tech_tags = header.find_parent("div").find_all("h4")

        stack = []
        for tag in tech_tags:
            text = get_text_helper(tag).strip()
            if text:
                # Remove extra newlines/spaces within the text
                text = " ".join(text.split())
                stack.append(text)

        return ", ".join(stack) if stack else ""

    def get_location(self, soup: BeautifulSoup) -> str:
        # Find all paths that match the location pin icon
        location_icons = soup.find_all(
            "path", d=re.compile(r"^M12 2C16\.2 2 20 5\.22", re.IGNORECASE)
        )  # Pin icon
        for icon in location_icons:
            container = icon.find_parent("div")
            if container:
                text = get_text_helper(container)
                # Clean up ZWSP and check if it looks like a valid location (has comma or city name)
                text = text.replace("\u200b", "").replace("\xa0", " ")
                if text and "," in text:
                    return text
        return ""

    def get_location_type(self, soup: BeautifulSoup) -> str:
        text = soup.get_text().lower()
        return get_location_type_with_llm(text)

    def get_salary(self, soup: BeautifulSoup) -> str:
        salary_node = soup.find(
            "span", string=re.compile("Salary", re.IGNORECASE)
        )
        if salary_node: 
            salary_section = salary_node.find_parent("div")
            return get_salary_helper(salary_section)
        return ''

    def get_salary_type(self, soup: BeautifulSoup) -> str:
        salary_node = soup.find(
            "span", string=re.compile("Salary", re.IGNORECASE)
        )
        if salary_node: 
            salary_section = salary_node.find_parent("div")
            return get_salary_type_helper(salary_section)
        return ''

    def get_years_of_experience(self, soup: BeautifulSoup) -> str:
        return get_years_of_experience_helper(soup)

    def get_responsibilities(self, soup: BeautifulSoup) -> str:
        page_text = soup.get_text(separator=" ", strip=True)
        return get_responsibilities_with_llm(page_text)

    def get_requirements(self, soup: BeautifulSoup) -> str:
        page_text = soup.get_text(separator=" ", strip=True)
        return get_requirements_with_llm(page_text)

    def get_benefits(self, soup: BeautifulSoup) -> str:
        page_text = soup.get_text(separator=" ", strip=True)
        return get_benefits_with_llm(page_text)

    def get_full_offer(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup)
