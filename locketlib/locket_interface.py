from locketlib import locket
import maskpass

class UserInterface:

    def __init__(self) -> None:
        self.client = None

    def login(self) -> None:
        email = input("Email: ")
        password = maskpass.askpass(prompt="Password: ", mask="*")
        try:
            self.client = locket.Locket(email, password)
            if self.client.is_logged_in():
                print("Logged in!")
            else:
                print("Wrong username or password!")

        except Exception as e:
            print(f"Error: {e}")

    
    def upload_image(self) -> None:
        filepath = input("Enter image file path: ")
        caption = input("Enter your caption: ")
        resp = self.client.post_image(filepath, caption)

        if resp[0] == True:
            print("Image uploaded!")
        else:
            print("Something went wrong, image was not uplaoded.")
            