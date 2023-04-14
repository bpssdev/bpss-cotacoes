from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image  
from utils.file import get_rootpath
import os

from gui.view_action import ViewAction


class Application(Frame):

    BACKGROUND_TOP = "#2979FF"
    BACKGROUND_BOTTON = "#1c54b2"
    BACKGROUND_STATUS = "#093170"
    BACKGROUND_APPLICATION = "#66cfff"
    
    def __init__(self):
        self.__root = Tk()
        self.__root.geometry("800x600")
        Frame.__init__(self, self.__root)
        self.pack()
        self.action = ViewAction(self)
        self.initUI()
        self.pack()
        self.action.init()
        

    def start(self):
        self.__root.mainloop()


    def initUI(self):
        self.master.title("Bpss Cotações")
        self.pack(fill=BOTH, expand=True)
        self.configure(bg=self.BACKGROUND_APPLICATION)
        self.__root.iconbitmap(os.path.join(get_rootpath(), "assets", "icon.ico"))
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)

        data_referencia_value = StringVar(value="")
        data_ultima_atualizacao = StringVar(value="")
        status_value = StringVar(value="Parado")
        inicio_processamento_value = StringVar(value="")
        fim_processamento_value = StringVar(value="")

        logo_image = ImageTk.PhotoImage(Image.open(os.path.join(get_rootpath(), "assets", "logo.jpg")))
   
        application_frame = Frame(self, bg=self.BACKGROUND_TOP, padx=10, pady=10)
        application_frame.grid(row=0, sticky=(W, E), columnspan=3)

        img = Label(application_frame, image=logo_image, bg=self.BACKGROUND_TOP)
        img.image = logo_image
        img.grid(column=0, row=0)
        
        # status frame
        status_frame = Frame(self, bg=self.BACKGROUND_STATUS)
        status_frame.grid(
            sticky=(W, S, E, N), 
            row=1,
            columnspan=4
        )
        Label(status_frame, 
              text="Status: ", 
              bg=self.BACKGROUND_STATUS,
              fg="white"
            )\
            .grid(row=0, column=0, padx=10, sticky=E)

        Label(status_frame, 
                textvariable=status_value, 
                bg=self.BACKGROUND_STATUS,
                fg="white"
            )\
            .grid(row=0, column=4, sticky=E)

        # Divisor
        Frame(self).grid(row=2, pady=10)


        # main frame
        main_frame = Frame(self, bg=self.BACKGROUND_APPLICATION)
        main_frame.grid(sticky=(W, E, S, N), row=3, padx=10, columnspan=2)
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        info_frame = Frame(main_frame, bg=self.BACKGROUND_APPLICATION)
        info_frame.grid(row=0, padx=10, sticky=(W, E, S, N))

        Label(info_frame, 
            text="Data de referencia: ", 
            bg=self.BACKGROUND_APPLICATION
        )\
        .grid(sticky=W, row=0)

        Label(info_frame, 
            textvariable=data_referencia_value, 
            bg=self.BACKGROUND_APPLICATION
        )\
        .grid(sticky=W, row=0, column=1)


        Label(info_frame, 
            text="Data da ultima atualizacao: ", 
            bg=self.BACKGROUND_APPLICATION
        )\
        .grid(row=1)

        Label(info_frame, 
            textvariable=data_ultima_atualizacao, 
            bg=self.BACKGROUND_APPLICATION
        )\
        .grid(sticky=W, row=1, column=1)

        # Divisor
        Frame(info_frame).grid(row=2, pady=10)

        Label(info_frame, 
            text="Inicio do processamento: ",
            bg=self.BACKGROUND_APPLICATION
        )\
        .grid(sticky=W, row=3, column=0)

        Label(info_frame, 
            textvariable=inicio_processamento_value,
            bg=self.BACKGROUND_APPLICATION
        )\
        .grid(sticky=W, row=3, column=1)

        Label(info_frame, 
            text="Fim do processamento: ",
            bg=self.BACKGROUND_APPLICATION
        )\
        .grid(sticky=W, row=4, column=0)

        Label(info_frame, 
            textvariable=fim_processamento_value,
            bg=self.BACKGROUND_APPLICATION
        )\
        .grid(sticky=W, row=4, column=1)
        

        # Divisor
        Frame(main_frame).grid(row=1, pady=10)

        Label(main_frame, 
            text="Produtos: ", 
            bg=self.BACKGROUND_APPLICATION
        )\
        .grid(sticky=W, padx=10, row=2)

        cotacoes_frame = Frame(main_frame, 
            bg=self.BACKGROUND_APPLICATION                       
        )
        cotacoes_frame.grid(row=3, sticky=(W, E, S, N), columnspan=2)
        cotacoes_frame.grid_rowconfigure(0, weight=1)
        cotacoes_frame.grid_columnconfigure(0, weight=1)
        cotacoes_frame.grid_columnconfigure(1, weight=4)

        self.produtos_listbox = Listbox(cotacoes_frame)
        self.produtos_listbox.grid(
            sticky=(W, E, S, N), 
            padx=10, 
            row=0
        )
        self.produtos_listbox.bind('<<ListboxSelect>>', self.action.handle_select_produto)

        cotacoes_por_produto_treeview = ttk.Treeview(cotacoes_frame)
        cotacoes_por_produto_treeview["columns"] = ("Safra", "Mês", "DDE", "Vlr. Cotação")
        cotacoes_por_produto_treeview.grid(
            row=0,
            column=1, 
            padx=5, 
            sticky=(W, E, S, N)
        )
        cotacoes_por_produto_treeview.column("#0", width=0,  stretch=NO)
        cotacoes_por_produto_treeview.column("Safra",anchor=W, width=80, stretch=NO)
        cotacoes_por_produto_treeview.column("Mês",anchor=W, width=80, stretch=NO)
        cotacoes_por_produto_treeview.column("DDE", anchor=W, width=50)
        cotacoes_por_produto_treeview.column("Vlr. Cotação", anchor=E, width=100, stretch=NO)
        cotacoes_por_produto_treeview.heading("#0", text="", anchor=E)
        cotacoes_por_produto_treeview.heading("Safra", text="Safra", anchor=W)
        cotacoes_por_produto_treeview.heading("Mês", text="Mês", anchor=W)
        cotacoes_por_produto_treeview.heading("DDE", text="DDE", anchor=W)
        cotacoes_por_produto_treeview.heading("Vlr. Cotação", text="Vlr. Cotação", anchor=E)

        # Divisor
        Frame(self).grid(row=4, pady=10)

        # Botton frame
        bottom_frame = Frame(self, bg=self.BACKGROUND_BOTTON)
        bottom_frame.grid(sticky=(W, E, S, N), row=5, columnspan=3)

        self.start_button = Button(bottom_frame, 
            text="INICIAR", 
            bg="#4DB6AC", 
            command=self.action.handle_start
        )
        self.start_button.grid(row=0, padx=20, pady=10)
        

        self.stop_button = Button(bottom_frame, 
            text=" PARAR ", 
            bg="#E57373",
            command=self.action.handle_stop
        ).grid(row=0, column=1, padx=6, pady=10)

        self.values_dict = {
            'data_referencia': data_referencia_value,
            'data_ultima_atualizacao': data_ultima_atualizacao,
            'lista_produtos': self.produtos_listbox,
            'status': status_value,
            'cotacoes_por_produto_treeview': cotacoes_por_produto_treeview,
            'inicio_processamento': inicio_processamento_value,
            'fim_processamento': fim_processamento_value
        }


    def update(self, target, value, is_options=False):
        target_widget = self.values_dict[target]
        target_not_exists = target_widget is None
        if target_not_exists: 
            return
        if isinstance(target_widget, Listbox):
            if is_options:
                for v in value:
                    target_widget.insert(*v)
            else: 
                target_widget.selection_clear(0, END)
                if not value is None:
                    target_widget.select_set(value)
                
                
        if isinstance(target_widget, StringVar):
            target_widget.set(value)
        if isinstance(target_widget, ttk.Treeview):
            for i in target_widget.get_children():
                target_widget.delete(i)
            index = 0
            for v in value:
                index += 1
                target_widget.insert(
                    '', END, values=v
                )

    def getvalue(self, target):
        target_widget = self.values_dict[target]
        target_not_exists = target_widget is None
        if target_not_exists: 
            return ""
        if isinstance(target_widget, Listbox):
            return target_widget.get(target_widget.curselection())
        if isinstance(target_widget, StringVar):
            return target_widget.get()
        return ""

    def set_loading(self, is_loading=False):
        if is_loading:
            self.config(cursor="watch")
            self.start_button.config(state="disabled")
        else: 
            self.config(cursor="")
            self.start_button.config(state="normal")
