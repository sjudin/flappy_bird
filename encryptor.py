from cryptography.fernet import Fernet

c_s = Fernet(b'NkUiwAxX9uGxILKru5nvTP1pe9eafOODuemmtcQbmJ8=')

pwd = input("Type your password!\n")
encrypted_pwd = c_s.encrypt(bytes(pwd, 'utf-8'))
print(encrypted_pwd)

