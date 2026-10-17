from prompt import string


def welcome():
    print("Первая попытка запустить проект!")
    print("\n***")
    
    while True:
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")
        
        command = string("Введите команду: ")
        
        if command == "exit":
            break
        elif command == "help":
            continue 
        else:
            print("Неизвестная команда. Попробуйте еще раз.")
