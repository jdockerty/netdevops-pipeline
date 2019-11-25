from os import system, name
import pyperclip
# Run from console, clears the output and can easily Ctrl + A -> Ctrl + C for easy config dump.
def clear():

    if name == 'nt':
        _ = system('cls')


interface = str(input("Enter the interface connected in GNS3: "))
ip_add_one = str(input("Enter the 1st Public Tunnel Address: "))
ip_add_two = str(input("Enter the 2nd Public Tunnel Address: "))



clear()


with open("BGP_IPsec_template.txt") as config_file:
    for lines_in_file in config_file:
        print(lines_in_file.format(interface, ip_add_one, ip_add_two))