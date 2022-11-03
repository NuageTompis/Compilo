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
| TABLE                                 -> var_tab
| INTEGER                               -> var_int
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
start = "com")

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


op = { '+' : "add", '-' : "sub"}
def asm_exp(e) :
    if e.data == "exp_nombre":
        return f"mov rax, {e.children[0].value}\n"
    elif e.data in {"exp_var_int", "exp_var_tab"}:
        return f"mov rax, [{e.children[0].value}]\n"
    elif e.data == "exp_par":
        return asm_exp(e.children[0]) # Il suffit de compiler ce qu'il y a à l'intérieur des parenthèses
    elif e.data == "exp_len":
        return f"""
        mov rbx, [{e.children[0].value}]
        mov rax, [rbx]
        """
    elif e.data == "exp_tab_inst":
        E = asm_exp(e.children[0])
        return f"""
        {E}  
        push rax 
        mov rbx, 8
        mul rbx
        add eax, 8
        mov rdi, rax
        call malloc
        mov [rcx], rax
        mov rbx, [rcx]  
        pop rax
        mov [rbx], QWORD rax
        mov rax, rbx                                                                            
        """
    elif e.data == "exp_elem_tab":
        E1 = asm_exp(e.children[1])
        E2 = asm_exp(e.children[0])
        f"""
        {E1}
        mov rcx, rax
        {E2}
        mov rbx, rax
        mov rax, [rbx+8+rcx*8]
        """
    else:
        E1 = asm_exp(e.children[0]) # Pour que ce soit plus lisible
        E2 = asm_exp(e.children[2])
        return f"""
        {E2}
        push rax
        {E1}
        pop rbx
        {op[e.children[1].value]} rax,rbx
        """ # NB : Pour l'instant on s'occupe uniquement de l'opération


def pp_com(c) :
    if c.data == "assignation":
        return f"{pp_lhs(c.children[0])} = {pp_exp(c.children[1])};"
    elif c.data == "if":
        return f"if ({pp_exp(c.children[0])}) {{ {pp_bcom(c.children[1])} }}"
    elif c.data == "while":
        return f"while ({pp_exp(c.children[0])}) {{ {pp_bcom(c.children[1])}}}"
    elif c.data == "print":
        return f"print({pp_exp(c.children[0])})"

def pp_com(c) :
    if c.data == "assignation":
        return f"{pp_lhs(c.children[0])} = {pp_exp(c.children[1])};"
    elif c.data == "if":
        return f"if ({pp_exp(c.children[0])}) {{ {pp_bcom(c.children[1])} }}"
    elif c.data == "while":
        return f"while ({pp_exp(c.children[0])}) {{ {pp_bcom(c.children[1])}}}"
    elif c.data == "print":
        return f"print({pp_exp(c.children[0])})"

def vars_com(c) :
    if c.data == "assignation":
        R = vars_exp(c.children[1]) # Donne toutes les variables qu'il y a dans l'expression
        return {c.children[0].value} | R
    elif c.data in {"if", "while"} :
        B = vars_bcom(c.children[1])
        E = vars_exp(c.children[0])
        return B | E
    elif c.data == "print":
        return vars_exp(c.children[0])

cpt = 0 # Compteur pour le nombre de fonctions fin
def next() : 
    global cpt
    cpt += 1
    return cpt

def asm_com(c) :
    if c.data == "assignation":
        if c.children[0].data in {"var_int", "var_tab"}:
            E = asm_exp(c.children[1])
            return f"""
            {E}
            mov [{c.children[0].children[0].value}], rax
            """
        elif c.children[0].data == "ele_tab":
            E1 = asm_lhs(c.children[0])
            E2 = asm_exp(c.children[1])
            return f"""
                {E1}
                push rax
                {E2}
                pop rbx
                mov [rbx], rax
                """
    elif c.data == "if":
        E = asm_exp(c.children[0])
        C = asm_bcom(c.children[1])
        n = next()
        return f"""
        {E}
        cmp rax,0
        jz fin{n}
        {C}
fin{n} : nop"""
    elif c.data == "while":
        E = asm_exp(c.children[0])
        C = asm_bcom(c.children[1])
        n = next()
        return f"""
        debut{n} : {E}
        cmp rax,0
        jz fin{n}
        {C}
        jmp debut{n}
fin{n} : nop"""
    elif c.data == "print":
        E = asm_exp(c.children[0])
        return f"""
        {E}
        mov rdi, fmt
        mov rsi, rax
        call printf
        """

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

def asm_lhs(l) :
    if l.data == "ele_tab":
        E = asm_exp(l.children[1])
        return f"""
            {E}
            mov rcx, rax
            mov rbx, [{l.children[0]}]
            mov rax, rbx + 8 + rcx*8
            """


def pp_prg(p) :
    F = pp_bfun(p.children[0])
    L = pp_var_list(p.children[1])
    C = pp_bcom(p.children[2])
    R = pp_exp(p.children[3])
    return "%s main (%s) {%s return (%s);\n}" % (F,L,C,R)

def pp_var_list(vl) :
    return ", ".join([t.value for t in vl.children])

#examples
ast = grammaire.parse("tx = int[ix+3] ;")
print(asm_com(ast))
