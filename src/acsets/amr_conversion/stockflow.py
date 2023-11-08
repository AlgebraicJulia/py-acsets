'''
This module contains two methods used for converting between stock and flow
acsets and amr. Both methods accept an acset/amr JSON dictionary object and
returns its counterpart JSON dictionary object.
'''
import requests
import sympy
import re


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

    params = []
    params_stock_flow_map = {}

    for stock in stocks:
        stocks_list.append({'id': stock['sname']})
        initials_list.append({'target': stock['sname']})

    for idx, flow in enumerate(flows):
        flow_id = 'flow' + str(flow['_id'])
        flow_name = flow['fname']
        upstream_stock = stocks[int(flow['u']) - 1]['sname']
        downstream_stock = stocks[int(flow['d']) - 1]['sname']

        expression_str = flow['ϕf'].replace('p.', '').replace('u.', '')

        flow_dict = {}
        flow_dict['id'] = flow_id
        flow_dict['name'] = flow_name
        flow_dict['upstream_stock'] = upstream_stock
        flow_dict['downstream_stock'] = downstream_stock
        flow_dict['rate_expression'] = expression_str

        params.extend(re.findall(r'p\.([^()*+-/ ]+)', flow['ϕf']))

        params_stock_flow_map[flow_id] = []

        params_stock_flow_map[flow_id].extend(
            re.findall(r'p\.([^()*+-/ ]+)', flow['ϕf']))
        params_stock_flow_map[flow_id].extend(
            re.findall(r'u\.([^()*+-/ ]+)', flow['ϕf']))

        flows_list.append(flow_dict)

    for param in params:
        param_dict = {}
        param_name = 'p_' + param
        param_dict['id'] = param_name
        param_dict['name'] = param_name
        param_dict['value'] = 0.0
        params_list.append(param_dict)

        auxiliary_dict = {}
        auxiliary_dict['id'] = param
        auxiliary_dict['name'] = param
        auxiliary_dict['expression'] = param_name
        auxiliaries_list.append(auxiliary_dict)

    idx = 0
    for flow_id, stock_param_list in params_stock_flow_map.items():
        for stock_or_param in stock_param_list:
            link_dict = {'id': 'link' + str(idx + 1)}
            link_dict['source'] = stock_or_param
            link_dict['target'] = flow_id

            links_list.append(link_dict)
            idx += 1

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
            symbols[parameter['id'][2:]] = sympy.Symbol(
                'p.' + parameter['id'][2:])

    for idx, stock in enumerate(stocks):
        stock_id = idx + 1
        stock_name = stock['id']
        stock_dict = {'_id': stock_id, 'sname': stock_name}
        stocks_list.append(stock_dict)
        symbols[stock_name] = sympy.Symbol('u.' + stock_name)
        stocks_mapping[stock_name] = idx + 1

    for idx, flow in enumerate(flows):
        flow_id = idx + 1
        upstream_stock = next(
            filter(lambda stock: stock['sname'] == flow['upstream_stock'],
                   stocks_list)).get(
            '_id')
        downstream_stock = next(
            filter(lambda stock: stock['sname'] == flow['downstream_stock'],
                   stocks_list)).get(
            '_id')
        flow_name = flow['name']

        amr_expression_str = flow['rate_expression']
        acset_expression_str = str(sympy.sympify(amr_expression_str, symbols))

        flow_dict = {}

        flow_dict['_id'] = flow_id
        flow_dict['u'] = upstream_stock
        flow_dict['d'] = downstream_stock
        flow_dict['fname'] = flow_name
        flow_dict["ϕf"] = acset_expression_str

        flows_list.append(flow_dict)

    link_id = 1
    for idx, link in enumerate(links):
        if link['source'] in stocks_mapping:
            link_dict = {'_id': link_id}
            link_dict['s'] = stocks_mapping[link['source']]
            link_dict['t'] = idx
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
