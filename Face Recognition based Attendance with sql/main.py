import tkinter as tk
# import systemcheck
import face_recogniser
import face_adder

class main_window(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        # self.attributes('-fullscreen',True)
        self.resizable(False, False)
        self.frames = {'Home': Home, 'AddFace': AddFace}
        self.show_page('Home')

    def show_page(self, page_name):
        self.frames[page_name](self).pack()


class Home(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, width=1200, height=650)

        self.parent = parent
        parent.title('Home')
        xref, yref = 150, 100

        addFaceB = tk.Button(self, text="Add Person", command=self.addFaceFun)
        addFaceB.config(font=("Times New Roman", 30), width=20, bg='lightgreen', cursor='hand2')
        addFaceB.place(x=xref + 200, y=yref + 100)

        TrackFacesB = tk.Button(self, text="Run System", command=self.trackFacesFun)
        TrackFacesB.config(font=("Times New Roman", 30), width=20, bg='lightgreen', cursor='hand2')
        TrackFacesB.place(x=xref + 200, y=yref + 300)

    def addFaceFun(self):
        self.pack_forget()
        self.parent.show_page("AddFace")

    def trackFacesFun(self):
        face_recogniser.track_faces()


class AddFace(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, width=1200, height=650)
        self.parent = parent
        parent.title("Add Face")
        xref, yref = 150, 100

        nameL = tk.Label(self, text="Name: ")
        nameL.config(font=("Times New Roman", 30), width=20, bg='lightgray')
        nameL.place(x=xref, y=yref)

        nameE = tk.Entry(self)
        nameE.config(font=("Times New Roman", 30), width=20, bg='lightgray')
        nameE.place(x=xref + 500, y=yref)

        imgCountL = tk.Label(self, text="Images Count: ")
        imgCountL.config(font=("Times New Roman", 30), width=20, bg='lightgray')
        imgCountL.place(x=xref, y=yref + 100)

        imgCountE = tk.Entry(self)
        imgCountE.config(font=("Times New Roman", 30), width=20, bg='lightgray')
        imgCountE.insert(0, 50)
        imgCountE.place(x=xref + 500, y=yref + 100)

        reWriteL = tk.Label(self, text="Rewrite?: ")
        reWriteL.config(font=("Times New Roman", 30), width=20, bg='lightgray')
        reWriteL.place(x=xref, y=yref + 200)

        self.reWriteVar = tk.BooleanVar(self, True)

        reWriteRB_T = tk.Radiobutton(self, text='Yes', variable=self.reWriteVar, value=True)
        reWriteRB_T.config(font=("Times New Roman", 30), bg='lightgray')
        reWriteRB_T.place(x=xref + 500, y=yref + 200)

        reWriteRB_F = tk.Radiobutton(self, text='No', variable=self.reWriteVar, value=False)
        reWriteRB_F.config(font=("Times New Roman", 30), bg='lightgray')
        reWriteRB_F.place(x=xref + 750, y=yref + 200)

        homeB = tk.Button(self, text="<-Home")
        homeB.config(font=("Times New Roman", 30), width=20, bg='lightgreen', command=self.homeFun)
        homeB.place(x=xref, y=yref + 320)

        submitB = tk.Button(self, text="Submit")
        submitB.config(font=("Times New Roman", 30), width=20, bg='lightgreen',
                       command=lambda: self.submitFun(nameE, imgCountE, self.reWriteVar))
        submitB.place(x=xref + 500, y=yref + 320)

        self.errorL = tk.Label(self)
        self.errorL.config(font=("Times New Roman", 30), fg='red')
        self.errorL.place(x=xref, y=yref + 450)

    def homeFun(self):
        self.pack_forget()
        self.parent.show_page("Home")

    def showError(self, msg):
        self.errorL.config(text=msg)

    def submitFun(self, nameE, imgCountE, reWriteVar):
        name = nameE.get()
        imgCount = imgCountE.get()
        reWrite = reWriteVar.get()
        try:
            imgCount = int(imgCount)
        except ValueError:
            self.showError("Images Count Must be an integer")
            return
        self.showError("Making Storage Folder")
        self.update()
        self.showError("Name added successfully")
        self.update()
        face_adder.add_face(label=name, req_count=imgCount, rewrite=reWrite)
        self.showError("Face Added")

        nameE.delete(0, tk.END)
        imgCountE.delete(0, tk.END)
        imgCountE.insert(0, '50')
        reWriteVar.set(True)


main_window()
tk.mainloop()
