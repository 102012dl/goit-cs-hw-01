    ```assembly
    section .data
        a db 5
        b db 10
        c db 3
        result db 0
    section .text
        global _start
    _start:
        ; Завантажуємо значення змінних у регістри
        mov al, [b]
        sub al, [c]
        add al, [a]
        
        ; Зберігаємо результат
        mov [result], al
        ; Завершуємо програму
        mov eax, 1
        int 0x80
