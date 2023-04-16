import tkinter as tk

class BCDDEPopupView:

    def __init__(self, root, action) -> None:
        self.root = root
        self.action = action

    def show(self):
        popup = tk.Toplevel(self.root)
        popup.geometry("230x180")
        popup.wm_title("Broadcast+ dde teste de comunicação")
        #popup.tkraise(self.root) # This just tells the message to be on top of the root window.

        application_entry_var = tk.StringVar(value="BC")
        topic_entry_var = tk.StringVar(value="Cot")
        parametro_entry_var = tk.StringVar(value="SMCF23*.ULT")


        tk.Label(popup, 
            text='Broadcast'
        )\
        .grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(
            master=popup,
            textvariable=application_entry_var
        )\
        .grid(row=0, column=1, padx=10, pady=10)

        tk.Label(popup, 
            text='Tópico'
        )\
        .grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(
            master=popup,
            textvariable=topic_entry_var
        )\
        .grid(row=1, column=1, padx=10, pady=10)

        tk.Label(popup, 
            text='Parametro'
        )\
        .grid(row=2, column=0, padx=10, pady=10)
        tk.Entry(
            master=popup,
            textvariable=parametro_entry_var
        )\
        .grid(row=2, column=1, padx=10, pady=10)

        tk.Button(popup, text="Testar comunicação", command=self.action.handle_test_broadcast_comunication)\
            .grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=10)


        self.values_dict = {
            'application': application_entry_var,
            'topic': topic_entry_var,
            'parametro': parametro_entry_var
        }


    def getvalue(self, target):
        target_widget = self.values_dict[target]
        target_not_exists = target_widget is None
        if target_not_exists: 
            return ""
        if isinstance(target_widget, tk.StringVar):
            return target_widget.get()
        return ""
