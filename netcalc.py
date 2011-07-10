#!/usr/bin/python
# -*- coding: utf-8 -*-
from pprint import pprint
from table import Table
import re

"""
Kalkulator sieci IPv4
Maxik http://maxik.me/

TODO:
* Optymalizacja
* Przepisanie na klasy
* Walidacja wszelkich danych
* Sprawdzanie liczbowego aspektu wprowadzanego ip - check_ip 0<x<256
* Blokowanie zarezerwowanych pul
"""

VERSION = "1.0.1beta"

def choose_mask(hosts, max_mask=1):
    """Wybranie maski dla danej ilości hostów"""
    masks = []
    for i in range(max_mask, 32):
        if pow(2, 32-i)>=hosts+2:
            masks.append(i)
        else:
            if len(masks) is not 0:
                return max(masks)
            else:
                return False
    
def mask_by_cidr(cidr):
    """Maska w DEC wg. podanego CIDR(/x)"""
    ip = []
    binary = bin(pow(2, 32-int(cidr)))[2:]
    if len(binary)<32:
        binary = ('1'*(32-len(binary)))+binary
    for i in range(8, 33, 8):
        ip.append(str(int(binary[i-8:i], 2)))
    return '.'.join(ip)
    
def ip2bin(ip):
    """Konwertuje podane IP na postać binarną"""
    ret = []
    for part in ip.split('.'):
        ret.append((bin(int(part))[2:]).zfill(8))
    return ret
    
def ip_class(ip):
    """Sprawdza klasę podanego adresu IP"""
    part = ip2bin(ip)[0]
    if part[:1]=='0':
        return 1
    elif part[:2]=='10':
        return 2
    elif part[:3]=='110':
        return 3
    elif part[:4]=='1110':
        return 4
    elif part[:4]=='1111':
        return 5
    else:
        return 0
    
def class_display(ip_class):
    """Zwraca 'nazwę' klasy IP"""
    classes = [False, 'A', 'B', 'C', 'D', 'E']
    return classes[ip_class]
    
def split_binip(binip):
    """Dzieli binarne IP na 4 części po 8 bitów"""
    ret = []
    for i in range(8, 33, 8):
        ret.append(binip[i-8:i])
    return ret
    
def merge_ip(ip_list=['0', '0', '0', '0'], delimiter=''):
    """Łączy IP podane w pierwszym parametrze znakiem z drugiego"""
    return delimiter.join(ip_list)
    
def ip_cidr(ip_str):
    """Format xxx.yyy.zzz.fff/cidr e.g. 192.168.0.1/24"""
    return ip_str.split('/')
    
def check_ip(ip, cidr=False):
    """Sprawdza poprawność podanego IP, drugi parametr=True sprawdza z CIDR po slashu
    TODO:
    * IP 0<x<256
    * Pule zarezerwowane, 127 itp.
    """
    if not cidr:
        regex = re.compile(r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$')
    else:
        regex = re.compile(r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\/[0-9]{1,2}$')
    if regex.match(ip) is not None:
        return True
    else:
        return False

def calc_gw_bc_hosts(netip, cidr):
    """Główna funkcja licząca, zwraca listę: [broadcast, minhost, maxhost, netaddr]"""
    ret = []
    binip = merge_ip(ip2bin(netip))
    net = binip[:cidr]
    devs = binip[cidr:]
    broadcastdev = '1'*len(devs)
    broadcast = split_binip(net+broadcastdev)
    ret.append('.'.join([str(int(v, 2)) for v in broadcast]))
    hostmindev = '1'.zfill(len(devs))
    hostmin = split_binip(net+hostmindev)
    ret.append('.'.join([str(int(v, 2)) for v in hostmin]))
    hostmaxdev = '1'*(len(devs)-1)+'0'
    hostmax = split_binip(net+hostmaxdev)
    ret.append('.'.join([str(int(v, 2)) for v in hostmax]))
    netaddrdev = '0'*len(devs)
    netaddr = split_binip(net+netaddrdev)
    ret.append('.'.join([str(int(v, 2)) for v in netaddr]))
    return ret

def next_network(base_ip, cidr, max_mask):
    """Wstępna wersja funkcji wyliczającej następny adres sieciowy NIE DZIAŁA!"""
    ipbin = merge_ip(ip2bin(base_ip))
    const = ipbin[:cidr]
    free = ipbin[cidr:max_mask]
    freel = len(free)
    devs = ipbin[max_mask:]
    pprint([const, free, devs])
    free = int(free, 2)
    free = bin(free+1)[2:].zfill(freel)
    pprint(split_binip(const+free+devs))
    return '.'.join([str(int(v, 2)) for v in split_binip(const+free+devs)])
    
def next_network_by_bc(base_ip, cidr):
    """Ostateczna wersja powyższej funkcji. Oblicza na podstawie poprzedniego broadcastu DZIAŁA!"""
    ipbin = merge_ip(ip2bin(base_ip))
    const = ipbin[:cidr]
    devs = ipbin[cidr:]
    devsl = len(devs)
    devs = bin(int(devs, 2)+1)[2:].zfill(devsl)
    return '.'.join([str(int(v, 2)) for v in split_binip(const+devs)])


if __name__=='__main__':
    """Śmietnik/piaskownica/minefield aka int main"""
    print 'Kalkulator sieci IPv4'
    print 'Maciej "Maxik" Tarnowski http://maxik.me/'
    print 'Wersja %s' % VERSION
    print
    while True:
        ip = raw_input('Podaj bazowy IP (z CIDR): ')
        if check_ip(ip, True):
            break
        else:
            print "Podane IP ma niewłaściwy format, właściwy to xxx.xxx.xxx.xxx/cidr"
            continue
    print
    print "Adres bazowy: %s Klasa %s Maska: /%d = %s Max. pula adresów: %d" % (ip_cidr(ip)[0], class_display(ip_class(ip_cidr(ip)[0])), int(ip_cidr(ip)[1]), mask_by_cidr(ip_cidr(ip)[1]), pow(2, 32-int(ip_cidr(ip)[1]))-2)
    print
    netcount = int(raw_input('Podaj liczbę sieci, max 26: '))
    print
    nets = []
    hosts_left = pow(2, 32-int(ip_cidr(ip)[1]))-2
    hosts_base = pow(2, 32-int(ip_cidr(ip)[1]))-2
    letters = [chr(x) for x in range(ord('A')-1, ord('Z')+1)]
    i = 1
    while i<=netcount:
        print "Sieć %s" % letters[i]
        hosts = int(raw_input('Hostów dla danej sieci-2 (BC i net) poz. %d: ' % hosts_left))
        nets.append([i, hosts])
        hosts_left-=(hosts+2)
        i+=1
        print
    nets = sorted(nets, key=lambda hosts: hosts[1], reverse=True)
    max_mask = choose_mask(nets[0][1])
    result = [('Siec', 'Maska', 'Adres sieci', 'Broadcast', 'Min. host', 'Max. host', 'Uzytych', 'Wolnych')]
    first = True
    allocated = 0
    used = 0
    for net in nets:
        if first:
            netip = ip_cidr(ip)[0]
            first = False
        else:
            netip = next_network_by_bc(calculated[0], int(ip_cidr(ip)[1]))
        calculated = calc_gw_bc_hosts(netip, choose_mask(net[1]))
        result.append((letters[net[0]], "%s/%d" % (mask_by_cidr(choose_mask(net[1])), choose_mask(net[1])), calculated[3], calculated[0], calculated[1], calculated[2], str(net[1]), str(pow(2, 32-choose_mask(net[1]))-2-net[1])))
        allocated+=(pow(2, 32-choose_mask(net[1]))-2)
        used+=net[1]
    print
    print "Adresów zaalokowanych: %d" % allocated
    print "Adresów wykorzystanych: %d" % used
    print "Wykorzystanie adresów z sieci bazowej: %d%%" % ((float(used)/float(hosts_base))*100)
    print "Wykorzystanie zaalokowanych: %d%%" % ((float(used)/float(allocated))*100)
    restable = Table(result)
    print
    print restable.create_table()
