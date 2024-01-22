"""
This module contains two methods used for converting between stock and flow
acsets and amr. Both methods accept an acset/amr JSON dictionary object and
returns its counterpart JSON dictionary object.
"""
import requests
import sympy
import re


def is_number(number):
    """
    Tests to see if an operand in an expression is a number or not.
    """
    try:
        float_num = float(number)
        return True
    except ValueError:
        return False


def acset_to_amr(acset):
    """
    A method that takes in a stock and flow JSON acset dictionary object
    and outputs an equivalent stock and flow JSON amr dictinary object
    """
    stocks = acset['Stock']
    flows = acset['Flow']

    stocks_list = []
    flows_list = []
    links_list = []
    params_list = []
    initials_list = []
    auxiliaries_list = []
    stock_set = set()

    total_params = set()
    params_stock_flow_map = {}

    for stock in stocks:
        stock_name = stock["sname"]
        param_stock_initial_name = stock_name + "0"
        stocks_list.append({'id': stock_name})
        initials_list.append({'target': stock_name, "expression": param_stock_initial_name})
        stock_set.add(stock_name)

        param_dict = {'id': param_stock_initial_name, 'name': param_stock_initial_name, 'value': 0.0}
        params_list.append(param_dict)

    for idx, flow in enumerate(flows):
        flow_id = 'flow' + str(flow['_id'])
        flow_name = flow['fname']
        upstream_stock = stocks[int(flow['u']) - 1]['sname']
        downstream_stock = stocks[int(flow['d']) - 1]['sname']

        flow_dict = {'id': flow_id, 'name': flow_name, 'upstream_stock': upstream_stock,
                     'downstream_stock': downstream_stock, 'rate_expression': flow['ϕf']}

        # this regex pattern finds all operands
        flow_operands = re.findall(r'\b\w+(?:\.\w+)*\b', flow['ϕf'])

        # if an operand is not a stock or number then it must be a parameter for current flow
        flow_params = [param for param in flow_operands if param not in stock_set and not is_number(
            param)]

        # add the current flow parameters to set of total parameters
        total_params |= set(flow_params)

        params_stock_flow_map[flow_id] = []
        params_stock_flow_map[flow_id].extend(flow_params)
        for stock_name in stock_set:
            params_stock_flow_map[flow_id].extend(re.findall(stock_name, flow['ϕf']))

        flows_list.append(flow_dict)

    for param in total_params:
        param_dict = {}

        # naming convention for parameters in stockflow amr?
        param_name = "p_" + param
        param_dict['id'] = param_name
        param_dict['name'] = param_name
        param_dict['value'] = 0.0
        params_list.append(param_dict)

        auxiliary_dict = {'id': param_name, 'name': param_name, 'expression': param_name}
        auxiliaries_list.append(auxiliary_dict)

    for idx, (flow_id, stock_param_list) in enumerate(params_stock_flow_map.items()):
        for stock_or_param in stock_param_list:
            link_dict = {'id': 'link' + str(idx + 1), 'source': stock_or_param, 'target': flow_id}
            links_list.append(link_dict)

    return {
        'header': {
            'name': '',
            'schema': '',
            'description': '',
            'schema_name': 'stockflow',
            'model_version': '0.1',
        },
        'model': {
            'flows': flows_list,
            'stocks': stocks_list,
            'auxiliaries': auxiliaries_list,
            'links': links_list
        },
        'semantics': {'ode': {
            'parameters': params_list,
            'initials': initials_list,
            'observables': [],
            'time': None
        }},
        'metadata': None
    }


def amr_to_acset(amr):
    """
    A method that takes in a stock and flow JSON amr dictionary
    object and outputs an equivalent stock and flow
    JSON acset dictinary object
    """
    flows = amr['model']['flows']
    stocks = amr['model']['stocks']
    links = amr['model']['links']

    flows_list = []
    stocks_list = []
    links_list = []

    symbols = {}
    stocks_mapping = {}
    for parameter in amr['semantics']['ode']['parameters']:
        if parameter['id'].startswith('p_'):
            symbols[parameter['id'][2:]] = sympy.Symbol(parameter['id'][2:])

    for idx, stock in enumerate(stocks):
        stock_id = idx + 1
        stock_name = stock['id']
        stock_dict = {'_id': stock_id, 'sname': stock_name}
        stocks_list.append(stock_dict)
        symbols[stock_name] = sympy.Symbol(stock_name)
        stocks_mapping[stock_name] = idx + 1

    for idx, flow in enumerate(flows):
        upstream_stock = next(
            filter(lambda stock_: stock_['sname'] == flow['upstream_stock'],
                   stocks_list)).get('_id')
        downstream_stock = next(
            filter(lambda stock_: stock_['sname'] == flow['downstream_stock'],
                   stocks_list)).get('_id')
        flow_name = flow['name']

        flow_dict = {'_id': idx + 1, 'u': upstream_stock, 'd': downstream_stock, 'fname': flow_name,
                     "ϕf": flow['rate_expression']}

        flows_list.append(flow_dict)

    link_id = 1
    for idx, link in enumerate(links):
        if link['source'] in stocks_mapping:
            link_dict = {'_id': link_id, 's': stocks_mapping[link['source']],
                         't': link["target"][4:]}
            link_id += 1
            links_list.append(link_dict)

    return {
        'Flow': flows_list,
        'Stock': stocks_list,
        'Link': links_list
    }


if __name__ == "__main__":
    acset_input = requests.get(
        "https://raw.githubusercontent.com/AlgebraicJulia/py-acsets/jpfairbanks-patch-1/"
        "src/acsets/schemas/examples/StockFlowp.json").json()
    amr_output = acset_to_amr(acset_input)

    amr_input = requests.get(
        "https://raw.githubusercontent.com/DARPA-ASKEM/Model-Representations/" \
        "7f5e377225675259baa6486c64102f559edfd79f/stockflow/examples/sir.json").json()

    acset_output = amr_to_acset(amr_input)
