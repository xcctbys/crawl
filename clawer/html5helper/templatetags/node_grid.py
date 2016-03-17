#coding=utf-8

from django.template import Context
from django import template
from django.template.loader import render_to_string


register = template.Library()


@register.inclusion_tag("html5helper/tags/node_card.html", name="node_card")
def do_node_card(label, nodes, column, node_template, node_template_data={}):
    """
    Args:
        label: will used to update Context. For example, {label: node}
        nodes: any type of list
        column: how many column, don't more than 12. Must in [1, 2, 3, 4, 6, 12]
        node_template: used to render node 
        node_template_data: must be dict, for render node
    """
    node_number = len(nodes)
    node_grids = []
    
    for i in range(column):
        node_grids.append([])
        
    for i in range(node_number):
        j = i % column
        node_grids[j].append(nodes[i])
        
    print node_grids
        
    return {"node_grids":node_grids, "col": 12/column, "label":label, "node_template":node_template, "node_template_data":node_template_data}
    
    

@register.inclusion_tag("html5helper/tags/node_list.html", name="node_list")
def do_node_list(label, nodes, node_template, node_template_data={}):
    """
    Args:
        label: will used to update Context. For example, {label: node}
        nodes: any type of list
        node_template: used to render node 
        node_template_data: must be dict, for render node
    """
    node_htmls = []
    
    for node in nodes:
        c = Context()
        c.update({label:node})
        node_html = render_to_string(node_template, node_template_data, c)
        node_htmls.append(node_html)
        
    return {"node_htmls":node_htmls}