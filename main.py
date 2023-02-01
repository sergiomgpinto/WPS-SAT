from input import input
from logic import logica
from output import output
from math import ceil

#Funcao main

if __name__ == '__main__':

    #Modulo do input
    n_runners, n_products, initial_positions, product_to_cbelt, cb_to_packaging, n_orders, orders = input()

    #Binary search algorithm

    LB = 2#LOWER BOUND
    UB = 100#UPPER BOUND
    mean_time = ceil((LB+UB)/2)

    status = True
    products_handled_by_runner = []
    products_ts_arrival_to_conv_belt = []

    #Modulo da logica 
    while (UB != mean_time):
        
        status,products_handled_by_runner,products_ts_arrival_to_conv_belt = logica(n_runners, n_products, initial_positions, product_to_cbelt, cb_to_packaging, n_orders, orders,mean_time)
        
        if (status == False):
            LB = mean_time
        else:
            UB = mean_time 
        
        mean_time = ceil((LB+UB)/2)
        
    status,products_handled_by_runner,products_ts_arrival_to_conv_belt = logica(n_runners, n_products, initial_positions, product_to_cbelt, cb_to_packaging, n_orders, orders,mean_time)

    #Modulo do output

    output(status,mean_time - 1,products_handled_by_runner,products_ts_arrival_to_conv_belt)