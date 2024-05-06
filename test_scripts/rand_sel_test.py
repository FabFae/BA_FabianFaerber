import random
group_of_items = []
for i in range(10000):
    group_of_items.append(i)

num_to_select = 100                           # set the number to select here.
list_of_random_items = random.sample(group_of_items, num_to_select)
first_random_item = list_of_random_items[0]
second_random_item = list_of_random_items[1]

for elem in list_of_random_items:
    print(elem)
