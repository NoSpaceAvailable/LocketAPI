from locketlib import locket_interface

if __name__ == "__main__":
    interface = locket_interface.UserInterface()
    interface.login()
    interface.upload_image()