import requests
import sympy
import re


def acset_to_amr():
    acset = requests.get("https://raw.githubusercontent.com/AlgebraicJulia/py-acsets/jpfairbanks-patch-1/"
                         "src/acsets/schemas/examples/StockFlowp.json").json()

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

        params_stock_flow_map[flow_id].extend(re.findall(r'p\.([^()*+-/ ]+)', flow['ϕf']))
        params_stock_flow_map[flow_id].extend(re.findall(r'u\.([^()*+-/ ]+)', flow['ϕf']))

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
        'properties': '',
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
            'time': ''
        }},
        'metadata': '',
    }


if __name__ == "__main__":
    amr = acset_to_amr()
