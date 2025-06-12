
.model small
.stack  100h

.data
    a dw 5
    b dw 10
    c dw 3

    result dw 0

    msg_fmt db "Результат b - c + a = $"

.code
main proc
    mov ax, @data
    mov ds, ax 

    mov ax, b 
    sub ax, c 
    add ax, a 

    mov result, ax

    lea dx, msg_fmt
    mov ah, 09h
    int 21h

    mov bx, 10 
    mov si, 0
    mov cx, 0
    mov dx, 0 

    mov ax, result

    cmp ax, 0
    jge skip_minus
        mov dl, '-'
        mov ah, 02h
        int 21h
        neg ax
    skip_minus:

    mov cx, 0 

digits_loop:
    xor dx, dx
    div bx 
    push dx 
    inc cx 
    cmp ax, 0 
    jne digits_loop


print_digits:
    pop dx
    add dl, '0'
    mov ah, 02h
    int 21h
    loop print_digits

    mov ah, 02h
    int 21h
    mov dl, 0Ah; LF
    mov ah, 02h
    int 21h
    mov ah, 4Ch
    int 21h

main endp
end main
