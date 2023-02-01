#Input:
#   status - string
#   timestamp - int
#   products_handled_by_runner - list of lists of ints
#   products_ts_arrival_to_conv_belt - list of lists of strings

#Output:
#   UNSAT 
#           OR
#   output estritamente descrito no enunciado do projeto

#output - printa os resultados
#Funcao principal

def output(status,timestamp,products_handled_by_runner,products_ts_arrival_to_conv_belt):

    #UNSAT
    if (status == False):
        print("UNSAT")

    #SAT
    else:
        #uma linha com T->timestamp otimo
        print(timestamp)
        #numero de runners de linhas com: numero_de_produtos_handled numero dos produtos handled pelo runner da linha(...) 
        for list in products_handled_by_runner:
           print(*list)

        #numero de orders de linhas com: numero_de_produtos_da_order product_number:ts_when_product_was_put_on_conv_belt(...)
        for list in products_ts_arrival_to_conv_belt:
            print(*list)

