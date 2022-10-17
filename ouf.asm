extern printf, atoi

section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
Y : dq 0
T : dq 0
X : dq 0
Z : dq 0

section .text
global main
main : 
    push rbp
    mov [argc], rdi
    mov [argv], rsi
    
        mov rbx, [argv]
        mov rdi, [rbx+8]
        xor rax,rax
        call atoi
        mov [X], rax
        
        mov rbx, [argv]
        mov rdi, [rbx+16]
        xor rax,rax
        call atoi
        mov [Y], rax
        
        mov rbx, [argv]
        mov rdi, [rbx+24]
        xor rax,rax
        call atoi
        mov [Z], rax
        
    

        debut1 : mov rax, [X]

        cmp rax,0
        jz fin1
        

        mov rax, 4

        mov [T], rax
        
        
        mov rax, 1

        push rax
        mov rax, [X]

        pop rbx
        sub rax,rbx
        
        mov [X], rax
        
        
        mov rax, 1

        push rax
        mov rax, [Y]

        pop rbx
        add rax,rbx
        
        mov [Y], rax
        

        jmp debut1
fin1 : nop

    mov rax, [Y]

    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret
