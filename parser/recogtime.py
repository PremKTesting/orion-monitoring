import os

directory = "/home/pkurumpanai/Documents/AB_Testing/r201_d130_o540/r201_d130_o540_b1_orion_*/log/2023-06-13/"
os.system("rm -rf recogtime.txt")
os.system("cat %s/* | grep 'Elapsed time for Recognition' >> recogtime.txt" % (directory))
f = open('recogtime.txt', 'r')
lines = f.readlines()

min = 5
avg = 0.000
max = 0.000
counter = 0
for k in lines:
    k = k[61:]
    k = k[:5]
    j = float(k)
    counter += 1
    avg = (((avg * (counter-1)) + j)/counter)
    if j < min:
        min = j
    if j > max:
        max = j
print("min: %.3f ms" % (min))
print("max: %.3f ms" % (max))
print("avg: %.3f ms" % (avg))     
os.system("rm -rf recogtime.txt")   