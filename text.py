



my_list = [1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17,18,19,10,1231,234,252,239]
print("len(my_list) ", len(my_list))


amount_of_trets = 4
step_sise = int(len(my_list)/(amount_of_trets-1))
print("step_sise ", step_sise)
for i in range(amount_of_trets-1):
    to_check_all_rout_ids = my_list[0:step_sise]
    my_list =  my_list[step_sise:]
    print(to_check_all_rout_ids)


to_check_all_rout_ids = my_list
print(to_check_all_rout_ids)
