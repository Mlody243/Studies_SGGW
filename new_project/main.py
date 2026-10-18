class Logger:
    def __init__(self,log_path):
        self.log_path=log_path

    def __enter__(self):
        print('Start sekcji logowania')
        logging_message=f'Logi sa zapisywane w pliku {self.log_path}'
        return logging_message
    
    def __exit__(self, exc_type, exc, tb):
        print('Koniec sekcji logowania')

class FileWriter:
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = None

    def __enter__(self):
        self.file = open(self.filepath, 'w', encoding='utf-8')
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        if exc_type is not None:
            print(f'Błąd podczas zapisu: {exc_val}')
        return False

class SafeDivision:
    def __enter__(self):
        return self

    def divide(self, a, b):
        return a / b

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is ZeroDivisionError:
            print('Nie można dzielić przez zero')
            return True
        return False


if __name__=='__main__':
    with Logger('/path/logs') as log:
        print(log)

    # with FileWriter('przyklad.txt') as f:
    #     f.write('Linijka 1\n')
    #     wynik=1/0
    #     f.write('Linijka 2')

    with SafeDivision() as sd:
        wynik = sd.divide(10, 2)
        print(f'Wynik: {wynik}')

    with SafeDivision() as sd:
        sd.divide(5, 0)  # Tutaj wystąpi ZeroDivisionError, który zostanie stłumiony
    print('test if its working after error')