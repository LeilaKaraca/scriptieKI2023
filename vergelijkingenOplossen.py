from quiche.lang.expr_lang import ExprNode, ExprTree 
from quiche.egraph import EGraph 
from quiche.rewrite import Rule
from quiche.lang.expr_constant_folding import ExprConstantFolding


# Toegevoegde = operator
def eq(a, b):
    return ExprNode._mk_op("=")(a, b)

# Korte notatie om een ExprNode aan te maken
def ex(var):
    return ExprNode(var, ())

def exprTreeMaken(lhs, rhs):
    enode = eq(lhs, rhs)
    return ExprTree(enode)

# Functie die checkt of een gegeven vergelijking gelijk is aan de originele vergelijking van de e-graph
def check(graaf, lhsAntwoord, rhsAntwoord):
    klasse = graaf.add(exprTreeMaken(lhsAntwoord, rhsAntwoord))
    return graaf.root.find() == klasse


# Rekenregels:
# Deze lijst is niet compleet
# Niet alle rekenregels die nodig zijn om alle vergelijkingen op te lossen staan erin, hier was namelijk niet genoeg tijd voor

commutativiteit = [
     ExprTree.make_rule(lambda x, y: (eq(x, y), eq(y, x))),                                     # x = y -> y = x
     ExprTree.make_rule(lambda x, y: (x * y, y * x)),                                           # xy -> yx
     ExprTree.make_rule(lambda x, y: (x + y, y + x)),                                           # x + y -> y + x
     ]

axEnbx = [                                                                                    
    ExprTree.make_rule(lambda x: (x + x, x * 2)),
    ExprTree.make_rule(lambda x, a: (a * x + x, (a + 1) * x)),
    ExprTree.make_rule(lambda x, a, b: (a * x + b * x, (a + b) * x)),                          # ax + bx -> abx

    ExprTree.make_rule(lambda x, a: (a * x - x, (a - 1) * x)),
    ExprTree.make_rule(lambda x, a, b: (a * x - b * x, (a - b) * x)),                          # ax - bx -> (a-b)x


    ExprTree.make_rule(lambda x, a, b, c: (eq(a * x, b * x + c), eq((a - b) * x, c))),         # ax = bx + c -> (a-b)x = c
    ExprTree.make_rule(lambda x, a, c: (eq(a * x, x + c), eq((a - 1) * x, c))),
]

axOverIsTillen = [
    ExprTree.make_rule(lambda x, a, y: (eq(a * x, y), eq(x, y / a))),                          # ax = y -> x = y/a
]

aOverIsTillen = [
    ExprTree.make_rule(lambda x, a, b: (eq(x + a, b), eq(x, b - a))),                           # x + a = b -> x = b - a
    ExprTree.make_rule(lambda x, a, b: (eq(x - a, b), eq(x, b + a))),                           # x - a = b -> x = b + a

    ExprTree.make_rule(lambda x, a, b: (eq(x * a, b), eq(x, b / a))),                           # x * a = b -> x = b / a
    ExprTree.make_rule(lambda x, a, b: (eq(x / a, b), eq(x, b * a))),                           # x / a = b -> x = b * a
]

distributiviteit = [
     ExprTree.make_rule(lambda x, y, z: (x * (y + z), x * y + x * z)),                          # x(y + z) -> xy + yz

     ExprTree.make_rule(lambda x, y, z: (x * (y - z), x * y - x * z)),                          # x(y - z) -> xy - xz


     ExprTree.make_rule(lambda a, b, x: (a * (b * x), a * b * x)),                              # a(bx) -> abx
     ExprTree.make_rule(lambda a, b, c, x: (a * (b * x + c), (a * b * x) + a * c)),             # a(bx + c) -> abx + cx
     ExprTree.make_rule(lambda a, b, c, x: (a * (b * x - c), (a * b * x) - a * c)),             # a(bx + c) -> abx + cx
]

associativiteit = [
    #  associativiteit + en -
     ExprTree.make_rule(lambda x, y, z: (x + y + z, x + (y + z))),
     ExprTree.make_rule(lambda x, y, z: (x + y - z, x + (y - z))),
     ExprTree.make_rule(lambda x, y, z: (x - y - z, x - (y + z))),
     ExprTree.make_rule(lambda x, y, z: (x - y + z, x - (y - z))),

    #  associativiteit * en /
     ExprTree.make_rule(lambda x, y, z: (x * y * z, x * (y * z))),
     ExprTree.make_rule(lambda x, y, z: (x * y / z, x * (y / z))),
     ExprTree.make_rule(lambda x, y, z: (x / y / z, x / (y * z))),
     ExprTree.make_rule(lambda x, y, z: (x / y * z, x / (y / z)))
]


regels = commutativiteit + axEnbx + axOverIsTillen + aOverIsTillen + distributiviteit + associativiteit


# Functie die een gegeven vergelijking oplost met een e-graph en meteen checkt of het meegegeven antwoord gevonden is
def vergelijkingOplossenChecken(lhs, rhs, lhsAntwoord, rhsAntwoord, regels):
    egraph = EGraph(exprTreeMaken(lhs, rhs), ExprConstantFolding())

    x = 0

    while not check(egraph, lhsAntwoord, rhsAntwoord) and x < 5:        # maximaal 5 iteraties runnen
        Rule.apply_rules(regels, egraph)
        x += 1

    return check(egraph, lhsAntwoord, rhsAntwoord)




"""
Voorbeeld hoe vergelijking op te lossen
"""

# 5x - 10 = -3x + 6
lhs = (ex(5) * ex("x")) - ex(10)
rhs = (ex(-3) * ex("x")) + ex(6)

# x = 2
lhsAntwoord = ex("x")
rhsAntwoord = ex(2)

print(vergelijkingOplossenChecken(lhs, rhs, lhsAntwoord, rhsAntwoord, regels))