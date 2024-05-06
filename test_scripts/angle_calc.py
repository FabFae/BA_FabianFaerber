num_light = 62
start = -0.2
end = 70

total_angle = abs(start) + abs(end)

angle_per_light = total_angle / num_light

print(angle_per_light)

angles = []

for i in range(71):
    angle = round(90-(i*angle_per_light-abs(start)), 2)
    # print(f"light {i}: {angle} ")
    angles.append(angle)
print(angles)
