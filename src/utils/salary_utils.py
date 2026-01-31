"""Utility functions for salary calculations and parsing."""
import re
from .text_utils import split_by_postfix


# Currency mapping for European currencies + US Dollar
EUROPE_CURRENCY_ISO_DICT = {
    "ALL": ["lek"],  # "L"
    "AMD": ["dram", "֏"],
    "AZN": ["manat", "₼"],
    "BAM": ["mark", "KM"],
    "BYN": ["ruble", "Rbl"],
    "CHF": ["franc", "CHF"],
    "CZK": ["koruna", "Kč"],
    "DKK": ["krone", "kr."],
    "EUR": ["euro", "€"],
    "GBP": ["sterling", "£"],
    "GEL": ["lari", "₾"],
    "HUF": ["forint", "Ft."],
    "ISK": ["króna", "kr."],
    "MDL": ["leu"],  # "L"
    "MKD": ["denar", "DEN"],
    "NOK": ["krone", "kr."],
    "PLN": ["złoty", "zł"],
    "RON": ["leu", "lei"],
    "RSD": ["dinar", "DIN"],
    "RUB": ["ruble", "₽"],
    "SEK": ["krona", "kr."],
    "TRY": ["lira", "₺"],
    "UAH": ["hryvnia", "₴"],
    "USD": ["dollar", "$"],
}


def replace_currency_to_iso(text: str) -> str:
    """Replace common currency names/symbols with ISO codes.
    
    Args:
        text: Text containing currency names or symbols
        
    Returns:
        Text with currencies replaced by ISO codes
    """
    for key, common_names in EUROPE_CURRENCY_ISO_DICT.items():
        for common_name in common_names:
            text = text.replace(common_name.lower(), key)
            text = text.replace(common_name.upper(), key)
    return text


def remove_spaces_in_numbers(text: str) -> str:
    """Remove spaces within numbers (e.g., '10 000' -> '10000').
    
    Args:
        text: Text potentially containing spaced numbers
        
    Returns:
        Text with spaces removed from numbers
    """
    return re.sub(r'(?<=\d)[ \u00A0](?=\d)', '', text)


salary_ranges_regex = r'(\d+-)?(\d+)( ' + '| '.join(list(EUROPE_CURRENCY_ISO_DICT.keys())) + r')?'



def get_salary_type(salary_section: str) -> str:
    """Extract salary type from a salary section.
    
    Args:
        salary_section: text containing salary info
        
    Returns:
        Comma-separated salary types (e.g., 'B2B H, UOP')
    """

    salary_section = salary_section.lower()

    found_types = []
    if 'b2b' in salary_section:
        if 'godz. | kontrakt b2b' in salary_section or 'godz. kontrakt b2b' in salary_section or 'hr. | b2b' in salary_section or 'hr. b2b' in salary_section:
            found_types.append('B2B H')
        elif 'mies. | kontrakt b2b' in salary_section or 'mth. | b2b' in salary_section or 'b2b) miesięcznie' in salary_section or 'mth. b2b' in salary_section:
            found_types.append('B2B M')
        else:
            found_types.append('B2B')
    if 'uop' in salary_section or 'umowa o pracę' in salary_section or 'of mandate' in salary_section or 'of employment' in salary_section:
        found_types.append('UOP')
    if 'substitution agreement' in salary_section:
        found_types.append('Substitution')
    if 'dzieło' in salary_section:
        found_types.append('Dzieło')
    if 'zlecenie' in salary_section:
        found_types.append('Zlecenie')

    return ', '.join(found_types)


def get_salary(salary_section: str) -> str:
    """Extract and parse salary ranges from a salary section.
    
    Args:
        salary_section: string containing salary info
        
    Returns:
        Comma-separated salary ranges (e.g., '16800-18480 PLN')
    """
    salary_text = salary_section.upper()
    salary_text = salary_text.replace('B2B', '')
    salary_text = replace_currency_to_iso(salary_text)
    salary_text = salary_text.replace(',00', '').replace('  ', ' ').replace(' - ', '-')
    salary_text = remove_spaces_in_numbers(salary_text)
    salary_ranges = re.findall(salary_ranges_regex, salary_text)

    salary_ranges_arr = [''.join(j for j in sub) for sub in salary_ranges]

    stringify = ", ".join(salary_ranges_arr)
    return stringify



def get_salary_types_sorted(salary_types: str) -> list[str]:
    """Extract and sort salary types from a salary type string.
    
    Args:
        salary_types: String containing salary types (e.g., 'B2B H, UOP')
        
    Returns:
        List of salary types in priority order
    """
    result = []
    if 'B2B H' in salary_types:
        result.append('B2B H')
    if 'Zlecenie' in salary_types: # TODO use UZ instead of Zlecenie, update in conde and in DB
        result.append('Zlecenie')
    if 'UOP' in salary_types:
        result.append('UOP')
    if 'Dzieło' in salary_types:
        result.append('Dzieło')
    if 'B2B M' in salary_types:
        result.append('B2B M')
    return result


def convert_to_pln(number: float, currency: str) -> float:
    """Convert a monetary amount to PLN.
    
    Args:
        number: The amount to convert
        currency: The source currency (PLN, EUR, or USD)
        
    Returns:
        The amount in PLN
        
    Raises:
        Exception: If the currency is not supported
    """
    if currency == 'PLN':
        return number
    elif currency == 'EUR':
        return number * 4.2371  # avg from 21.01.25 - 21.01.26
    elif currency == 'USD':
        return number * 3.7575  # avg from 21.01.25 - 21.01.26
    else:
        raise Exception(f"Unsupported currency {currency}")


def calculate_min_max(salary_ranges: str, salary_type: str, full_offer: str) -> tuple[int, int]:
    """Calculate normalized min/max salary from salary ranges.
    
    Args:
        salary_ranges: Comma-separated salary ranges (e.g., '16800-18480 PLN')
        salary_type: Comma-separated salary types (e.g., 'UOP, B2B M')
        full_offer: The full job offer text (for context)
        
    Returns:
        Tuple of (min_salary, max_salary) normalized to net monthly PLN, or (None, None)
    """
    # Net coefficients for different contract types based on gross-net.png
    dzielo = 0.904
    b2b_m = 0.7703
    zlecenie = 0.7223
    uop = 0.7
    b2b_h = 160 * b2b_m

    if not salary_ranges or not salary_type:
        return None, None

    salary_types = get_salary_types_sorted(salary_type)

    ranges = [range.strip() for range in salary_ranges.split(',')]
    ranges_with_ccy = [split_by_postfix(range, ['PLN']) for range in ranges]

    tmp_ranges = []

    for range_ccy in ranges_with_ccy:
        salary_ccy = range_ccy[1]
        salary_range = range_ccy[0]
        salary_tmp = [float(x) for x in salary_range.split('-')]

        if len(salary_tmp) != 2:
            salary_tmp = [salary_tmp[0], salary_tmp[0]]

        tmp_ranges.append((salary_tmp, salary_ccy))
        
    tmp_ranges.sort(key=lambda x: x[0][1])

    if len(tmp_ranges) != len(salary_types):
        return None, None

    salary_min = None
    salary_max = None

    for salary_tmp, salary_type_tmp in zip(tmp_ranges, salary_types):
        
        salary_range = salary_tmp[0]
        salary_ccy = salary_tmp[1]

        if 'B2B H' in salary_type_tmp:
            salary_min = min(int(convert_to_pln(salary_range[0], salary_ccy) * b2b_h), salary_min or float("inf"))
            salary_max = max(int(convert_to_pln(salary_range[1], salary_ccy) * b2b_h), salary_max or 0)
        
        if 'B2B M' in salary_type_tmp:
            salary_min = min(int(convert_to_pln(salary_range[0], salary_ccy) * b2b_m), salary_min or float("inf"))
            salary_max = max(int(convert_to_pln(salary_range[1], salary_ccy) * b2b_m), salary_max or 0)

        if 'UOP' in salary_type_tmp:
            salary_min = min(int(convert_to_pln(salary_range[0], salary_ccy) * uop), salary_min or float("inf"))
            salary_max = max(int(convert_to_pln(salary_range[1], salary_ccy) * uop), salary_max or 0)

        if 'Dzieło' in salary_type_tmp:
            salary_min = min(int(convert_to_pln(salary_range[0], salary_ccy) * dzielo), salary_min or float("inf"))
            salary_max = max(int(convert_to_pln(salary_range[1], salary_ccy) * dzielo), salary_max or 0)

        if 'Zlecenie' in salary_type_tmp:
            salary_min = min(int(convert_to_pln(salary_range[0], salary_ccy) * zlecenie), salary_min or float("inf"))
            salary_max = max(int(convert_to_pln(salary_range[1], salary_ccy) * zlecenie), salary_max or 0)
    
    if salary_min is None:
        return None, None

    return salary_min, salary_max


def calculate_years_normalized(years_as_text: str) -> int | None:
    """Calculate normalized years of experience from text.
    
    Args:
        years_as_text: Experience text like '4+, 2-3, 40'
        
    Returns:
        Maximum reasonable years of experience (capped at 8), or 0 if none found
    """
    years_ranges_list = years_as_text.replace('+', '').split(',')
    years_as_numbers = [int(float(i.split('-')[0])) for i in years_ranges_list]
    max_years = max([i for i in years_as_numbers if i < 9] + [0])
    return max_years
