from typing import Any, Dict, List
import os
import json
this_dir = os.path.dirname(__file__)


def find_key_lengths(table_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Find the lengths of the table columns in the table_data

    Parameters
    ----------
    table_data : list
        List of dictionaries with the table data

    Returns
    -------
    dict
        Dictionary with the keys and the lengths of columns in the table
    """
    keys_and_lengths = {}
    for item in table_data:
        for key, value in item.items():
            current_length = keys_and_lengths.get(key, 0)
            if len(str(value)) > current_length:
                keys_and_lengths[key] = len(str(value))
    for key, value in keys_and_lengths.items():
        new_length = value + 3
        if new_length <= len(key):
            new_length = len(key) + 3
        keys_and_lengths[key] = new_length
    return keys_and_lengths


def create_splitter(length: int) -> str:
    """
    Create a line of "-" with the given length
    """
    return f'{"-"*length}'


def create_line(
    line_data: Dict[str, Any],
    keys_and_lengths: Dict[str, int],
    columns: List[str] = None,
) -> str:
    """
    Create a line for the table

    Parameters
    ----------
    line_data : dict
        Dictionary with the data for the line
        the key is the name of the column and the value is the value for the column
    keys_and_lengths : dict
        Dictionary with the keys and the lengths of columns in the table

    Returns
    -------
    str
        The line for the table
    """
    line = "|"
    columns = columns or list(keys_and_lengths.keys())
    for key in columns:
        length = keys_and_lengths[key]
        line += f' {str(line_data.get(key, "")):{length}} |'
    return line


def create_header(length: int, table_name: str) -> str:
    """
    Create the header for the table

    Parameters
    ----------
    length : int
        The length of the header
    table_name : str
        The name of the table

    Returns
    -------
    str
        The header for the table

    """
    name_length = len(table_name) + 4

    left_length = int((length - name_length) / 2)

    if name_length % 2 != 0:
        return f'{"-"*left_length}  {table_name}  {"-"*left_length}-'
    return f'{"-"*left_length}  {table_name}  {"-"*left_length}'


def print_table(
    table_name: str,
    table_data: List[Dict[str, Any]],
    sort_by: str = None,
    columns: List[str] = None,
) -> List[str]:
    """
    Print a table with the given data

    Parameters
    ----------
    table_name : str
        The name of the table
    table_data : list
        List of dictionaries with the table data
    sort_by : str, optional
        The key to sort the table by, by default None
    """
    keys_and_lengths = find_key_lengths(table_data)

    columns = columns or list(keys_and_lengths.keys())
    header_line = create_line(
        {key: key for key in columns}, keys_and_lengths, columns=columns
    )
    splitter = create_splitter(len(header_line))
    table_header = create_header(len(header_line), table_name)

    lines = [table_header, header_line, splitter]
    if sort_by:
        table_data = sorted(table_data, key=lambda x: x[sort_by])
    for line in table_data:
        lines.append(create_line(line, keys_and_lengths, columns=columns))
        lines.append(splitter)
    print("\n".join(lines))
    return lines

def show_proxy_stats():
    with open(os.path.join(this_dir, "stats", "proxies.json")) as f:
        proxie_data = json.load(f)

    proxies = {}
    for datapoint in proxie_data:
        #print(datapoint)

        current_data = proxies.get(datapoint["proxy"], {"Success": 0, "Failure": 0})
        if datapoint["success"] is True:
            current_data["Success"] += 1
        else:
            current_data["Failure"] += 1
        proxies[datapoint["proxy"]] = current_data

    for proxy, stats in proxies.items():
        stats["Total"] = stats["Success"] + stats["Failure"]
        stats["Success Rate %"] = round(stats["Success"] / stats["Total"] * 100, 2)
        stats["Proxy"] = proxy

    print_table(
        table_name="Proxies",
        table_data=list(proxies.values()),
        sort_by="Success Rate %",
        columns=["Proxy", "Success", "Failure", "Total", "Success Rate %"],
    )

def show_domain_stats():
    with open(os.path.join(this_dir, "stats", "domains.json")) as f:
        domain_data = json.load(f)

    domains = {}
    for datapoint in domain_data:
        current_data = domains.get(datapoint["domain"], {"Success": 0, "Failure": 0})
        if datapoint["success"] is True:
            current_data["Success"] += 1
        else:
            current_data["Failure"] += 1
        domains[datapoint["domain"]] = current_data

    for domain, stats in domains.items():
        stats["Total"] = stats["Success"] + stats["Failure"]
        stats["Success Rate %"] = round(stats["Success"] / stats["Total"] * 100, 2)
        stats["Domain"] = domain

    print_table(table_name="Domains", table_data=list(domains.values()),
        sort_by="Success Rate %",
        columns=["Domain", "Success", "Failure", "Total", "Success Rate %"], )

if __name__ == "__main__":
    show_proxy_stats()
    show_domain_stats()
