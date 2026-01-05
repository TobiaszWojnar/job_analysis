from bs4 import BeautifulSoup
import re
from .base_strategy import BaseJobStrategy
from .strategy_helper import get_category_helper, get_salary_type_helper, get_text_helper, get_years_of_experience_helper, get_salary_helper

class ProtocolStrategy(BaseJobStrategy):
    def get_title(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup.find('h1', attrs={'data-test': 'text-offerTitle'}))

    def get_company(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup.find('h2', attrs={'data-test': 'text-offerEmployer'}), ['Firma: ', 'Company: '])

    def get_company_link(self, soup: BeautifulSoup) -> str:
        # data-test="anchor-company-link"
        link = soup.find('h2', attrs={'data-test': 'text-offerEmployer'}).find('a')
        if link:
            return "https://theprotocol.it"+link.get('href')
        return ""

    def get_company_description(self, soup: BeautifulSoup) -> str:
        about_us_section = soup.find(id="ABOUT_US")
        about_us_description = get_text_helper(about_us_section, ['O nas', 'This is how we work']) if about_us_section else ""

        work_section = soup.find(attrs={"data-test":"section-work-organization"})
        work_description = get_text_helper(work_section) if work_section else ""
        
        return about_us_description + "\n" + work_description

    def get_category(self, soup: BeautifulSoup) -> str:
        return get_category_helper(self.get_title(soup), self.get_tech_stack(soup))

    def get_tech_stack(self, soup: BeautifulSoup) -> str:
        technologies = soup.find(id="REQUIREMENTS").find_all('span')
        return ", ".join([get_text_helper(tech) for tech in technologies])

    def get_location(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup.find(attrs={'data-test':'text-primaryLocation'}))

    def get_location_type(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup.find(attrs={'data-test':'content-workModes'}))

    def get_salary(self, soup: BeautifulSoup) -> str:
        return get_salary_helper(soup.find(attrs={'data-test':'section-contracts'}))

    def get_salary_type(self, soup: BeautifulSoup) -> str:
        salary_section = soup.find(attrs={'data-test':'section-contracts'})
        salary_types = get_salary_type_helper(salary_section)
        if salary_types:
            return salary_types

        contracts_types = soup.find_all(attrs={'data-test':'text-contractName'})
        
        return ', '.join([get_text_helper(contract) for contract in contracts_types])

    def get_years_of_experience(self, soup: BeautifulSoup) -> str:
        return get_years_of_experience_helper(soup)

    def get_responsibilities(self, soup: BeautifulSoup) -> str:
        responsibilities_section = soup.find(attrs={'data-test': 'section-responsibilities'})
        responsibilities = responsibilities_section.find_all('li')
        if responsibilities:
            return ", ".join([get_text_helper(responsibility) for responsibility in responsibilities])
        responsibilities = responsibilities_section.find_all('div')
        return ", ".join([get_text_helper(responsibility) for responsibility in responsibilities])

    def get_requirements(self, soup: BeautifulSoup) -> str:
        requirements = soup.find(attrs={'data-test': 'section-requirements'}).find_all('li')
        if requirements:
            return ", ".join([get_text_helper(requirement) for requirement in requirements])
        return ""

    def get_benefits(self, soup: BeautifulSoup) -> str:
        benefits_section = soup.find(attrs={"data-test":"PROGRESS_AND_BENEFITS"})
        benefits = benefits_section.find_all('li')
        if benefits:
            return ", ".join([get_text_helper(benefit) for benefit in benefits])
        return get_text_helper(benefits_section)

    def get_full_offer(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup.find(id="offerHeader").parent)
