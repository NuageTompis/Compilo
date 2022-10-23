from pprint import pp
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
| NAME"(" var_list ")"         -> call_function 


bcom : (com)*

com : lhs "=" exp ";"                   -> assignation
| "if" "(" exp ")" "{" bcom "}"         -> if
| "while" "(" exp ")" "{" bcom "}"      -> while
| "print" "(" exp ")"                   -> print

prg : bfunction "main" "(" var_list ")" "{" bcom "return" "(" exp ")" ";" "}" 

var_list :                              -> vide
| IDENTIFIER ("," IDENTIFIER)*          -> aumoinsune

lhs: TABLE"[" exp "]"                   -> ele_tab
| IDENTIFIER                            -> var

IDENTIFIER : TABLE | INTEGER

TABLE : "t" /[a-zA-Z0-9]*/

INTEGER: "i" /[a-zA-Z0-9]*/

OPBIN : /[+*\->]/

NAME : /[a-zA-Z]+/

function : NAME "(" var_list ")" "{" bcom "return" "(" exp ")" ";" "}" 

bfunction : (function)*

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
    elif e.data == "call_function":
        return f"{e.children[0].value} ({pp_var_list(e.children[1])}) "
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

def pp_fun(f):
    N = pp_name(f.children[0])
    L = pp_var_list(f.children[1])
    C = pp_bcom(f.children[2])
    R = pp_exp(f.children[3])
    return "%s(%s) {%s return (%s);\n}" % (N,L,C,R)

def pp_name(n):
    return f"{n.value}"

def pp_bcom(bc) :
    return "\n"  + "\n".join([pp_com(c) for c in bc.children]) +"\n"

def pp_bfun(bf) :
    return "\n"  + "\n".join([pp_fun(c) for c in bf.children]) +"\n"

def pp_lhs(l) :
    if l.data == "ele_tab":
        return f"{l.children[0].value}[{pp_exp(l.children[1])}]"
    else :
        return l.children[0].value

def pp_prg(p) :
    F = pp_bfun(p.children[0])
    L = pp_var_list(p.children[1])
    C = pp_bcom(p.children[2])
    R = pp_exp(p.children[3])
    return "%s main (%s) {%s return (%s);\n}" % (F,L,C,R)

def pp_var_list(vl) :
    return ", ".join([t.value for t in vl.children])

#examples
print(pp_prg(grammaire.parse("""
f(ix){
    iy = ix;
    return (iy);
}

main(iX,tY){
    ix = f(tY); 
    return (ix);
}""")))




