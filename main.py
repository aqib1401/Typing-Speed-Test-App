from gui import GUI


gui = GUI()


gui.entry.bind("<KeyRelease>", gui.on_key_release)
gui.entry.bind('<space>', gui.on_space_press)
gui.entry.bind('<BackSpace>', gui.on_backspace_press)
gui.restart_button.config(command=gui.restart)


gui.root.mainloop()



