import fileinput
import argparse

#Funcao auxiliar

def listoint(cb_to_pack, product_to_cbelt, orders):
    
    new_cb_to_pack = []
    for i in range(len(cb_to_pack)):
        new_cb_to_pack += [int(cb_to_pack[i])]


    new_product_to_cbelt = []
    for i in range(len(product_to_cbelt)):
        temporary_list = []
        for j in range(len(product_to_cbelt[i])):
            temporary_list += [int(product_to_cbelt[i][j])]
        new_product_to_cbelt += [temporary_list]

    new_orders = []
    for i in range(len(orders)):
        temporary_list = []
        for j in range(len(orders[i])):
            temporary_list += [int(orders[i][j])]
        new_orders += [temporary_list]

    return new_cb_to_pack, new_product_to_cbelt, new_orders

#input - funcao que le do ficheiro de input e passa a informacao ao modulo da logica
#Funcao principal

def input():
    parser = argparse.ArgumentParser(description='Warehouse Packaging Scheduling')
    parser.add_argument('input', help="Input file name.")

    args = parser.parse_args()
    file = args.input

    with open(file, 'r') as f:
        initial_positions = []
        product_to_cbelt = []
        orders = []

        lines = f.read().splitlines()

        n_runners = int(lines[0]) #nr de runners
        n_products = int(lines[1]) #nr de produtos

        for i in lines[2].split(" "):
            initial_positions += [int(i)] #posição inicial dos runners

        for times in range(n_products):
            product_to_cbelt += [(lines[3 + times].split(" "))] # t(i,j) tempo do runner até ao produto e por no conveyor belt
        
        cb_to_packaging = lines[3 + n_products].split(" ") # c(i) tempo que o produto leva do conveyor belt até à packaging area
        n_orders = int(lines[3 + n_products + 1])  #nr de orders             
        
        for order in range(n_orders):
            orders += [(lines[3 + n_products + 2 + order].split(" "))] # nr de orders
            
        cb_to_packaging, product_to_cbelt, orders = listoint(cb_to_packaging, product_to_cbelt,orders)


    return n_runners, n_products, initial_positions, product_to_cbelt, cb_to_packaging, n_orders, orders