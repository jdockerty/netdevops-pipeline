from os import system, name


# Run from console, clears the output and can easily Ctrl + A -> Ctrl + C for easy config dump.
def clear():

    if name == 'nt':
        _ = system('cls')


interface = str(input("Enter the interface connected in GNS3: ")) # {0}
ip_outside_address_one = str(input("Enter the 1st Public Tunnel Address: ")) # {1}
#ip_add_two = str(input("Enter the 2nd Public Tunnel Address: "))
tunnel_one_neighbour = str(input("Enter the tunnel 1 neighbor inside address (first address of CIDR block): ")) # {3}
#tunnel_two_neighbour = str(input("Enter the tunnel 2 neighbor inside address (first address of CIDR block): ")) #{6}
my_tunnel_one_CIDR = str(input("Enter the address for the customer tunnel 1 side (2nd address of CIDR block): ")) # {2}
#my_tunnel_two_CIDR = str(input("Enter the address for the customer tunnel 2 side (2nd address of CIDR block): ")) # {5}
clear()

with open("BGP_IPsec_template.txt") as config_file:
    for lines_in_file in config_file:
        print(lines_in_file.format(interface, ip_outside_address_one, my_tunnel_one_CIDR, tunnel_one_neighbour))