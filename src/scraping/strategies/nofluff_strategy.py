from bs4 import BeautifulSoup
import re
from .base_strategy import BaseJobStrategy
from .strategy_helper import get_category_helper, get_text_helper, get_salary_type_helper, get_salary_helper, get_years_of_experience_helper

class NoFluffStrategy(BaseJobStrategy):
    def get_title(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup.find('h1'))

    def get_company(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup.find(id="postingCompanyUrl"))

    def get_company_link(self, soup: BeautifulSoup) -> str:
        link = soup.find(id="postingCompanyUrl").get('href')
        if link:
            return "https://nofluffjobs.com" + link
        return ''

    def get_company_description(self, soup: BeautifulSoup) -> str:
        company_description = soup.find(id="posting-company")
        if company_description:
            return get_text_helper(company_description)
        
        postingdescription = soup.find(attrs={'data-cy-section': 'JobOffer_Project'})
        if postingdescription and postingdescription.find_all('p'):
            return ", ".join(get_text_helper(p,['Oferujemy:','Opis firmy']) for p in postingdescription.find_all('p'))
        return ''

    def get_category(self, soup: BeautifulSoup) -> str:
        category = get_category_helper(self.get_title(soup), self.get_tech_stack(soup))
        if category:
            return category
        return get_category_helper(get_text_helper(soup.find(attrs={'commonpostingcattech':''})), self.get_tech_stack(soup))


    def get_tech_stack(self, soup: BeautifulSoup) -> str:
        expected_section = soup.find(attrs={'branch': 'musts'})
        expected = expected_section.find_all('li') if expected_section else []

        optional_section = soup.find(attrs={'branch': 'nices'})
        optional = optional_section.find_all('li') if optional_section else []
        
        return ", ".join(get_text_helper(tech) for tech in expected + optional)

    def get_location(self, soup: BeautifulSoup) -> str:
        location_remote = get_text_helper(soup.find(attrs={'data-cy': 'location_remote'})) #Investigate why this does not work correctly
        if location_remote:
            return location_remote
        return get_text_helper(soup.find(attrs={'class': 'popover-locations'}), ['Lokalizacje: '])

    def get_location_type(self, soup: BeautifulSoup) -> str: #Investigate why this does not work correctly
        location = get_text_helper(soup.find(attrs={'data-cy': 'location_pin'}))
        location_remote = get_text_helper(soup.find(attrs={'data-cy': 'location_remote'}))

        if location_remote:
            return location_remote
        if location:
            return location
        return ''

    def get_salary(self, soup: BeautifulSoup) -> str:
        return get_salary_helper(soup.find('common-posting-salaries-list'))

    def get_salary_type(self, soup: BeautifulSoup) -> str:
        salary_section = soup.find('common-posting-salaries-list')

        salary_types = get_salary_type_helper(salary_section)
        if salary_types:
            return salary_types
        
        if not salary_section:
            return ''
        return get_text_helper(salary_section.find('div').find('div'), [' oblicz "na rękę"'])

    def get_years_of_experience(self, soup: BeautifulSoup) -> str:
        return get_years_of_experience_helper(soup)

    def get_responsibilities(self, soup: BeautifulSoup) -> str:
        methodologies_section = soup.find(attrs={'commonpostingmethodologies': ''})
        methodologies = methodologies_section.find_all('li') if methodologies_section else []

        responsibilities_section = soup.find(attrs={'data-cy-section': 'JobOffer_DailyTasks'})
        responsibilities = responsibilities_section.find_all('li') if responsibilities_section else []
        return ", ".join(get_text_helper(responsibility) for responsibility in responsibilities+methodologies)

    def get_requirements(self, soup: BeautifulSoup) -> str:
        requirements_section = soup.find(attrs={'data-cy-section': 'JobOffer_Requirements'})
        requirements = requirements_section.find_all('li') if requirements_section else []
        return ", ".join(get_text_helper(requirement) for requirement in requirements)

    def get_benefits(self, soup: BeautifulSoup) -> str:
        benefits = soup.find_all('section',attrs={'commonpostingperks': ''})
        return ", ".join(get_text_helper(benefit) for benefit in benefits).strip('Benefity ')


    def get_full_offer(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup.find('common-posting-content-wrapper'))
