from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

from ...utils.salary_utils import calculate_min_max, calculate_years_normalized


class BaseJobStrategy(ABC):
    @abstractmethod
    def get_title(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_company(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_company_link(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_company_description(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_category(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_tech_stack(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_location(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_location_type(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_salary(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_salary_type(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_years_of_experience(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_responsibilities(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_requirements(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_benefits(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_full_offer(self, soup: BeautifulSoup) -> str:
        pass

#TODO confirm that that works
    def get_salary_min_normalized(self, soup: BeautifulSoup) -> int | None:
        """Calculate normalized minimum salary from parsed salary data."""
        salary = self.get_salary(soup)
        salary_type = self.get_salary_type(soup)
        full_offer = self.get_full_offer(soup)
        min_value, _ = calculate_min_max(salary, salary_type, full_offer)
        return min_value

    def get_salary_max_normalized(self, soup: BeautifulSoup) -> int | None:
        """Calculate normalized maximum salary from parsed salary data."""
        salary = self.get_salary(soup)
        salary_type = self.get_salary_type(soup)
        full_offer = self.get_full_offer(soup)
        _, max_value = calculate_min_max(salary, salary_type, full_offer)
        return max_value

    def get_years_of_experience_normalized(self, soup: BeautifulSoup) -> int | None:
        """Calculate normalized years of experience from parsed data."""
        years_of_experience = self.get_years_of_experience(soup)
        if not years_of_experience:
            return None
        return calculate_years_normalized(years_of_experience)

