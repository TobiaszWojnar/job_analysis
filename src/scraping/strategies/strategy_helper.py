from bs4 import BeautifulSoup

def get_category_helper(title: str, tech_stack: str) -> str:
    title = title.lower()
    tech_stack = tech_stack.lower()

    if 'data' in title or 'danych' in title or 'danymi' in title:
        return 'Data'
    if 'android' in title or 'mobil' in title or 'react native' in title or 'flutter' in title:
        return 'Mobile'
    if 'test' in title or 'qa' in title:
        return 'QA'
    if 'cyber' in title or 'security' in title or 'bezpieczeństwa' in title:
        return 'Security'
    if 'ux' in title or  'ui' in title:
        return 'UX/UI'
    if 'ruby' in title:
        return 'Ruby'
    if 'business analyst' in title or 'manager' in title or 'pmo' in title:
        return 'Manager'
    if 'devops' in title or 'automation' in title:
        return 'DevOps'
    if 'backend' in title or 'back-end' in title: # In what ??
        return 'Backend'
    if 'frontend' in title or 'front-end' in title:  # In what ??
        return 'Frontend'
    if 'fullstack' in title or 'full-stack' in title:  # In what ??
        return 'Fullstack'
    if 'AI' in title:
        return 'AI'
    if 'support' in title or 'wsparc' in title or 'konsult' in title:
        return 'Support'

    return ''

def get_salary_type_helper(salary_section: BeautifulSoup) -> str:
    if not salary_section:
        return ''

    salary_text = get_text_helper(salary_section).lower()

    found_types = []
    if 'b2b' in salary_text:
        found_types.append('B2B')
        if 'godz. | kontrakt b2b' in salary_text or 'godz. kontrakt b2b' in salary_text or 'hr. | b2b' in salary_text or 'hr. b2b' in salary_text:
            found_types.append('B2B H')
        elif 'mies. | kontrakt b2b' in salary_text or 'mth. | b2b' in salary_text or 'b2b) miesięcznie' in salary_text or 'mth. b2b' in salary_text:
            found_types.append('B2B M')
        else:
            found_types.append('B2B')
    if 'uop' in salary_text or 'umowa o pracę' in salary_text or 'of mandate' in salary_text or 'of employment' in salary_text:
        found_types.append('UOP')
    if 'substitution agreement' in salary_text:
        found_types.append('Substitution')
    if 'dzieło' in salary_text:
        found_types.append('Dzieło')
    if 'zlecenie' in salary_text:
        found_types.append('Zlecenie')

    return ', '.join(found_types)


def get_text_helper(node: BeautifulSoup, replace_strs: list[str] = []) -> str:
    if not node:
        return ''
    text = node.get_text(strip=True, separator=' ').replace('\xa0', ' ').replace('–','-')

    for replace_str in replace_strs:
        text = text.replace(replace_str, '')
    return text

def get_years_of_experience_helper(node: BeautifulSoup) -> str:
    text = node.get_text()
    matches_pl = re.findall(r'(?:\+|\()?\s*(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?)\s*\+?\s+lat', text)
    matches_en = re.findall(r'(?:\+|\()?\s*(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?)\s*\+?\s+year', text)
    return ", ".join(matches_pl + matches_en)

def get_salary_helper(node: BeautifulSoup) -> str: # TODO: triple check if works
    salary_text = get_text_helper(node).upper().replace('ZŁ', 'PLN')
    salary_ranges = re.findall(r'((( ?\d)+([,]\d+)?) ?- ?)?(( ?\d)+([,]\d+)?)[ ]?(PLN)?', salary_text)

    remove_after_comma = ", ".join(salary_ranges).replace(',00', '')
    return re.sub(r'(?<=\d)[ \u00A0](?=\d)', '', remove_after_comma)
