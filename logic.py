from input import input 
from pysat.solvers import Glucose4
from pysat.card import *
from collections import Counter
from math import ceil
from pysat.formula import *

def create_variables(n_runners, n_products, initial_positions, product_to_cbelt, cb_to_packaging, n_orders, orders,mean_time):

    t_upper = mean_time #timestamp de 0 a t - 1
    index = 1
    
    X = []
    
    for i in range(n_runners):
        X.append([])
   
        for j in range(n_products):
            X[i].append([])

            for k in range(t_upper):
                X[i][j].append(index)
                index+=1

    P = [[i+index + j*n_products for j in range(t_upper)] for i in range(n_products)] #Variavel P(j,k)

    for list in P:
        if (max(list) > index):
            index = max(list)

    A = [[i+index + j*n_runners for j in range(t_upper)] for i in range(n_runners)] #Variavel A(i,k)

    return X, A, P

def logica(n_runners, n_products, initial_positions, product_to_cbelt, cb_to_packaging, n_orders, orders,mean_time):

    #################################################################################
    ######################### VARS ##################################################
    #################################################################################
    solver = Glucose4()

    X, A, P  = create_variables(n_runners, n_products, initial_positions, product_to_cbelt, cb_to_packaging, n_orders, orders,mean_time)

    t_upper = mean_time
    total_number_of_products_ordered = 0
    max_aux_var_id = 0

    number_of_times_each_product_was_ordered = {}
    vpool_cc5 = IDPool(start_from=max(A[n_runners-1])+1)

    status = ''

    products_handled_by_runner = []
    products_ts_arrival_to_conv_belt = []
    lits_cc1 = []
    lits_cc2 = []
    lits_cc3 = []
    lits_cc5 = []
    lits_cc6 = []
    lits_cc8 = []
    lits_cc9 = []

    for list in orders:
        total_number_of_products_ordered += list[0]
        d = Counter(list[1:])
        for key,value in d.items():
            if key in number_of_times_each_product_was_ordered: 
                number_of_times_each_product_was_ordered[key] +=1
            else:
                number_of_times_each_product_was_ordered[key] = value

    #################################################################################
    ######################### SOMATORIOS ############################################
    #################################################################################

    #um runner nao pode estar em dois sitios ao mesmo tempo

    for runner in range(n_runners):
        for time in range(t_upper):
            for product in range(n_products):
                lits_cc1 += [X[runner][product][time]]
            enc = CardEnc.atmost(lits = lits_cc1, bound = 1,vpool = vpool_cc5,encoding=EncType.bitwise)
            for clause in enc.clauses:
                solver.add_clause(clause)
            lits_cc1.clear()

    max_aux_var_id = enc.nv 
    vpool_cc6 = IDPool(start_from=max_aux_var_id + 1)

    #so pode estar um runner no mesmo produto
    for product in range(n_products):
        for time in range(1,t_upper):
            for runner in range(n_runners):
                lits_cc2 += [X[runner][product][time]]
            enc = CardEnc.atmost(lits = lits_cc2, bound = 1,vpool = vpool_cc6,encoding=EncType.bitwise)
            for clause in enc.clauses:
                solver.add_clause(clause)
            lits_cc2.clear()
    
    max_aux_var_id = enc.nv 
    vpool_cc7 = IDPool(start_from=max_aux_var_id + 1)

    #so pode chegar um produto no max ao mesmo tempo na pack. area
    for time in range(t_upper):
        for product in range(n_products):
            lits_cc3 += [P[product][time]]
        enc = CardEnc.atmost(lits = lits_cc3, bound = 1,vpool = vpool_cc7,encoding=EncType.bitwise)
        for clause in enc.clauses:
            solver.add_clause(clause)
        lits_cc3.clear()

    max_aux_var_id = enc.nv 
    vpool_cc8 = IDPool(start_from=max_aux_var_id + 1)

    #o numero de produtos j pedidos tem de ser igual ao numero de produtos j que chega a pack area
    for product in range(n_products):
        for time in range(t_upper):
            lits_cc5 += [P[product][time]]
     
        enc = CardEnc.equals(lits = lits_cc5, bound = number_of_times_each_product_was_ordered.get(product+1),vpool = vpool_cc8,encoding=EncType.totalizer)
        for clause in enc.clauses:
            solver.add_clause(clause)
    
        lits_cc5.clear()
    
    max_aux_var_id = enc.nv 
    vpool_cc9 = IDPool(start_from=max_aux_var_id + 1)

    #o numero de produtos que chega a pack area tem de ser igual ao numero de produtos pedidos

    for product in range(n_products):
        for time in range(t_upper):
            lits_cc6 += [P[product][time]]

    enc = CardEnc.equals(lits = lits_cc6, bound = total_number_of_products_ordered,vpool = vpool_cc9,encoding=EncType.totalizer)
    for clause in enc.clauses:
        solver.add_clause(clause)  

    max_aux_var_id = enc.nv 
    vpool_cc11 = IDPool(start_from=max_aux_var_id + 1)

    for runner in range(n_runners):
        for product in range(n_products):
            for time in range(1,t_upper):
                lits_cc9 += [X[runner][product][time]]

    enc = CardEnc.equals(lits = lits_cc9, bound = total_number_of_products_ordered ,vpool = vpool_cc11,encoding=EncType.totalizer)
    for clause in enc.clauses:
        solver.add_clause(clause)  

    max_aux_var_id = enc.nv 
    vpool_cc12 = IDPool(start_from=max_aux_var_id + 1)

    #################################################################################
    ######################### A(I,K) -> #############################################
    #################################################################################

    for runner in range(n_runners):
        solver.add_clause([-A[runner][0]])
        solver.add_clause([-A[runner][1]])

        for time in range(t_upper):
            if (time + 1 < t_upper):
                solver.add_clause([-A[runner][time],A[runner][time + 1]])

            if (time - 1 > 0):
                solver.add_clause([A[runner][time],-A[runner][time - 1]])

            for runner2 in range(n_runners):
                if (time * 2 <  t_upper):
                    solver.add_clause([A[runner][time * 2],-A[runner2][time]])

            for products in range(n_products):
                if (time < t_upper):
                    solver.add_clause([-A[runner][time], -X[runner][products][time]])

    #################################################################################
    ######################### P(J,K) ################################################
    #################################################################################

    for product in range(n_products):
        for time in range(t_upper):
            if time <= cb_to_packaging[product]:
                solver.add_clause([-P[product][time]])
            clause_aux = [-P[product][time]]
            signal = 0
            for runner in range(n_runners):
                if(time - cb_to_packaging[product] > 0):
                    clause_aux += [X[runner][product][time - cb_to_packaging[product]]]
                    signal = 1
            if (signal):
                solver.add_clause(clause_aux)
    
    for product in range(n_products):
        for time in range(t_upper):
            for runner in range(n_runners):
                if(time - cb_to_packaging[product] > 0):
                    lits_cc8 += [-A[runner][time - cb_to_packaging[product]]]
            enc = CardEnc.atleast(lits = lits_cc8, bound = 1,vpool = vpool_cc12, encoding=EncType.bitwise)
            for clause in enc.clauses:
                clause_aux = [-P[product][time]]
                clause_aux += clause
                solver.add_clause(clause_aux)
            lits_cc8 = []
    
    #################################################################################
    ######################### X(I,J,K)###############################################
    #################################################################################
    
    for runner in range(n_runners):
        #os runners estao a 1 nos produtos onde spawnam
        solver.add_clause([X[runner][initial_positions[runner] - 1][0]])
        for product in range(n_products):
            #quando um runner spawna no produto j nao pode enviar logo para o conv belt, mas sim passado 1 timestamp
            solver.add_clause([-X[runner][product][0],-P[product][cb_to_packaging[product]]])
            for time in range(t_upper):
                #se um runner esta num produto j entao tem de estar ativo
                solver.add_clause([-X[runner][product][time],-A[runner][time]])

                #se um runner esta num produto j no tempo time entao vai chegar à pack area um produto j no tempo time + Cj
                if (time + cb_to_packaging[product] < t_upper and time > 0):
                    solver.add_clause([-X[runner][product][time],P[product][time + cb_to_packaging[product]]])


    #se nao estiver nenhum runner na posicao j no tempo k nao vai chegar nenhum produto j à pack area no tempo k + Cj
    for product in range(n_products):
        for time in range(t_upper):
            clause_aux = []
            if (time + cb_to_packaging[product] < t_upper ):
                for runner in range(n_runners):
                    clause_aux += [X[runner][product][time]]
                clause_aux += [-P[product][time + cb_to_packaging[product]]]
                solver.add_clause(clause_aux)    

    #se um runner esta ativo num produto j num tempo k entao ou a seguir fica inativo ou fica no proprio produto
    # ou vais para os outros produtos
    
    for runner in range(n_runners):
        for product in range(n_products):
            for time in range(t_upper):
                clause_aux = []
                if time + 1 < t_upper:
                    clause_aux += [-X[runner][product][time]]
                    clause_aux += [A[runner][time + 1]]

                    for product2 in range(n_products):
                        if (time + product_to_cbelt[product][product2] < t_upper):
                            clause_aux += [X[runner][product2][time + product_to_cbelt[product][product2]]]
                    
                    solver.add_clause(clause_aux)
    
    #se um runner esta no produto j e no timestamp k e vai estar no produto w no timestamp k + Tjw entao
    #ele na transicao nao vai estar em nenhum produto
    
    for runner in range(n_runners):
        for product in range(n_products):
            for time in range(t_upper):          
                for product2 in range(n_products):
                    if (time + product_to_cbelt[product][product2] < t_upper):
                        for product3 in range(n_products): 
                            k = time + 1
                            while (k < time + product_to_cbelt[product][product2]):
                                clause_aux = [-X[runner][product][time]]
                                clause_aux += [-X[runner][product2][time + product_to_cbelt[product][product2]]]
                                clause_aux += [-X[runner][product3][k]]
                                solver.add_clause(clause_aux)

                                clause_aux = [-X[runner][product][time]]
                                clause_aux += [-X[runner][product2][time + product_to_cbelt[product][product2]]]
                                clause_aux += [-A[runner][k]]
                                solver.add_clause(clause_aux)

                                k += 1
                                
    status = solver.solve()

    #################################################################################
    ######################### OUTPUT ################################################
    #################################################################################

    model = solver.get_model()

    if status:
 
        delivered_list = []
        for runner in range(n_runners):
            for time in range(1,t_upper):
                for product in range(n_products):
                    if(X[runner][product][time] in model):
                        delivered_list += [X[runner][product][time]]
                        break
        
        products_handled_by_runner = []
        for _ in range(n_runners):
            products_handled_by_runner += [[0]]

        for solution in delivered_list:
            signal = 0
            for runners in range(n_runners):
                if signal:
                   break
                for product in range(n_products):
                    if solution in X[runners][product]:
                        products_handled_by_runner[runners] += [product + 1]
                        products_handled_by_runner[runners][0] += 1
                        signal = 1
                        break

        delivered_list = [] #esta lista vai ter só as variáveis do set P que estão a 1
        for solution in model:
            for products in range(n_products):
                if solution in P[products]:
                    delivered_list += [solution]

        products_to_cbelt_time = []

        for products in range(n_products):
            temporary_list = []
            for time in range(t_upper):
                for chosen_solution in delivered_list:
                    if chosen_solution == P[products][time]:
                        temporary_list += [time - cb_to_packaging[products]]
            products_to_cbelt_time += [temporary_list]

        products_ts_arrival_to_conv_belt = copy.deepcopy(orders)

        for order in range(n_orders):
            orders_length = len(products_ts_arrival_to_conv_belt[order])
            for product in range(orders_length):
                if (product != 0) and products_to_cbelt_time[(products_ts_arrival_to_conv_belt[order][product])-1]:
                    products_ts_arrival_to_conv_belt[order][product] = str(products_ts_arrival_to_conv_belt[order][product]) + ":" +  str(products_to_cbelt_time[(orders[order][product]) - 1][0])
                    products_to_cbelt_time[(orders[order][product]) - 1].pop(0)

    return status, products_handled_by_runner, products_ts_arrival_to_conv_belt
