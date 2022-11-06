import lark

grammaire = lark.Lark(r"""
exp : SIGNED_NUMBER              -> exp_nombre
| IDENTIFIER                     -> exp_var
| exp OPBIN exp                  -> exp_opbin
| "(" exp ")"                    -> exp_par
| NAME"(" arg_list ")"           -> call_function 

NAME : /[a-zA-Z]+/

com : IDENTIFIER "=" exp ";"     -> assignation
| "if" "(" exp ")" "{" bcom "}"  -> if
| "while" "(" exp ")" "{" bcom "}"  -> while
| "print" "(" exp ")"               -> print
bcom : (com)*

prg : bfunction "main" "(" var_list ")" "{" bcom "return" "(" exp ")" ";" "}" 

var_list :                       -> vide
| IDENTIFIER (","  IDENTIFIER)*  -> aumoinsune

arg_list : exp ("," exp)

IDENTIFIER : /[a-zA-Z][a-zA-Z0-9]*/
OPBIN : /[+\-*>]/

function : NAME "(" var_list ")" "{" bcom "return" "(" exp ")" ";" "}" 
bfunction : (function)*

%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""",start="prg")

op = { '+' : "add", '-' : "sub"}

def asm_exp(e) :
    if e.data == "exp_nombre":
        return f"mov rax, {e.children[0].value}\n"
    elif e.data == "exp_var":
        return f"mov rax, [{e.children[0].value}]\n"
    elif e.data == "exp_par":
        return asm_exp(e.children[0]) # Il suffit de compiler ce qu'il y a à l'intérieur des parenthèses
    elif e.data == "call_function":
        s=""
        # on push tous les arguments de la fonction dans la pile, 
        # ici notre grammaire accepte des exp_bin normalement
        L = e.children[1]
        for i in range(len(L.children)-1,0,-1) :
            v = L.children[i]
            if v.data == "exp_nombre":
                s = s + f"push {v.value} \n"
            else:
                s = s + f"push [{e.value}] \n"
        s = s + f"call {e.children[0].data} \n" #la valeur retournée est bien dans rax
        s = s + "add rsp, 8" # restauration du pointeur de la pile
        return s
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

def vars_exp(e) :
    if e.data == "exp_nombre":
        return set()
    elif e.data == "exp_var":
        return {e.children[0].value}
    elif e.data == "exp_par":
        return vars_exp(e.children[0])
    elif e.data == "call_function":
        s = set()
        for i in e.children[1]:
            if i.data == "exp_var":
                s = s | {i.value}
            elif i.data == "exp_bin":
                s = s | vars_exp(i)
        return s
    else:
        L = vars_exp(e.children[0])
        R = vars_exp(e.children[2])
        return L | R # L'union de L et de R

def pp_exp(e) :
    if e.data in {"exp_nombre", "exp_var"} :
        return e.children[0].value
    elif e.data == "exp_par":
        return f"({pp_exp(e.children[0])})"
    elif e.data == "call_function":
        return f"{e.children[0].value} ({pp_arg_list(e.children[1])}) "
    else:
        return f"{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"

def pp_com(c) :
    if c.data == "assignation":
        return f"{c.children[0]} = {pp_exp(c.children[1])};"
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
        E = asm_exp(c.children[1])
        return f"""
        {E}
        mov [{c.children[0].value}], rax
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

def pp_bcom(bc) :
    return "\n"  + "\n".join([pp_com(c) for c in bc.children]) +"\n"

def vars_bcom(bc) :
    S = set()
    for c in bc.children :
        S = S | vars_com(c)
    return S

def asm_bcom(bc) :
    return "\n"  + "".join([asm_com(c) for c in bc.children]) +"\n" # En fait on a déjà mis des /n dans les autres fonctions

def pp_name(n):
    return f"{n.value}"

def pp_fun(f):
    N = pp_name(f.children[0])
    L = pp_var_list(f.children[1])
    C = pp_bcom(f.children[2])
    R = pp_exp(f.children[3])
    return "%s(%s) {%s return (%s);\n}" % (N,L,C,R)

def vars_fun(f):
    A = set([t.value for t in f.children[1].children])
    C = vars_bcom(f.children[2])
    R = vars_exp(f.children[3])
    return A | C | R

def vars_bfunction(bf):
    S = set()
    for f in bf.children :
        S = S | vars_fun(f)
    return S

def vars_prg(p) :
    L = set([t.value for t in p.children[1].children])
    C = vars_bcom(p.children[2])
    R = vars_exp(p.children[3])
    return  L | C | R

def pp_bfun(bf) :
    return "\n"  + "\n".join([pp_fun(c) for c in bf.children]) +"\n"

def pp_prg(p) :
    F = pp_bfun(p.children[0])
    L = pp_var_list(p.children[1])
    C = pp_bcom(p.children[2])
    R = pp_exp(p.children[3])
    return "%s main (%s) {%s return (%s);\n}" % (F,L,C,R)

def asm_bfun(bf):
    return "\n"  + "".join([asm_fun(f) for f in bf.children])

def asm_fun(f):
    # Sauvegarde de l'ancien base pointer 
    # Initialisation nouveau base pointer 
    # Reservation place pour variable locale
    s="""
    .type {f.children[0].value},@function
    {f.children[0].value} 
    push rbp
    mov rbp, rsp
    """
    # Allocation variables
    liste = vars_fun(f)
    longueur = len(liste)
    s = s + f"sub rsp 8*{longueur}]"
    # Déclaration des variables locales
    d=""
    for i in range(len(liste)):
        d = d + f"mov rbp-{8*(i+1)}, {liste[i]}"
    s = s + d
    # Sauvegarde des arguemnts : attention le premier argument se trouve en +16
    for i in range(len(f.children[1].children)) :
        v = f.children[1].children[i].value
        e = f"""
        mov rcx, [rbp+{8*(i+2)}] 
        mov [{v}], rcx
        """
        s = s+e
    # asm bcom
    bc = asm_bcom(f.children[2])
    s = s + bc
    # Sauvegarde de la valeur retournée dans rax
    ret = asm_exp(f.children[3])
    s = s + ret
    # fin 
    s = s + "mov rsp, rbp" # stack pointer ramené au niveau de base pointer
    s = s + "pop rbp"     # on restore le base pointer
    s = s + "ret"

    return s

def asm_prg(p) :
    f = open("moule.asm")
    moule = f.read()
    F = asm_bfun(p.children[0])
    moule = moule.replace("FUNCTIONS", F)
    C = asm_bcom(p.children[2])
    moule = moule.replace("BODY", C)
    R = asm_exp(p.children[3])
    moule = moule.replace("RETURN", R)
    D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
    moule = moule.replace("DECL_VARS", D)
    s = ""
    for i in range(len(p.children[1].children)) :
        v = p.children[1].children[i].value
        e = f"""
        mov rbx, [argv]
        mov rdi, [rbx+{8*(i+1)}]
        xor rax,rax
        call atoi
        mov [{v}], rax
        """
        s = s+e
    moule = moule.replace("INIT_VARS", s)
    return moule

def pp_var_list(vl) :
    return ", ".join([t.value for t in vl.children])

def pp_arg_list(l) :
    return ", ".join([pp_exp(e) for e in l.children])

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


