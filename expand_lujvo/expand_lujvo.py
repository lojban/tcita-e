# -*- coding: utf-8 -*-

# The content of this file is licensed under a CC0 1.0 Universal license (see the file LICENSE.txt located in the same directory).

'''
REQUIREMENTS:
   rafsi_list.csv
      list of rafsi following the format "gismu;cvc;ccv;cvv;" on every line.
   expand_lujvo_in.txt
      a file containing a list of lujvo used as the input for this program.
   
   The program writes the output into a file "expand_lujvo_out.txt".
'''

import sys, csv, re
from typing import List, Tuple


def gismus_from_lujvo(lujvo, rafsi_list):
   rafsis: List[Tuple] = rafsis_from_lujvo(lujvo)
   gismus = []
   # print("\nWORD: " + lujvo)
   # for r in rafsis:
   #    print(str(r))
   # print("-".join([*map((lambda t: t[1]), rafsis)]))
   for (type, rafsi) in rafsis:
      if type == "G":
         is_found = True
         gismus.append(rafsi)
      if type not in ("G", "*"):
         i = {"GY" : 0, "G" : 0, "CVC" : 1, "CCV" : 2, "CVV" : 3}[type]
         is_found = False
         for row in rafsi_list:
            if i < len(row):
               if row[i] == rafsi or (type == "GY" and row[0][:4] == rafsi):
                  gismus.append(row[0])
                  is_found = True
      if not is_found:
         gismus.append("<" + rafsi + ">")
   return gismus

Cs = "bcdfgjklmnprstvxz"
Vs = "aeiou"
Ds = ["ai", "au", "ei", "oi"]

def matches_cd(s):
  if len(s) < 3:
    return False
  return s[0] in Cs and s[1:3] in Ds

def matches_cvhv(s):
  if len(s) < 4:
    return False
  return (s[0] in Cs and s[1] in Vs
          and s[2] == "'" and s[3] in Vs)

def matches_ccv(s):
  if len(s) < 3:
    return False
  # TODO: s[:2] in initial_CC
  return s[0] in Cs and s[1] in Cs and s[2] in Vs
  
def matches_cvc(s):
  if len(s) < 3:
    return False
  return s[0] in Cs and s[1] in Vs and s[2] in Cs

def matches_gismy(s):
  if len(s) < 4:
    return False
  return (s[0] in Cs
          and ((s[1] in Cs and s[2] in Vs)
               or (s[1] in Vs and s[2] in Cs))
          and s[3] in Cs and (len(s) == 4 or s[4] == "y"))

def matches_gismu(s):
  if len(s) != 5:
    return False
  return (s[0] in Cs
          and ((s[1] in Cs and s[2] in Vs)
               or (s[1] in Vs and s[2] in Cs))
          and s[3] in Cs and s[4] in Vs)


def rafsis_from_lujvo(lujvo: str) -> List[Tuple]:
   l = len(lujvo)
   r = []
   is_initial = True
   is_final = False
   if l < 6:
      return []
   # TODO: add "if is_initial"
   while True:
      n = 0
      if matches_cd(lujvo):
         n = 3
      elif matches_cvhv(lujvo):
         n = 4
      if n != 0:
         r.append(("CVV", lujvo[:n]))
         if (n < len(lujvo)):
            if ( (lujvo[n] == "r" and lujvo[n+1] in Cs)
                  or (lujvo[n] == "n" and lujvo[n+1] == "r") ):
               n += 1
      else:
         if matches_gismy(lujvo):
            n = 5
            r.append(("GY", lujvo[:4]))
         elif matches_gismu(lujvo):
            n = 5
            r.append(("G", lujvo[:5]))
            break
         elif matches_ccv(lujvo):
            n = 3
            r.append(("CCV", lujvo[:3]))
         elif matches_cvc(lujvo):
            r.append(("CVC", lujvo[:3]))
            # TODO: cvc(y) voice check
            if len(lujvo) > 3 and lujvo[3] == "y":
               n = 4
            else:
               n = 3
      assert n <= len(lujvo)
      lujvo = lujvo[n:]
      is_initial = False
      if n == 0:
        if len(lujvo) > 0:
           r.append(("*", lujvo))
        break
   return r


# === ENTRY POINT === #

path = sys.argv[0]
i = len(path) - 1
while i >= 0 and path[i] not in "/\\":
   i -= 1
path = path[: i + 1]
with open(path + "rafsi_list.csv", "r") as rl, \
     open(path + "expand_lujvo_in.txt", "r") as inf, \
     open(path + "expand_lujvo_out.txt", "wb") as outf:
   rafsi_list = []
   csv_reader = csv.reader(rl, delimiter=';')
   for row in csv_reader:
      rafsi_list.append(row)
   words = re.split(r'[,;\s\r\n]+', inf.read())
   length = len(words)
   i = 0
   while i < length:
      w = words[i].strip()
      if w != "":
         rafsis = " ".join(gismus_from_lujvo(w, rafsi_list))
         if rafsis == "":
            rafsis = "∅"
         words[i] += " = " + rafsis
      i += 1
   outf.truncate()
   outf.writelines(map((lambda l: (l + "\n").encode('utf-8')), words))



