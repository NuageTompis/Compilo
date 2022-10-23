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


IDENTIFIER : TABLE | INTEGER

TABLE : "t" /[a-zA-Z0-9]*/

INTEGER: "i" /[a-zA-Z0-9]*/

OPBIN : /[+*\->]/

%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""",
start = "exp")

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

#examples
print(pp_exp(grammaire.parse("tx")))
print(pp_exp(grammaire.parse("ix")))
print(pp_exp(grammaire.parse("3")))
print(pp_exp(grammaire.parse("len(tx)")))
print(pp_exp(grammaire.parse("concat(tx, ty)")))
print(pp_exp(grammaire.parse("int[ix+3]")))



