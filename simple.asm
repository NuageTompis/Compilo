extern printf, atoi ; "On note la liste des fonctions qu'on veut employer"

section .data
hello : db "hello world %d", 10, 0 ;  "0 pour dire que c'est la fin de la section data ? 10 pour retour à la ligne"
fmt : db "%s", 10, 0
argc : dq 0
argv : dq 0

section .text
global main ; "pour dire quel est le point d'entrée (dit que cette adresse-là est une adresse qu'il doit rendre disponible à l'extérieur)"
main : ; "Indentations optionnelles"
 push rbp ; "sera expliqué plus tard"
 mov [argc], rdi
 mov [argv], rsi
 mov rdi, hello ; "on met hello dans la variable rdi"
 mov rsi, [argc]
 call printf
 mov rdi, fmt
 mov rbx, [argv] ; argv est un pointeur qui contient un tableau de chaînes de caractères
 mov rdi, [rbx+8]; valeur stockée en rbx+8 ie pointeur du premier argument
 call atoi
 mov rdi, hello
 mov rsi, rax
 call printf
 pop rbp
 ret ; "c'est le return de la fonction main"

