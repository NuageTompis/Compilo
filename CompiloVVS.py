from pprint import pp
import sys
input = sys.argv
filename = input[1]
import lark
grammaire = (r"""
exp : SIGNED_NUMBER                     -> exp_nombre
| TABLE                                 -> exp_var_tab
| TABLE"[" exp "]"                      -> exp_elem_tab
| "int[" exp "]"                        -> exp_tab_inst
| "len(" TABLE ")"                      -> exp_len
| INTEGER                               -> exp_var_int
| exp OPBIN exp                         -> exp_opbin
| "(" exp ")"                           -> exp_par
| NAME"(" var_list ")"         -> call_function 
bcom : (com)*
com : lhs "=" exp ";"                   -> assignation
| "if" "(" exp ")" "{" bcom "}"         -> if
| "while" "(" exp ")" "{" bcom "}"      -> while
| "print" "(" exp ")"                   -> print
| "sort" "(" exp ")"                    -> sort
| "tableprint" "(" exp ")"              -> tab_print
prg : "main" "(" var_list ")" "{" bcom "return" "(" exp ")" ";" "}" 
var_list :                              -> vide
| IDENTIFIER ("," IDENTIFIER)*          -> aumoinsune
lhs: TABLE"[" exp "]"                   -> ele_tab
| TABLE                                 -> var_tab
| INTEGER                               -> var_int
IDENTIFIER : TABLE | INTEGER
TABLE : "t" /[a-zA-Z0-9]*/
INTEGER: "i" /[a-zA-Z0-9]*/
OPBIN : /[+*\->]/ | "concat" | "mult" | "add" | "sum" | "times" | "sub" | "minus"
NAME : "f" /[a-zA-Z]*/
function : NAME "(" var_list ")" "{" bcom "return" "(" exp ")" ";" "}" 
bfunction : (function)*
%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""")
grammairePrg = lark.Lark(grammaire, start = "prg")

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
    elif e.data == "call_function":
        
        return f"{e.children[0].value} ({pp_var_list(e.children[1])}) "
    else:#opbinaire
        return f"{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"


op = { '+' : "add", '-' : "sub", '*' : "mul", "mult" : "mul r14", "add" : "add rax, r14", "sub" : "sub rax, r14", "sum" : "add rax, r13", "minus" : "sub rax, r13", "times" : "mul r13"}
def asm_exp(e) :
    if e.data == "exp_nombre":
        return f"mov rax, {e.children[0].value}\n"
    elif e.data in {"exp_var_int", "exp_var_tab"}:
        return f"mov rax, [{e.children[0].value}]\n"
    elif e.data == "exp_par":
        return asm_exp(e.children[0]) # Il suffit de compiler ce qu'il y a ?? l'int??rieur des parenth??ses
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
        return f"""
        {E1}
        mov rcx, rax
        mov rax, [{e.children[0]}]
        mov rbx, rax
        mov rax, rcx
        mov rdx, 8
        mul rdx
        add rax, 8
        add rax, rbx
        mov rbx, rax
        mov rax, QWORD [rbx]
        """
    else:
        E1 = asm_exp(e.children[0]) # Pour que ce soit plus lisible
        E2 = asm_exp(e.children[2])
        # Si les 2 op??randes sont des entiers
        if e.children[1].value == '*'  :
            return f"""
            {E2}
            push rax
            {E1}
            pop rbx
            {op[e.children[1].value]} rbx
            """
        elif e.children[1].value == "concat" :
            # On peut les adresses des 2 tableaux et on met la somme de leur longueur dans rax
            a =  f"""
            {E2}
            push rax
            {E1}
            pop rbx
            mov rcx, [rax]
            add rcx, [rbx]
            push rbx
            push rax
            mov rax, rcx
            """

            # On cr??e un nouveau tableau de la bonne longueur, son adresse est dans rax
            a = a + f"""
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

            # On copie les ??l??ments du premier tableau
            # Le nouveau tableau est ?? l'adresse r8 et l'ancien dans rcx
            # On ajoute les ??l??ments du dernier au premier, aux adresses r12 et r11 respectivement pour l'adresse dans le nouveau et l'ancien tableau
            n = next()
            a = a + f"""
            pop rcx
            mov rbx, [rcx]
            mov r8, rax
            mov r9, 8
            
            mov rax, rbx
            mul r9
            push rax
            mov r11, rax
            mov r12, r11
            add r12, r8
            add r11, rcx


            debut{n} : cmp rbx,0
            jz fin{n}

            mov r13, [r11]
            mov [r12], r13

            sub r12, r9
            sub r11, r9
            dec rbx
            jmp debut{n}
    fin{n} : nop                                                                          
                """

            # On copie les ??l??ments du deuxi??me tableau
            n = next()
            a = a + f"""
            pop r15
            add r12, r15


            pop rcx
            mov rbx, [rcx]
            
            mov rax, rbx
            mul r9
            mov r11, rax
            add r12, r11
            add r11, rcx
            add rax, rcx


            debut{n} : cmp rbx,0
            jz fin{n}

            mov r13, [r11]
            mov [r12], r13

            sub r12, r9
            sub r11, r9
            dec rbx
            jmp debut{n}
    fin{n} : nop    
            mov rax, r8                                                                      
                """
            return a
        elif e.children[1].value in {"times", "sum", "minus"} :
            # On push les adresses des 2 tableaux et on met la longueur du premier dans rax
            a =  f"""
            {E2}
            push rax
            {E1}
            pop rbx
            mov rcx, [rax]
            push rbx
            push rax
            mov rax, rcx
            """

            # On cr??e un nouveau tableau de la bonne longueur, son adresse est dans rax
            a = a + f"""
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

            # On copie les ??l??ments du premier tableau
            # Le nouveau tableau est ?? l'adresse r8 et l'ancien dans rcx
            # On ajoute les ??l??ments du dernier au premier, aux adresses r12 et r11 respectivement pour l'adresse dans le nouveau et l'ancien tableau
            n = next()
            a = a + f"""
            pop rcx
            pop r10
            mov rbx, [rcx]
            mov r8, rax
            mov r9, 8
            
            mov rax, rbx
            mul r9
            mov r11, rax
            mov r12, r11
            add r12, r8
            add r10, r11
            add r11, rcx


            debut{n} : cmp rbx,0
            jz fin{n}

            mov r13, [r11]
            mov rax, [r10]
            {op[e.children[1].value]}
            mov [r12], rax

            sub r12, r9
            sub r11, r9
            sub r10, r9
            dec rbx
            jmp debut{n}
    fin{n} : nop  

            mov rax, r8                                                                   
                """
            return a

        elif e.children[1].value in {"add", "mult", "sub"} :
            n = next()
            return f"""
            {E2}
            push rax
            {E1}
            pop r10
            push rax

            mov rax, [r10]
            mov rcx, 8
            mul rcx
            add rax, 8
            mov rdi, rax
            call malloc
            mov rcx, rax
            mov r15, [r10]
            mov [rax], r15

            mov rbx, [r10]
            pop rdx
            mov r14, rdx
            mov r9, 8
            mov rax, 8
            mul rbx
            mov r11, r10
            add r11, rax
            add rcx, rax

            debut{n} : cmp rbx,0
            jz fin{n}

            mov rax, QWORD [r11]
            {op[e.children[1].value]}
            mov QWORD [rcx], rax

            sub r11, r9
            sub rcx, r9
            dec rbx
            jmp debut{n}
    fin{n} : nop    

            mov rax, rcx
            """
        elif e.children[1].value in {'+', '-'}  :
            return f"""
            {E2}
            push rax
            {E1}
            pop rbx
            {op[e.children[1].value]} rax,rbx
            """



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
        return vars_lhs(c.children[0]) | R
    elif c.data in {"if", "while"} :
        B = vars_bcom(c.children[1])
        E = vars_exp(c.children[0])
        return B | E
    elif c.data in {"print", "sort", "tab_print"}:
        return vars_exp(c.children[0])

def vars_exp(e) :
    if e.data in  {"exp_nombre", "exp_tab_inst"} :
        return set()
    elif e.data in {"exp_var_int", "exp_var_tab", "exp_len"} :
        return {e.children[0].value}
    elif e.data == "exp_par":
        return vars_exp(e.children[0])
    elif e.data == "exp_elem_tab" :
        L = {e.children[0]}
        R = vars_exp(e.children[1])
        return L | R
    else: # opbin
        L = vars_exp(e.children[0])
        R = vars_exp(e.children[2])
        return L | R # L'union de L et de R


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
    elif c.data == "tab_print" :
        E = asm_exp(c.children[0])
        n = next()
        return f"""
        {E}
        mov rbx, [rax]
        mov r11, rax
        debut{n} : cmp rbx, 0
        jz fin{n}
            add r11, 8
            mov rax, [r11]
            mov rdi, fmt
            mov rsi, rax
            push rbx
            push r11
            push rax
            push rdi
            call printf
            pop rdi
            pop rax
            pop r11
            pop rbx
            dec rbx
        jmp debut{n}
    fin{n} : nop
        """
    elif c.data == "sort" :
        E = asm_exp(c.children[0])
        n = next()
        next()
        next()
        # Nous allons trier le tableaun ?? l'aide d'un tri s??lection
        # L'adresse du tableau est dans rax
        # r10 contient le nombre d'??l??ments qu'il reste ?? trier
        # r8 contient l'adresse de l'??l??ment qu'on compare
        # r9 contient sa valeur
        # r12 contient l'indice qui a la valeur minimale
        # r13 contient cette valeur
        # r15 contient la valeur interm??diaire pour le switch
        return f"""
        {E}
        mov r8, rax
        mov rbx, [r8]
        mov r10, rbx
        dec r10

        debut{n} : cmp rbx, 0
    jz fin{n}
        add r8, 8
        mov r9, [r8]
        mov r12, r8
        mov r13, r9
        mov r11, r8
        debut{n+1} : cmp r10, 0
        jz fin{n+1}
            add r11, 8
            debut{n+2} : cmp r13, [r11]
            jl fin{n+2}
                mov r12, r11
                mov r13, [r12]
            fin{n+2} : nop
            dec r10
        jmp debut{n+1}
        fin{n+1} : nop
        mov r15, [r8]
        mov [r8], r13
        mov [r12], r15
        dec rbx
        mov r10, rbx
        dec r10
    jmp debut{n}
    fin{n} : nop
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

def vars_bcom(bc) :
    S = set()
    for c in bc.children :
        S = S | vars_com(c)
    return S

def asm_bcom(bc) :
    return "\n"  + "".join([asm_com(c) for c in bc.children]) +"\n" # En fait on a d??j?? mis des /n dans les autres fonctions

def pp_bfun(bf) :
    return "\n"  + "\n".join([pp_fun(c) for c in bf.children]) +"\n"

def pp_lhs(l) :
    if l.data == "ele_tab":
        return f"{l.children[0].value}[{pp_exp(l.children[1])}]"
    else :
        return l.children[0].value

def vars_lhs(l) :
    if l.data in {"var_tab", "var_int"} :
        return {l.children[0].value}
    elif l.data == "ele_tab" :
        L = {l.children[0].value}
        R = vars_exp(l.children[1])
        return L | R

def asm_lhs(l) :
    if l.data == "ele_tab":
        E = asm_exp(l.children[1])
        return f"""
            {E}
            mov rcx, rax
            mov rbx, [{l.children[0]}]
            mov rax, rcx
            mov rdx, 8
            mul rdx
            add rax, 8
            add rax, rbx
            """


def pp_prg(p) :
    F = pp_bfun(p.children[0])
    L = pp_var_list(p.children[1])
    C = pp_bcom(p.children[2])
    R = pp_exp(p.children[3])
    return "%s main (%s) {%s return (%s);\n}" % (F,L,C,R)

def vars_prg(p) :
    L = set([t.value for t in p.children[0].children])
    C = vars_bcom(p.children[1])
    R = vars_exp(p.children[2])
    return L | C | R

def asm_prg(p) :
    f = open("moule.asm")
    moule = f.read()
    C = asm_bcom(p.children[1])
    moule = moule.replace("BODY", C)
    R = asm_exp(p.children[2])
    moule = moule.replace("RETURN", R)
    D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
    moule = moule.replace("DECL_VARS", D)
    s = ""
    for i in range(len(p.children[0].children)) :
        v = p.children[0].children[i].value
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



# Assemblage du code
program = open(filename, "r")
code = ""
lines  = program.readlines()
for line in lines :
    code += line
ast = grammairePrg.parse(code)

asm = asm_prg(ast)

f = open("ouf.asm", "w")
f.write(asm)
f.close()