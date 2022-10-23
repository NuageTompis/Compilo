import lark
grammaire = lark.Lark(r"""
exp : SIGNED_NUMBER                     -> exp_nombre
| TABLE                                 -> exp_var_tab
| TABLE"[" exp "]"                      -> exp_elem_tab
| "int[" exp "]"                        -> exp_tab_inst
| "len(" TABLE ")"                      -> exp_len
| "concat(" TABLE "," TABLE ")"         -> exp_concat
| INTEGER                               -> exp_var_int
| exp OPBIN exp                         -> exp_opbin
| "(" exp ")"                           -> exp_par

bcom : (com)*

com : lhs "=" exp ";"                   -> assignation
| "if" "(" exp ")" "{" bcom "}"         -> if
| "while" "(" exp ")" "{" bcom "}"      -> while
| "print" "(" exp ")"                   -> print

prg : "main" "(" var_list ")" "{" bcom "return" "(" exp ")" ";" "}" 

var_list :                              -> vide
| IDENTIFIER ("," IDENTIFIER)*          -> aumoinsune

lhs: TABLE"[" exp "]"                   -> ele_tab
| IDENTIFIER                            -> var

IDENTIFIER : TABLE | INTEGER

TABLE : "t" /[a-zA-Z0-9]*/

INTEGER: "i" /[a-zA-Z0-9]*/

OPBIN : /[+*\->]/

%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""",
start = "prg")

def pp_exp(e) :
    if e.data in {"exp_nombre", "exp_var_int", "exp_var_tab"} :
        return e.children[0].value
    elif e.data == "exp_par":
        return f"({pp_exp(e.children[0])})"
    elif e.data == "exp_elem_tab":
        return f"{e.children[0].value}[{pp_exp(e.children[1])}]"
    elif e.data == "exp_tab_inst":
        return f"int[{pp_exp(e.children[0])}]"
    elif e.data == "exp_len":
        return f"len({e.children[0].value})"
    elif e.data == "exp_concat":
        return f"concat({e.children[0].value}, {e.children[1].value})"
    else:#opbinaire
        return f"{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"

def pp_com(c) :
    if c.data == "assignation":
        return f"{pp_lhs(c.children[0])} = {pp_exp(c.children[1])};"
    elif c.data == "if":
        return f"if ({pp_exp(c.children[0])}) {{ {pp_bcom(c.children[1])} }}"
    elif c.data == "while":
        return f"while ({pp_exp(c.children[0])}) {{ {pp_bcom(c.children[1])}}}"
    elif c.data == "print":
        return f"print({pp_exp(c.children[0])})"

def pp_bcom(bc) :
    return "\n"  + "\n".join([pp_com(c) for c in bc.children]) +"\n"

def pp_lhs(l) :
    if l.data == "ele_tab":
        return f"{l.children[0].value}[{pp_exp(l.children[1])}]"
    else :
        return l.children[0].value

def pp_prg(p) :
    L = pp_var_list(p.children[0])
    C = pp_bcom(p.children[1])
    R = pp_exp(p.children[2])
    return "main (%s) {%s return (%s);\n}" % (L,C,R)

def pp_var_list(vl) :
    return ", ".join([t.value for t in vl.children])

#examples
print(pp_prg(grammaire.parse("main(iX,tY){ix = tY; return (ix);}")))




