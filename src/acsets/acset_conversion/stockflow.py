import requests
import sympy


def amr_to_acset():
    amr = requests.get("https://raw.githubusercontent.com/DARPA-ASKEM/Model-Representations/" \
                       "7f5e377225675259baa6486c64102f559edfd79f/stockflow/examples/sir.json").json()

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
            symbols[parameter['id'][2:]] = sympy.Symbol('p.' + parameter['id'][2:])

    for idx, stock in enumerate(stocks):
        stock_id = idx + 1
        stock_name = stock['id']
        stock_dict = {'_id': stock_id, 'sname': stock_name}
        stocks_list.append(stock_dict)
        symbols[stock_name] = sympy.Symbol('u.' + stock_name)
        stocks_mapping[stock_name] = idx + 1

    for idx, flow in enumerate(flows):
        flow_id = idx + 1
        upstream_stock = list(filter(lambda stock: stock['sname'] == flow['upstream_stock'], stocks_list))[0].get(
            '_id')
        downstream_stock = list(filter(lambda stock: stock['sname'] == flow['downstream_stock'], stocks_list))[0].get(
            '_id')
        flow_name = flow['name']

        amr_expression_str = flow['rate_expression']
        acset_expression_str = str(sympy.sympify(amr_expression_str, symbols))

        flow_dict = {}

        flow_dict['_id'] = flow_id
        flow_dict['fname'] = flow_name
        flow_dict['u'] = upstream_stock
        flow_dict['d'] = downstream_stock
        flow_dict["ϕf"] = acset_expression_str

        flows_list.append(flow_dict)

    link_id = 1
    for link in links:
        if link['source'] in stocks_mapping:
            link_dict = {'_id': link_id}
            link_dict['s'] = stocks_mapping[link['source']]
            link_dict['t'] = link['target'][4:]
            link_id += 1
            links_list.append(link_dict)

    return {
        'Flow': flows_list,
        'Stock': stocks_list,
        'Link': links_list
    }


if __name__ == "__main__":
    acset = amr_to_acset()
